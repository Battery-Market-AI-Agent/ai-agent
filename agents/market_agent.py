"""
T1: 시장 환경 조사 Agent (RAG 기반)

# BaseAgent 상속
# Tool: RAG (FAISS 검색)
# Agentic RAG Loop:
#   1. 쿼리 생성 (배터리 시장 환경, 캐즘, HEV 피벗 등)
#   2. RAG 검색
#   3. Grader(LLM)로 관련성 판단 (relevant / not relevant)
#   4. not relevant → 쿼리 재작성 → 재검색 (max 2회, 로컬 변수로 관리)
#   5. 2회 실패 시 해당 항목 "[데이터 불충분]" 처리
# 결과를 state["market"]에 ResearchResult 형태로 저장
"""
from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from agents.base import BaseAgent
from state import ReportState


class MarketAgent(BaseAgent):
    """T1: 시장 환경 조사 — RAG(FAISS) 기반 Agentic RAG Loop."""

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool] | None = None):
        super().__init__(llm, tools)

    def run(self, state: ReportState) -> ReportState:
        # TODO: 구현
        # 1. 쿼리 생성 (배터리 시장 환경, 캐즘, HEV 피벗 등)
        # 2. RAG 검색
        # 3. Grader(LLM)로 관련성 판단 (relevant / not relevant)
        # 4. not relevant → 쿼리 재작성 → 재검색 (max 2회, 로컬 변수로 관리)
        # 5. 2회 실패 시 해당 항목 "[데이터 불충분]" 처리
        # 6. 결과를 state["market"]에 ResearchResult 형태로 저장
        ...
