"""
WebSearch 도구 모듈 (Tavily API)

- web_search(query, max_results): 단일 쿼리 Tavily 검색
- 최근 1년 이내 자료만 검색 (days=365, API 레벨 필터링)
- 결과를 raw dict 형태로 반환 (title, content, url, source, date)
"""
import os
import re
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
        search_depth="advanced",
    )

    if not query:
        return []

    try:
        raw = tool.invoke({"query": query})
        raw = raw.get("results", raw) if isinstance(raw, dict) else raw
        if not isinstance(raw, list):
            return []
    except Exception as e:
        print(f"  [Tavily 에러] {e}")
        return []

    results = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        url = r.get("url", "")
        date = r.get("published_date", "") or _extract_date_from_url(url)
        results.append({
            "title": r.get("title", ""),
            "content": r.get("content", ""),
            "url": url,
            "source": _extract_source(url),
            "date": date,
        })

    return results


def _extract_date_from_url(url: str) -> str:
    """URL 경로에서 날짜 패턴 추출."""
    m = re.search(r"/(20\d{2})/(\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    m = re.search(r"[/_](20\d{2})(\d{2})(\d{2})[/_\-.]", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    m = re.search(r"(?<!\d)(20\d{2})(?!\d)", url)
    if m:
        return m.group(1)

    return ""


def _extract_source(url: str) -> str:
    """URL에서 도메인명 추출."""
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""
