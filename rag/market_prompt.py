"""T1 Market Agent 프롬프트 및 RAG 쿼리 정의"""
from typing import Dict, List

# PDF 파일명(stem) → 출처 URL 매핑
SOURCE_URL_MAP: Dict[str, str] = {
    "GlobalEVOutlook2025": "https://www.iea.org/reports/global-ev-outlook-2025",
}

MARKET_RAG_QUERIES: List[Dict[str, str]] = [
    {
        "query": "global battery market size growth forecast 2024 2025 2026",
        "category": "글로벌 배터리 시장 현황",
    },
    {
        "query": "electric vehicle EV demand slowdown sales decline chasm 2024 2025",
        "category": "전기차 캐즘",
    },
    {
        "query": "hybrid HEV battery demand shift trend growth 2024 2025",
        "category": "HEV 전환 트렌드",
    },
    {
        "query": "battery energy storage stationary storage market growth demand 2024 2025",
        "category": "ESS 시장 성장",
    },
]

GRADER_SYSTEM_PROMPT: str = """당신은 배터리/에너지 도메인 문서의 관련성 평가자입니다.
주어진 쿼리와 검색 결과를 보고 관련성을 판단하세요.

판단 기준:
- relevant: 검색 결과에 쿼리와 관련된 내용이 조금이라도 언급된 경우
- not relevant: 검색 결과가 쿼리와 전혀 무관한 경우

반드시 'relevant' 또는 'not relevant' 중 하나만 응답하세요."""

QUERY_REWRITE_SYSTEM_PROMPT: str = """당신은 배터리/에너지 도메인 검색 전문가입니다.
주어진 쿼리로 관련 문서를 찾지 못했습니다. 더 구체적이고 다양한 키워드를 사용하여 쿼리를 재작성하세요.

재작성 원칙:
- 동의어, 영문 약어(EV, ESS, HEV, LFP, NMC 등) 추가
- 연도 범위 조정 (2023~2026)
- 더 넓거나 좁은 범위로 조정

재작성된 쿼리만 출력하세요. 설명 불필요."""

SUMMARY_SYSTEM_PROMPT: str = """당신은 배터리 시장 분석 전문가입니다.
아래 RAG 검색 결과를 바탕으로 보고서의 '시장 배경' 섹션(2장)에 들어갈 요약을 작성하세요.

작성 원칙:
- 검색 결과에 있는 내용만 사용 (hallucination 금지)
- 근거 없는 주장은 절대 포함하지 않음
- "검색 데이터 불충분"으로 표시된 항목은 추론하거나 보완하지 말고 반드시 "데이터 불충분"으로 명시
- 반드시 아래 4개 항목을 각각 하나의 문단으로 작성:
  1문단: 글로벌 배터리 시장 현황
  2문단: 전기차 캐즘
  3문단: HEV 전환 트렌드
  4문단: ESS 시장 성장
- 각 문단 첫 줄은 **[항목명]** 으로 시작
- 한국어로 작성"""
