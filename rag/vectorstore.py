"""
FAISS 벡터스토어 모듈

# FAISS 인덱스 생성
# 검색 함수 (쿼리 → top-k 문서 반환)
"""
from typing import Dict, List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


def create_vectorstore(
    documents: List[Document], embeddings: Embeddings
) -> FAISS:
    """문서 리스트와 임베딩 모델로 FAISS 인덱스를 생성한다."""
    return FAISS.from_documents(documents, embeddings)


def save_vectorstore(vectorstore: FAISS, path: str) -> None:
    """FAISS 인덱스를 로컬 경로에 저장한다."""
    vectorstore.save_local(path)


def load_vectorstore(path: str, embeddings: Embeddings) -> FAISS:
    """로컬 경로에서 FAISS 인덱스를 로드한다."""
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)


def search_vectorstore(
    vectorstore: FAISS, query: str, top_k: int = 5
) -> List[Dict]:
    """FAISS 인덱스에서 쿼리로 유사도 검색하여 top-k 문서를 반환한다."""
    return vectorstore.similarity_search(query, k=top_k)
