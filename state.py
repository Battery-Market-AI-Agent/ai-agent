from typing import TypedDict, List, Dict


class ResearchResult(TypedDict, total=False):
    """각 조사 Agent의 결과물"""
    raw: List[Dict]
    # raw 내부 dict 구조:
    # {
    #     "category": str,       # 6가지 항목 중 하나 (사업 포트폴리오, 기술 경쟁력, 재무 현황, 공급망/생산, 시장 지위, 리스크)
    #     "sentiment": str,      # "positive" 또는 "negative"
    #     "title": str,          # 기사/자료 제목
    #     "content": str,        # 조사 내용
    #     "source": str,         # 출처 기관명
    #     "url": str,            # URL
    #     "date": str            # YYYY-MM-DD
    # }
    summary: str


class SWOTResult(TypedDict, total=False):
    """Comparative SWOT 분석 결과"""
    table: str       # S/W/O/T × LG/CATL/전략적 시사점 테이블
    insights: str    # 종합 시사점


class ReportState(TypedDict, total=False):
    # Research Layer
    market: ResearchResult
    sko: ResearchResult
    catl: ResearchResult
    # Analysis Layer
    comparative_swot: SWOTResult
    # Report Layer
    final_report: str
