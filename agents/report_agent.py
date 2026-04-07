"""
T5: 최종 보고서 생성 Agent (LLM 생성)

# BaseAgent 상속
# Tool: 없음 (LLM 생성)
# 입력: state 전체 (raw 기반으로 작성 — 요약 손실 방지)
# 보고서 목차:
#   1. SUMMARY (반 페이지)
#   2. 시장 배경
#      2.1 글로벌 배터리 시장 현황
#      2.2 전기차 캐즘과 HEV 피벗
#   3. 기업별 전략 분석
#      3.1 SK on 포트폴리오 다각화
#      3.2 CATL 포트폴리오 다각화
#   4. 비교 분석
#      4.1 핵심 전략 비교
#      4.2 Comparative SWOT (state["comparative_swot"]["table"] 활용)
#   5. 종합 시사점 (state["comparative_swot"]["insights"] 활용)
#   6. REFERENCE (raw 내 source, url, date에서 추출, 형식 준수)
# REFERENCE 형식:
#   - 웹페이지: 기관명(YYYY-MM-DD). 제목. URL
# state["final_report"]에 저장
"""
from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from agents.base import BaseAgent
from state import ReportState


class ReportAgent(BaseAgent):
    """T5: 최종 보고서 생성 — state 전체를 기반으로 보고서 작성."""

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool] | None = None):
        super().__init__(llm, tools)

    def run(self, state: ReportState) -> ReportState:
        # TODO: 구현
        # 1. state 전체에서 raw 데이터 및 SWOT 결과 수집
        # 2. 보고서 목차에 맞춰 LLM으로 각 섹션 생성
        # 3. REFERENCE 섹션: raw 내 source, url, date로 출처 생성
        # 4. 토큰 총합 200,000 초과 시 완성된 섹션만 출력, 미완성은 "분석 미완료" 명시
        # 5. state["final_report"]에 최종 보고서 문자열 저장
        ...
