"""RAG 도구 모듈 — retrieve / grade / rewrite"""
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from rag.market_prompt import GRADER_SYSTEM_PROMPT, QUERY_REWRITE_SYSTEM_PROMPT


def rag_retrieve(query: str, vectorstore: FAISS, top_k: int = 5) -> List[Document]:
    """FAISS에서 유사도 검색하여 top-k 문서를 반환한다."""
    return vectorstore.similarity_search(query, k=top_k)


def grade_documents(llm: BaseChatModel, query: str, documents: List[Document]) -> str:
    """LLM으로 검색 결과 관련성을 일괄 판단한다. 반환: 'relevant' 또는 'not relevant'."""
    content = "\n\n---\n\n".join(d.page_content for d in documents)
    messages = [
        SystemMessage(content=GRADER_SYSTEM_PROMPT),
        HumanMessage(content=f"쿼리: {query}\n\n검색 결과:\n{content}"),
    ]
    response = llm.invoke(messages).content.strip().lower()
    return "relevant" if "not" not in response and "relevant" in response else "not relevant"


def rewrite_query(llm: BaseChatModel, original_query: str) -> str:
    """not relevant 판정 시 LLM으로 쿼리를 재작성한다."""
    messages = [
        SystemMessage(content=QUERY_REWRITE_SYSTEM_PROMPT),
        HumanMessage(content=f"원본 쿼리: {original_query}"),
    ]
    return llm.invoke(messages).content.strip()
