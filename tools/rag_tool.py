"""
RAG 도구 모듈

# RAG Retrieve: FAISS에서 유사도 검색
# Grader: LLM에게 검색 결과 관련성 판단 시키는 함수 (relevant / not relevant)
# 쿼리 재작성: not relevant 시 LLM으로 쿼리 리포뮬레이션
"""
from typing import Dict, List

from langchain_core.language_models import BaseChatModel


def rag_retrieve(query: str, vectorstore, top_k: int = 5) -> List[Dict]:
    """FAISS 벡터스토어에서 유사도 검색하여 top-k 문서 반환."""
    # TODO: 구현
    ...


def grade_document(llm: BaseChatModel, query: str, document: Dict) -> str:
    """LLM으로 검색 결과의 관련성을 판단한다. 반환값: 'relevant' 또는 'not relevant'."""
    # TODO: 구현
    ...


def rewrite_query(llm: BaseChatModel, original_query: str) -> str:
    """not relevant 판정 시 LLM으로 쿼리를 리포뮬레이션한다."""
    # TODO: 구현
    ...
