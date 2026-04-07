"""
T3: CATL 조사 Agent (WebSearch 기반)

# BaseAgent 상속
# sko_agent.py와 동일 구조, 회사명만 CATL로 변경
# T2와 병렬 실행됨
# 확증 편향 방지: 긍정 쿼리 + 부정 쿼리 병렬 검색
# 6가지 조사 항목: 사업 포트폴리오, 기술 경쟁력, 재무 현황, 공급망/생산, 시장 지위, 리스크
# 검색 실패 시 쿼리 변경 후 1회 재시도
# 결과를 state["catl"]에 저장
"""
from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from agents.base import BaseAgent
from state import ReportState


class CATLAgent(BaseAgent):
    """T3: CATL 조사 — WebSearch 확증 편향 방지 병렬 검색."""

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool] | None = None):
        super().__init__(llm, tools)

    def run(self, state: ReportState) -> ReportState:
        # TODO: 구현
        # 1. 6가지 조사 항목별 긍정/부정 쿼리 생성 (CATL 대상)
        # 2. WebSearch 도구로 병렬 검색
        # 3. 결과를 raw list[dict] 형태로 파싱
        # 4. 검색 실패 시 쿼리 변경 후 1회 재시도
        # 5. state["catl"]에 ResearchResult 형태로 저장
        ...
