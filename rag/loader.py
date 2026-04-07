from pathlib import Path
from typing import List

import pdfplumber
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_PAGES = 100


def load_pdfs(data_dir: str) -> List[Document]:
    """data_dir의 PDF 파일을 로드한다. 텍스트 추출 가능한 페이지 기준 100페이지 이내 제한."""
    docs = []
    total_pages = 0
    for pdf_path in sorted(Path(data_dir).glob("*.pdf")):
        if total_pages >= MAX_PAGES:
            break
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                if total_pages >= MAX_PAGES:
                    break
                text = page.extract_text() or ""
                if text.strip():
                    docs.append(Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path.stem,
                            "page": i + 1,
                            "date": "",
                        },
                    ))
                    total_pages += 1
    return docs


def chunk_documents(documents: List[Document]) -> List[Document]:
    """문서를 700 tokens, overlap 100으로 청킹한다."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )
    return splitter.split_documents(documents)
