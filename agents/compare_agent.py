"""T4: Comparative SWOT 분석 Agent (LLM 추론)"""
from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool

from agents.base import BaseAgent
from prompts.compare_prompt import COMPARE_SYSTEM_PROMPT, INSIGHTS_PROMPT, SWOT_TABLE_PROMPT
from state import ReportState, SWOTResult


class CompareAgent(BaseAgent):
    """T4: Comparative SWOT 분석 — LLM 추론."""

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool] | None = None):
        super().__init__(llm, tools)

    def run(self, state: ReportState) -> ReportState:
        sko_summary = self._get_summary(state, "sko")
        catl_summary = self._get_summary(state, "catl")

        table = self._generate_swot_table(sko_summary, catl_summary)
        insights = self._generate_insights(table)

        return {**state, "comparative_swot": SWOTResult(table=table, insights=insights)}

    def _get_summary(self, state: ReportState, key: str) -> str:
        """state에서 summary를 추출. 없으면 raw 데이터를 텍스트로 변환해 fallback."""
        result = state.get(key, {})
        if result.get("summary"):
            return result["summary"]

        # summary 없으면 raw에서 직접 조합
        raw = result.get("raw", [])
        if not raw:
            return f"[{key.upper()} 데이터 없음]"

        lines = []
        for item in raw:
            category = item.get("category", "")
            sentiment = item.get("sentiment", "")
            content = item.get("content", "")
            lines.append(f"[{category} / {sentiment}] {content}")
        return "\n".join(lines)

    def _generate_swot_table(self, sko_summary: str, catl_summary: str) -> str:
        """LLM으로 Comparative SWOT 테이블 생성."""
        messages = [
            SystemMessage(content=COMPARE_SYSTEM_PROMPT),
            HumanMessage(content=SWOT_TABLE_PROMPT.format(
                sko_summary=sko_summary,
                catl_summary=catl_summary,
            )),
        ]
        response = self.llm.invoke(messages)
        content = response.content.strip()
        # LLM이 ```markdown ... ``` 으로 감쌀 경우 코드 펜스 제거
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:]).strip()
        return content

    def _generate_insights(self, swot_table: str) -> str:
        """LLM으로 종합 시사점 생성."""
        messages = [
            SystemMessage(content=COMPARE_SYSTEM_PROMPT),
            HumanMessage(content=INSIGHTS_PROMPT.format(swot_table=swot_table)),
        ]
        response = self.llm.invoke(messages)
        return response.content.strip()
