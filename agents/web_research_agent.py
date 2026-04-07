"""
WebResearchAgent — 웹검색 기반 기업 조사 Agent

SKOAgent, CATLAgent가 상속.
생성자에서 company, state_key를 고정하면 동작한다.
"""
import json

from agents.base import BaseAgent
from state import ReportState

MAX_RETRIES = 3


class WebResearchAgent(BaseAgent):
    """웹검색 기반 기업 조사 Agent.

    SKOAgent, CATLAgent는 생성자에서 company, state_key만 고정하면 된다.
    """

    def __init__(self, llm, company: str, state_key: str, tools=None):
        super().__init__(llm, tools)
        self.company = company
        self.state_key = state_key

    def run(self, state: ReportState) -> ReportState:
        from prompts.research_prompt import (
            RESEARCH_CATEGORIES,
            RESEARCH_SUMMARY_PROMPT,
        )
        from tools.web_search_tool import web_search

        # Step 1: LLM이 12개 쿼리 생성 (6개 카테고리 × 긍정/부정)
        queries = self._generate_queries()

        raw_results = []

        # Step 2 & 3: 카테고리별 긍정/부정 쿼리 검색 + 평가 루프
        for category in RESEARCH_CATEGORIES:
            category_queries = queries.get(category, {})
            category_def = category  # 카테고리명 자체가 정의

            for sentiment in ("positive", "negative"):
                query = category_queries.get(sentiment, "")
                if not query:
                    continue

                retry = 0
                current_query = query

                while retry <= MAX_RETRIES:
                    print(f"  [{self.company}] {category}/{sentiment} | 시도 {retry+1} | 쿼리: {current_query}")
                    results = web_search(current_query)

                    if not results:
                        print(f"  [{self.company}] {category}/{sentiment} | 검색 결과 없음 → 재시도")
                        retry += 1
                        if retry <= MAX_RETRIES:
                            current_query = self._refine_query(
                                category, sentiment, current_query, "검색 결과 없음", retry
                            )
                        continue

                    grade = self._evaluate_results(
                        category, category_def, current_query, results
                    )
                    print(f"  [{self.company}] {category}/{sentiment} | 평가: {grade['grade']} | {grade['reason']}")

                    if grade["grade"] == "sufficient":
                        for r in results:
                            raw_results.append(
                                {
                                    **r,
                                    "category": category,
                                    "sentiment": sentiment,
                                }
                            )
                        break

                    retry += 1
                    if retry <= MAX_RETRIES:
                        current_query = self._refine_query(
                            category, sentiment, current_query, grade["reason"], retry
                        )
                        print(f"  [{self.company}] {category}/{sentiment} | 쿼리 재작성 → {current_query}")
                else:
                    # 최대 재시도 소진 — 데이터 불충분 마커 추가
                    print(f"  [{self.company}] {category}/{sentiment} | 재시도 소진 → 데이터 불충분 마커")
                    raw_results.append({
                        "category": category,
                        "sentiment": sentiment,
                        "title": "[데이터 불충분]",
                        "content": f"{MAX_RETRIES + 1}회 검색 후에도 {category} 관련 충분한 자료를 찾지 못했습니다.",
                        "url": "", "source": "", "date": "",
                    })

        # Step 4: summary 생성
        summary_response = self.llm.invoke(
            RESEARCH_SUMMARY_PROMPT.format(
                company=self.company,
                raw=json.dumps(raw_results, ensure_ascii=False, indent=2),
            )
        )

        # Step 5: state 저장
        state[self.state_key] = {
            "raw": raw_results,
            "summary": summary_response.content,
        }
        return state

    def _generate_queries(self) -> dict:
        """LLM으로 6개 카테고리 × 긍정/부정 = 12개 쿼리 생성."""
        from prompts.research_prompt import QUERY_GENERATION_PROMPT

        response = self.llm.invoke(
            QUERY_GENERATION_PROMPT.format(company=self.company)
        )
        return _parse_json(response.content)

    def _evaluate_results(
        self, category: str, category_def: str, query: str, results: list
    ) -> dict:
        """LLM으로 검색 결과 충분성 평가. 파싱 실패 시 insufficient 반환."""
        from prompts.research_prompt import RESULT_EVALUATOR_PROMPT

        response = self.llm.invoke(
            RESULT_EVALUATOR_PROMPT.format(
                company=self.company,
                category=category,
                category_definition=category_def,
                query=query,
                results=json.dumps(results, ensure_ascii=False, indent=2),
            )
        )
        try:
            return _parse_json(response.content)
        except ValueError:
            return {"grade": "insufficient", "reason": "평가 결과 파싱 실패"}

    def _refine_query(
        self, category: str, sentiment: str, original_query: str, reason: str, retry: int = 1
    ) -> str:
        """LLM으로 실패한 쿼리를 재작성. retry 횟수에 따라 방향을 코드에서 분기."""
        from prompts.research_prompt import QUERY_REFINEMENT_PROMPT

        if retry == 1:
            direction = "더 구체적인 세부 키워드로 변경 (연도, 수치, 사건명 등 추가)"
        elif retry == 2:
            direction = "영어 쿼리로 전환 (English keywords only, 반드시 회사명 포함)"
        else:
            direction = f"더 넓은 범위로 확장하되 반드시 {self.company} 포함 (경쟁사 비교, 업계 동향 관점)"

        response = self.llm.invoke(
            QUERY_REFINEMENT_PROMPT.format(
                company=self.company,
                category=category,
                sentiment=sentiment,
                original_query=original_query,
                reason=reason,
                refinement_direction=direction,
            )
        )
        return response.content.strip()


def _parse_json(content: str) -> dict:
    """LLM 응답에서 JSON 파싱. 마크다운 코드블록 제거 후 재시도."""
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {e}\n원문: {content}") from e
