"""
WebResearchAgent — 웹검색 기반 기업 조사 Agent

SKOAgent, CATLAgent가 상속.
생성자에서 company, state_key를 고정하면 동작한다.
"""
import json

from agents.base import BaseAgent
from state import ReportState

# S/O는 긍정, W/T는 부정 방향 키워드로 구성되므로 sentiment 고정
_SENTIMENT_MAP = {
    "S": "positive",
    "W": "negative",
    "O": "positive",
    "T": "negative",
}

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
            RESEARCH_SUMMARY_PROMPT,
            SWOT_CATEGORIES,
        )
        from tools.web_search_tool import web_search

        # Step 1: LLM이 16개 쿼리 생성
        queries = self._generate_queries()

        raw_results = []

        # Step 2 & 3: 쿼리별 검색 + 평가 루프
        for swot_item, lang_queries in queries.items():
            swot_def = SWOT_CATEGORIES.get(swot_item, "")
            sentiment = _SENTIMENT_MAP[swot_item]

            for lang in ("ko", "en"):
                for query in lang_queries.get(lang, []):
                    retry = 0
                    current_query = query

                    while retry <= MAX_RETRIES:
                        results = web_search(current_query)

                        if not results:
                            retry += 1
                            if retry <= MAX_RETRIES:
                                current_query = self._refine_query(
                                    swot_item, current_query, "검색 결과 없음"
                                )
                            continue

                        grade = self._evaluate_results(
                            swot_item, swot_def, current_query, results
                        )

                        if grade["grade"] == "sufficient":
                            for r in results:
                                raw_results.append(
                                    {
                                        **r,
                                        "category": swot_item,
                                        "sentiment": sentiment,
                                    }
                                )
                            break

                        retry += 1
                        if retry <= MAX_RETRIES:
                            current_query = self._refine_query(
                                swot_item, current_query, grade["reason"]
                            )

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
        """LLM으로 SWOT 4개 × 한/영 2개 = 16개 쿼리 생성."""
        from prompts.research_prompt import QUERY_GENERATION_PROMPT

        response = self.llm.invoke(
            QUERY_GENERATION_PROMPT.format(company=self.company)
        )
        return _parse_json(response.content)

    def _evaluate_results(
        self, swot_item: str, swot_def: str, query: str, results: list
    ) -> dict:
        """LLM으로 검색 결과 충분성 평가. 파싱 실패 시 insufficient 반환."""
        from prompts.research_prompt import RESULT_EVALUATOR_PROMPT

        response = self.llm.invoke(
            RESULT_EVALUATOR_PROMPT.format(
                company=self.company,
                swot_item=swot_item,
                swot_definition=swot_def,
                query=query,
                results=json.dumps(results, ensure_ascii=False, indent=2),
            )
        )
        try:
            return _parse_json(response.content)
        except ValueError:
            return {"grade": "insufficient", "reason": "평가 결과 파싱 실패"}

    def _refine_query(self, swot_item: str, original_query: str, reason: str) -> str:
        """LLM으로 실패한 쿼리를 재작성."""
        from prompts.research_prompt import QUERY_REFINEMENT_PROMPT

        response = self.llm.invoke(
            QUERY_REFINEMENT_PROMPT.format(
                company=self.company,
                swot_item=swot_item,
                original_query=original_query,
                reason=reason,
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
