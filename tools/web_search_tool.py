"""
WebSearch 도구 모듈 (Tavily API)

- web_search(query, max_results): 단일 쿼리 Tavily 검색
- 최근 1년 이내 자료만 검색 (days=365, API 레벨 필터링)
- 결과를 raw dict 형태로 반환 (title, content, url, source, date)

TODO: 최종 보고서 품질 검토 후 raw_content 전환 여부 결정
  - 현재: include_raw_content=False (snippet, ~500자/건)
  - 전환 시: TavilyClient + include_raw_content=True, max_results=2~3으로 축소
  - 전환 시 중간 요약 레이어 추가 필요 (결과 1건씩 개별 요약 후 합산)
"""
import os
from typing import Dict, List
from urllib.parse import urlparse

from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

# 최근 1년 이내 자료만 검색 (API 레벨 필터링)
_SEARCH_DAYS = 365


def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """Tavily API로 단일 쿼리 웹 검색.

    Args:
        query: 검색 쿼리 문자열
        max_results: 반환할 최대 결과 수 (기본값 5)

    Returns:
        raw dict 리스트. 각 dict: {title, content, url, source, date}
        검색 실패 또는 예외 발생 시 빈 리스트 반환.
    """
    tool = TavilySearch(
        max_results=max_results,
        include_raw_content=False,
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        days=_SEARCH_DAYS,
    )

    try:
        raw = tool.invoke({"query": query})
        raw = raw.get("results", raw) if isinstance(raw, dict) else raw
    except Exception:
        return []

    results = []
    for r in raw:
        url = r.get("url", "")
        results.append({
            "title": r.get("title", ""),
            "content": r.get("content", ""),
            "url": url,
            "source": _extract_source(url),
            # TODO: Tavily가 published_date를 반환하지 않아 항상 빈 문자열
            # → raw_content 전환 시 본문에서 날짜 추출 가능 (Reference 섹션 품질 개선)
            "date": r.get("published_date", ""),
        })

    return results


def _extract_source(url: str) -> str:
    """URL에서 도메인명 추출.

    예) "https://www.hankyung.com/..." → "hankyung.com"
    """
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""
