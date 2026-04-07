"""T5: 최종 보고서 생성 프롬프트"""

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
#      4.2 Comparative SWOT
#   5. 종합 시사점
#   6. REFERENCE
# REFERENCE 형식: 기관명(YYYY-MM-DD). 제목. URL

REPORT_SYSTEM_PROMPT: str = ""
# TODO: 보고서 생성용 시스템 프롬프트 작성

REPORT_SECTION_PROMPT: str = ""
# TODO: 각 섹션별 생성 프롬프트 작성

REFERENCE_FORMAT_PROMPT: str = ""
# TODO: REFERENCE 섹션 포맷팅 프롬프트 작성
