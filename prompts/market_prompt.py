"""T1: 시장 환경 조사 프롬프트"""

# 배터리 시장 환경 분석을 위한 RAG 쿼리 및 LLM 프롬프트 정의
# - 글로벌 배터리 시장 현황
# - 전기차 캐즘(Chasm)
# - HEV 피벗 트렌드
# - ESS 시장 성장

MARKET_SYSTEM_PROMPT: str = ""
# TODO: 시장 환경 조사용 시스템 프롬프트 작성

MARKET_RAG_QUERIES: list[str] = []
# TODO: RAG 검색에 사용할 쿼리 목록 정의

GRADER_PROMPT: str = ""
# TODO: 검색 결과 관련성 판단(Grader)용 프롬프트 작성

QUERY_REWRITE_PROMPT: str = ""
# TODO: 쿼리 재작성(리포뮬레이션)용 프롬프트 작성
