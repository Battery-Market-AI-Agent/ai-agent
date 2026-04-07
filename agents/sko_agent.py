"""
T2: SK on 조사 Agent (WebSearch 기반)

# BaseAgent 상속
# Tool: WebSearch
# 확증 편향 방지: 긍정 쿼리 + 부정 쿼리 병렬 검색
#   - 긍정: "SK on ESS 성장 전략 포트폴리오 다각화 2025 2026"
#   - 부정: "SK on 실적 부진 리스크 가동률 하락 약점 2025 2026"
# 6가지 조사 항목: 사업 포트폴리오, 기술 경쟁력, 재무 현황, 공급망/생산, 시장 지위, 리스크
# 각 결과를 raw list[dict] 형태로 저장 (category, sentiment, title, content, source, url, date)
# 검색 실패 시 쿼리 변경 후 1회 재시도
# 결과를 state["sko"]에 저장
"""
from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from agents.base import BaseAgent
from state import ReportState


class SKOAgent(BaseAgent):
    """T2: SK on 조사 — WebSearch 확증 편향 방지 병렬 검색."""

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool] | None = None):
        super().__init__(llm, tools)

    def run(self, state: ReportState) -> ReportState:
        # TODO: 구현
        # 1. 6가지 조사 항목별 긍정/부정 쿼리 생성
        # 2. WebSearch 도구로 병렬 검색
        # 3. 결과를 raw list[dict] 형태로 파싱
        # 4. 검색 실패 시 쿼리 변경 후 1회 재시도
        # 5. state["sko"]에 ResearchResult 형태로 저장
        ...
