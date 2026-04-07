"""
임베딩 모듈

# 임베딩 모델: BGE-M3 (BAAI/bge-m3, 오픈소스, 한중영 다국어)
# HuggingFace에서 로드
"""
from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings() -> HuggingFaceEmbeddings:
    """BGE-M3 다국어 임베딩 모델을 로드하여 반환한다."""
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
