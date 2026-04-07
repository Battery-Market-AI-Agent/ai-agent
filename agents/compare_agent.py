"""
T4: Comparative SWOT 분석 Agent (LLM 추론)

# BaseAgent 상속
# Tool: 없음 (LLM 추론만)
# 입력: state["sko"]["summary"] + state["catl"]["summary"] (필요시 raw 참조)
# Comparative SWOT 테이블 생성:
#   | 구분 | SK on | CATL | 전략적 시사점 |
#   | S - 내부 경쟁력 | ... | ... | ... |
#   | W - 내부 취약점 | ... | ... | ... |
#   | O - 외부 기회   | ... | ... | ... |
#   | T - 외부 리스크 | ... | ... | ... |
# 결과를 state["comparative_swot"]에 SWOTResult(table, insights)로 저장
"""
from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from agents.base import BaseAgent
from state import ReportState


class CompareAgent(BaseAgent):
    """T4: Comparative SWOT 분석 — LLM 추론."""

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool] | None = None):
        super().__init__(llm, tools)

    def run(self, state: ReportState) -> ReportState:
        # TODO: 구현
        # 1. state["sko"], state["catl"]에서 summary 및 raw 데이터 수집
        # 2. LLM에게 Comparative SWOT 테이블 생성 요청
        # 3. table + insights 파싱
        # 4. state["comparative_swot"]에 SWOTResult 형태로 저장
        ...
