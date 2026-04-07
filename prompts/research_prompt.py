"""T2, T3 공통: 기업 조사 프롬프트 (회사명만 변수)"""

# 6가지 조사 항목:
#   1. 사업 포트폴리오
#   2. 기술 경쟁력
#   3. 재무 현황
#   4. 공급망/생산
#   5. 시장 지위
#   6. 리스크
# 확증 편향 방지를 위해 긍정/부정 쿼리 템플릿 분리

RESEARCH_SYSTEM_PROMPT: str = ""
# TODO: 기업 조사용 시스템 프롬프트 작성 (회사명은 {company} 변수)

POSITIVE_QUERY_TEMPLATE: str = ""
# TODO: 긍정 검색 쿼리 템플릿 (e.g. "{company} ESS 성장 전략 포트폴리오 다각화 2025 2026")

NEGATIVE_QUERY_TEMPLATE: str = ""
# TODO: 부정 검색 쿼리 템플릿 (e.g. "{company} 실적 부진 리스크 가동률 하락 약점 2025 2026")

RESEARCH_CATEGORIES: list[str] = [
    "사업 포트폴리오",
    "기술 경쟁력",
    "재무 현황",
    "공급망/생산",
    "시장 지위",
    "리스크",
]
