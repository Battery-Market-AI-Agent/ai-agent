"""
LangGraph 그래프 정의

START → [T1, T2, T3]  (fan-out, 전부 병렬)
         T2, T3 → T4  (fan-in, Compare는 sko+catl만)
         T1, T4 → T5  (fan-in, Report는 전체 사용)
         T5 → END
"""
import time
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, START, END

from state import ReportState
from agents.market_agent import MarketAgent
from agents.sko_agent import SKOAgent
from agents.catl_agent import CATLAgent
from agents.compare_agent import CompareAgent
from agents.report_agent import ReportAgent

AGENT_LABELS = {
    "market": "T1 시장조사(RAG)",
    "sko": "T2 SK on(WebSearch)",
    "catl": "T3 CATL(WebSearch)",
    "compare": "T4 비교분석(SWOT)",
    "report": "T5 보고서생성",
}


def _make_node(name: str, agent_run, output_keys: List[str]):
    """Agent.run()을 래핑하여 로깅 + 변경된 키만 반환하는 노드 함수를 만든다."""
    label = AGENT_LABELS.get(name, name)

    def node_fn(state: ReportState) -> dict:
        print(f"  [{label}] 시작...")
        start = time.time()
        result = agent_run(state)
        elapsed = time.time() - start
        print(f"  [{label}] 완료 ({elapsed:.1f}초)")
        return {k: result[k] for k in output_keys if k in result}
    return node_fn


def build_graph(
    llm: BaseChatModel,
    vectorstore: FAISS,
    output_dir: str = "outputs",
):
    """Multi-Agent 그래프를 구성하고 컴파일된 그래프를 반환한다."""

    # 1. Agent 인스턴스 생성
    market_agent = MarketAgent(llm=llm, vectorstore=vectorstore)
    sko_agent = SKOAgent(llm=llm)
    catl_agent = CATLAgent(llm=llm)
    compare_agent = CompareAgent(llm=llm)
    report_agent = ReportAgent(llm=llm, output_dir=output_dir)

    # 2. StateGraph 생성
    graph = StateGraph(ReportState)

    # 3. 노드 추가 (로깅 + 담당 키만 반환)
    graph.add_node("market", _make_node("market", market_agent.run, ["market"]))
    graph.add_node("sko", _make_node("sko", sko_agent.run, ["sko"]))
    graph.add_node("catl", _make_node("catl", catl_agent.run, ["catl"]))
    graph.add_node("compare", _make_node("compare", compare_agent.run, ["comparative_swot"]))
    graph.add_node("report", _make_node("report", report_agent.run, ["final_report", "chart_paths"]))

    # 4. 엣지 연결
    # START → T1, T2, T3 (fan-out, 전부 병렬)
    graph.add_edge(START, "market")
    graph.add_edge(START, "sko")
    graph.add_edge(START, "catl")

    # T2, T3 → T4 (fan-in, Compare는 sko+catl만 사용)
    graph.add_edge("sko", "compare")
    graph.add_edge("catl", "compare")

    # T1, T4 → T5 (fan-in, Report는 market+compare 결과 모두 사용)
    graph.add_edge("market", "report")
    graph.add_edge("compare", "report")

    # T5 → END
    graph.add_edge("report", END)

    # 5. 컴파일
    return graph.compile()
