"""
1회성 인덱스 빌드 스크립트.
실행: python -m rag.build_index
"""
from pathlib import Path

from rag.embedder import get_embeddings
from rag.loader import chunk_documents, load_pdfs
from rag.vectorstore import create_vectorstore, save_vectorstore

DATA_DIR = Path(__file__).parent / "data"
INDEX_DIR = Path(__file__).parent / "faiss_index"


def build_index() -> None:
    print(f"[1/4] PDF 로드 중... ({DATA_DIR})")
    docs = load_pdfs(str(DATA_DIR))
    if not docs:
        raise FileNotFoundError(f"{DATA_DIR} 에 텍스트를 추출할 수 있는 PDF 파일이 없습니다.")
    print(f"  → {len(docs)} 페이지 로드 완료")

    print("[2/4] 청킹 중...")
    chunks = chunk_documents(docs)
    print(f"  → {len(chunks)} 청크 생성 완료")

    print("[3/4] BGE-M3 임베딩 로드 중... (최초 실행 시 모델 다운로드)")
    embeddings = get_embeddings()

    print("[4/4] FAISS 인덱스 생성 및 저장 중...")
    vectorstore = create_vectorstore(chunks, embeddings)
    INDEX_DIR.mkdir(exist_ok=True)
    save_vectorstore(vectorstore, str(INDEX_DIR))
    print(f"  → 인덱스 저장 완료: {INDEX_DIR}")


if __name__ == "__main__":
    build_index()
