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
import re
from typing import Dict, List
from urllib.parse import urlparse

import httpx
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
    except Exception:
        return []

    results = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        url = r.get("url", "")
        date = (
            r.get("published_date", "")
            or _extract_date_from_url(url)
            or _fetch_date_from_meta(url)
        )
        results.append({
            "title": r.get("title", ""),
            "content": r.get("content", ""),
            "url": url,
            "source": _extract_source(url),
            "date": date,
        })

    return results


def _fetch_date_from_meta(url: str) -> str:
    """URL의 HTML 메타태그에서 발행일 추출.

    PDF는 건너뜀. 앞 4KB만 스트리밍으로 가져와 article:published_time 등 파싱.
    실패 시 빈 문자열 반환.
    """
    if not url or url.lower().endswith(".pdf"):
        return ""

    _META_PATTERNS = re.compile(
        r'(?:article:published_time|datePublished|pubdate|article:modified_time)'
        r'[^>]*content=["\']([^"\']+)',
        re.IGNORECASE,
    )

    try:
        with httpx.Client(timeout=5, follow_redirects=True) as client:
            with client.stream("GET", url, headers={"Range": "bytes=0-4096"}) as resp:
                chunk = b""
                for data in resp.iter_bytes(chunk_size=4096):
                    chunk += data
                    break  # 첫 청크만
        html = chunk.decode("utf-8", errors="ignore")
        m = _META_PATTERNS.search(html)
        if m:
            return m.group(1)[:10]  # YYYY-MM-DD
    except Exception:
        pass

    return ""


def _extract_date_from_url(url: str) -> str:
    """URL 경로에서 날짜 패턴 추출.

    지원 패턴 (우선순위 순):
      /2025/10/31/  → 2025-10-31  (전체 날짜, 웹페이지용)
      /20251031     → 2025-10-31  (전체 날짜, 웹페이지용)
      /2025/        → 2025        (연도만, 기관 보고서·PDF용)
    추출 실패 시 빈 문자열 반환.
    """
    # 패턴 1: /2025/10/31/
    m = re.search(r"/(20\d{2})/(\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 패턴 2: /20251031 or _20251031
    m = re.search(r"[/_](20\d{2})(\d{2})(\d{2})[/_\-.]", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 패턴 3: 연도만 (앞뒤로 숫자가 없는 경우만 - idxno=20467 같은 ID 오매칭 방지)
    m = re.search(r"(?<!\d)(20\d{2})(?!\d)", url)
    if m:
        return m.group(1)

    return ""


def _extract_source(url: str) -> str:
    """URL에서 도메인명 추출.

    예) "https://www.hankyung.com/..." → "hankyung.com"
    """
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""
