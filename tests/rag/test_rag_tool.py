from unittest.mock import MagicMock

from langchain_core.documents import Document
from tools.rag_tool import grade_documents, rag_retrieve, rewrite_query


def _mock_llm(response_text: str):
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content=response_text)
    return llm


def test_rag_retrieve_calls_search():
    mock_vs = MagicMock()
    mock_vs.similarity_search.return_value = [
        Document(page_content="배터리 시장 현황", metadata={"source": "test"})
    ]
    results = rag_retrieve("배터리 시장", mock_vs, top_k=3)
    assert len(results) == 1
    mock_vs.similarity_search.assert_called_once_with("배터리 시장", k=3)


def test_grade_documents_returns_relevant():
    llm = _mock_llm("relevant")
    docs = [Document(page_content="글로벌 배터리 시장 성장률 25%", metadata={})]
    result = grade_documents(llm, "배터리 시장 성장률", docs)
    assert result == "relevant"


def test_grade_documents_returns_not_relevant():
    llm = _mock_llm("not relevant")
    docs = [Document(page_content="오늘 날씨가 맑습니다", metadata={})]
    result = grade_documents(llm, "배터리 시장 성장률", docs)
    assert result == "not relevant"


def test_rewrite_query_returns_new_query():
    llm = _mock_llm("글로벌 리튬이온 배터리 시장 규모 2025 성장 전망")
    result = rewrite_query(llm, "배터리 시장")
    assert result == "글로벌 리튬이온 배터리 시장 규모 2025 성장 전망"
    llm.invoke.assert_called_once()
