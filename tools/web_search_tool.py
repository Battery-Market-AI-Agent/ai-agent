"""
WebSearch 도구 모듈

# WebSearch 실행 함수
# 확증 편향 방지: 긍정 쿼리 + 부정 쿼리를 받아서 각각 검색
# 결과를 raw dict 형태로 반환
# 2025년 이후 자료만 필터링
"""
from typing import Dict, List


def web_search(query: str) -> List[Dict]:
    """단일 쿼리로 웹 검색을 수행하고 결과를 raw dict 리스트로 반환한다.
    2025년 이후 자료만 필터링한다."""
    # TODO: 구현
    ...


def web_search_dual(
    positive_query: str, negative_query: str
) -> Dict[str, List[Dict]]:
    """확증 편향 방지를 위해 긍정/부정 쿼리를 각각 검색한다.
    반환: {"positive": [...], "negative": [...]}"""
    # TODO: 구현
    ...
