from unittest.mock import MagicMock

from langchain_core.documents import Document
from state import ReportState


def _make_mock_llm(grade_response: str = "relevant"):
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content=grade_response)
    return llm


def _make_mock_vectorstore():
    vs = MagicMock()
    vs.similarity_search.return_value = [
        Document(
            page_content="글로벌 배터리 시장은 2025년 기준 1500억 달러 규모.",
            metadata={"source": "battery_report", "page": 1, "date": "2025-01-01"},
        )
    ]
    return vs


def test_market_agent_run_returns_market_state():
    from agents.market_agent import MarketAgent

    agent = MarketAgent(llm=_make_mock_llm(), vectorstore=_make_mock_vectorstore())
    result = agent.run({})

    assert "market" in result
    assert "raw" in result["market"]
    assert "summary" in result["market"]
    assert len(result["market"]["raw"]) == 4  # 쿼리 4개


def test_market_agent_raw_has_required_fields():
    from agents.market_agent import MarketAgent

    agent = MarketAgent(llm=_make_mock_llm(), vectorstore=_make_mock_vectorstore())
    result = agent.run({})

    for item in result["market"]["raw"]:
        assert "category" in item
        assert "content" in item
        assert "source" in item


def test_market_agent_fallback_on_max_retry():
    from agents.market_agent import MarketAgent

    # LLM이 항상 not relevant 반환
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content="not relevant")

    vs = MagicMock()
    vs.similarity_search.return_value = [
        Document(page_content="관련없는 내용", metadata={"source": "x", "page": 1, "date": ""})
    ]

    agent = MarketAgent(llm=llm, vectorstore=vs)
    result = agent.run({})

    for item in result["market"]["raw"]:
        assert item["content"] == "검색 데이터 불충분"


def test_market_agent_preserves_existing_state():
    from agents.market_agent import MarketAgent

    initial_state: ReportState = {"final_report": "기존 데이터"}
    agent = MarketAgent(llm=_make_mock_llm(), vectorstore=_make_mock_vectorstore())
    result = agent.run(initial_state)

    assert result["final_report"] == "기존 데이터"
    assert "market" in result
