from unittest.mock import MagicMock, patch, ANY

from langchain_core.documents import Document
from rag.vectorstore import create_vectorstore, save_vectorstore, load_vectorstore, search_vectorstore


def _make_fake_embeddings():
    embeddings = MagicMock()
    embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]] * 3
    embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    return embeddings


def test_create_vectorstore():
    docs = [
        Document(page_content="배터리 시장 성장", metadata={"source": "test"}),
        Document(page_content="전기차 캐즘 분석", metadata={"source": "test"}),
        Document(page_content="ESS 에너지 저장", metadata={"source": "test"}),
    ]
    with patch("rag.vectorstore.FAISS") as mock_faiss:
        mock_faiss.from_documents.return_value = MagicMock()
        vs = create_vectorstore(docs, _make_fake_embeddings())
        assert vs is not None
        mock_faiss.from_documents.assert_called_once()


def test_save_and_load_vectorstore():
    with patch("rag.vectorstore.FAISS") as mock_faiss:
        mock_vs = MagicMock()
        save_vectorstore(mock_vs, "/tmp/test_index")
        mock_vs.save_local.assert_called_once_with("/tmp/test_index")

        mock_faiss.load_local.return_value = MagicMock()
        vs = load_vectorstore("/tmp/test_index", _make_fake_embeddings())
        assert vs is not None
        mock_faiss.load_local.assert_called_once_with(
            "/tmp/test_index", ANY, allow_dangerous_deserialization=True
        )


def test_search_vectorstore():
    mock_vs = MagicMock()
    mock_vs.similarity_search.return_value = [
        Document(page_content="검색 결과", metadata={"source": "test"})
    ]
    results = search_vectorstore(mock_vs, "배터리 시장", top_k=3)
    assert len(results) == 1
    mock_vs.similarity_search.assert_called_once_with("배터리 시장", k=3)
