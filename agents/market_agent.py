"""T1: 시장 환경 조사 Agent — LangGraph 서브그래프 기반 Agentic RAG"""
from typing import List, Optional

from langchain_community.callbacks import get_openai_callback
from langchain_community.vectorstores import FAISS
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from agents.base import BaseAgent
from prompts.market_prompt import MARKET_RAG_QUERIES, SOURCE_URL_MAP, SUMMARY_SYSTEM_PROMPT
from tools.rag_tool import grade_documents, rag_retrieve, rewrite_query
from state import ReportState, ResearchResult

MAX_RETRIES = 3
TOKEN_LIMIT = 30_000


class RagLoopState(TypedDict):
    query: str
    category: str
    documents: list        # List[Document]
    grade: str             # "relevant" | "not relevant" | ""
    retry_count: int       # 재시도 횟수 (max 3)
    result: dict           # 최종 raw dict


def _build_rag_graph(llm: BaseChatModel, vectorstore: FAISS):
    """쿼리 1개를 처리하는 LangGraph 서브그래프를 빌드하여 반환한다."""

    def retrieve(state: RagLoopState) -> dict:
        docs = rag_retrieve(state["query"], vectorstore)
        return {"documents": docs}

    def grade(state: RagLoopState) -> dict:
        result = grade_documents(llm, state["query"], state["documents"])
        return {"grade": result}

    def rewrite(state: RagLoopState) -> dict:
        new_query = rewrite_query(llm, state["query"])
        return {"query": new_query, "retry_count": state["retry_count"] + 1}

    def finalize(state: RagLoopState) -> dict:
        if state["grade"] != "relevant":
            result = {
                "category": state["category"],
                "sentiment": "",
                "title": "",
                "content": "검색 데이터 불충분",
                "source": "",
                "url": "",
                "date": "",
            }
        else:
            docs = state["documents"]
            content = "\n\n".join(d.page_content for d in docs)
            first_meta = docs[0].metadata if docs else {}
            source = first_meta.get("source", "")
            result = {
                "category": state["category"],
                "sentiment": "",
                "title": f"{source} p.{first_meta.get('page', '')}",
                "content": content,
                "source": source,
                "url": SOURCE_URL_MAP.get(source, ""),
                "date": first_meta.get("date", ""),
            }
        return {"result": result}

    def route_after_grade(state: RagLoopState) -> str:
        if state["grade"] == "relevant":
            return "finalize"
        if state["retry_count"] < MAX_RETRIES:
            return "rewrite"
        return "finalize"

    graph = StateGraph(RagLoopState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("grade", grade)
    graph.add_node("rewrite", rewrite)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", route_after_grade, {
        "finalize": "finalize",
        "rewrite": "rewrite",
    })
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("finalize", END)

    return graph.compile()


class MarketAgent(BaseAgent):
    """T1: 시장 환경 조사 — LangGraph Agentic RAG Loop (max 3회 재시도)."""

    def __init__(
        self,
        llm: BaseChatModel,
        vectorstore: FAISS,
        tools: Optional[List[BaseTool]] = None,
    ):
        super().__init__(llm, tools)
        self.vectorstore = vectorstore
        self._rag_graph = _build_rag_graph(self.llm, vectorstore)

    def run(self, state: ReportState) -> ReportState:
        raw = []
        total_tokens = 0

        for item in MARKET_RAG_QUERIES:
            if total_tokens >= TOKEN_LIMIT:
                raw.append({
                    "category": item["category"],
                    "sentiment": "",
                    "title": "",
                    "content": "[분석 미완료]",
                    "source": "",
                    "url": "",
                    "date": "",
                })
                continue

            with get_openai_callback() as cb:
                loop_result = self._rag_graph.invoke({
                    "query": item["query"],
                    "category": item["category"],
                    "documents": [],
                    "grade": "",
                    "retry_count": 0,
                    "result": {},
                })
            total_tokens += cb.total_tokens
            raw.append(loop_result["result"])

        summary = self._generate_summary(raw, total_tokens)
        market: ResearchResult = {"raw": raw, "summary": summary}
        return {**state, "market": market}

    def _generate_summary(self, raw: list, used_tokens: int) -> str:
        if not raw:
            return "데이터 불충분 — 시장 배경 섹션 작성 불가"
        if used_tokens >= TOKEN_LIMIT:
            return "[분석 미완료] 토큰 한도(200K) 초과로 요약을 생성할 수 없습니다."
        content = "\n\n".join(
            f"[{r['category']}]\n{r['content']}" for r in raw
        )
        with get_openai_callback() as cb:
            result = self.llm.invoke([
                SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
                HumanMessage(content=content),
            ]).content
        total_after = used_tokens + cb.total_tokens
        if total_after > TOKEN_LIMIT:
            return "[분석 미완료] 토큰 한도(200K) 초과로 요약이 불완전할 수 있습니다.\n\n" + result
        return result
