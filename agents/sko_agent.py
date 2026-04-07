"""
T2: SK on 조사 Agent (WebSearch 기반)

WebResearchAgent 상속.
생성자에서 company="SK on", state_key="sko" 고정.
"""
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from agents.web_research_agent import WebResearchAgent


class SKOAgent(WebResearchAgent):
    """T2: SK on 조사 — LLM 쿼리 생성 + Tavily 검색 + 평가 루프."""

    def __init__(self, llm: BaseChatModel, tools: list[BaseTool] | None = None):
        super().__init__(llm, company="SK on", state_key="sko", tools=tools)
