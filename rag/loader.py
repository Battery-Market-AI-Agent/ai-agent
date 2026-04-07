"""
PDF 로더 및 청킹 모듈

# PDF 로드 (PyPDF, PDFPlumber 등)
# 청킹: 500~800 tokens, overlap 100
# 총 100페이지 이내 제한
"""
from typing import List

from langchain_core.documents import Document


def load_pdfs(data_dir: str) -> List[Document]:
    """data/ 디렉토리에서 PDF 파일을 로드한다. 총 100페이지 이내 제한."""
    # TODO: 구현
    ...


def chunk_documents(documents: List[Document]) -> List[Document]:
    """문서를 500~800 tokens, overlap 100으로 청킹한다."""
    # TODO: 구현
    ...
