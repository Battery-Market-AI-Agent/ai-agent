"""
임베딩 모듈

# 임베딩 모델: BGE-base-en-v1.5 (BAAI, 영문 특화)
# HuggingFace에서 로드
"""
from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings() -> HuggingFaceEmbeddings:
    """BGE-base-en-v1.5 영문 임베딩 모델을 로드하여 반환한다."""
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
