"""T5: 최종 보고서 생성 Agent (LLM 생성)"""
import json
import os
from typing import Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool

from agents.base import BaseAgent
from prompts.report_prompt import (
    CHART_DATA_EXTRACTION_PROMPT,
    REFERENCE_FORMAT_PROMPT,
    REPORT_SECTION_PROMPT,
    REPORT_SUMMARY_PROMPT,
    REPORT_SYSTEM_PROMPT,
)
from state import ReportState


class ReportAgent(BaseAgent):
    """T5: 최종 보고서 생성 — state 전체를 기반으로 보고서 작성."""

    MAX_TOKENS = 200_000

    def __init__(
        self,
        llm: BaseChatModel,
        tools: List[BaseTool] | None = None,
        output_dir: str = "outputs",
    ):
        super().__init__(llm, tools)
        self._token_usage = 0
        self._ref_map: Dict[str, int] = {}
        self._ref_list: List[Dict] = []
        self._output_dir = output_dir

    def run(self, state: ReportState) -> ReportState:
        self._build_ref_map(state)

        sections: List[str] = []

        # --- 섹션 2: 시장 배경 ---
        market_summary, market_raw = self._format_section_data(state, ["market"])

        s2_1 = self._generate_section(
            "2.1", "글로벌 배터리 시장 현황",
            "글로벌 배터리 시장의 규모, 성장률, ESS 시장 전망, 구조 변화를 데이터 기반으로 서술하세요.",
            market_summary, market_raw,
            categories=["시장 현황", "배터리 시장 구조 변화"],
        )
        s2_2 = self._generate_section(
            "2.2", "전기차 캐즘과 HEV 피벗",
            "전기차 시장의 성장 둔화(캐즘) 현상과 HEV 전환 트렌드를 분석하세요.",
            market_summary, market_raw,
            categories=["HEV 피벗"],
        )
        sections.append(f"## 2. 시장 배경\n\n{s2_1}\n\n{s2_2}")

        # --- 섹션 3: 기업별 전략 분석 ---
        sko_summary, sko_raw = self._format_section_data(state, ["sko"])
        catl_summary, catl_raw = self._format_section_data(state, ["catl"])

        s3_1 = self._generate_section(
            "3.1", "SK on 포트폴리오 다각화",
            "SK on의 사업 포트폴리오, 기술 경쟁력, 재무 현황, 공급망/생산, 시장 지위, 리스크를 종합 분석하세요. 각 항목의 긍정/부정 데이터를 균형 있게 서술하세요.",
            sko_summary, sko_raw,
        )
        s3_2 = self._generate_section(
            "3.2", "CATL 포트폴리오 다각화",
            "CATL의 사업 포트폴리오, 기술 경쟁력, 재무 현황, 공급망/생산, 시장 지위, 리스크를 종합 분석하세요. 각 항목의 긍정/부정 데이터를 균형 있게 서술하세요.",
            catl_summary, catl_raw,
        )
        sections.append(f"## 3. 기업별 전략 분석\n\n{s3_1}\n\n{s3_2}")

        # --- 섹션 4: 비교 분석 ---
        combined_summary = f"=== SK on ===\n{sko_summary}\n\n=== CATL ===\n{catl_summary}"
        combined_raw = f"=== SK on 상세 데이터 ===\n{sko_raw}\n\n=== CATL 상세 데이터 ===\n{catl_raw}"

        s4_1 = self._generate_section(
            "4.1", "핵심 전략 비교",
            "SK on과 CATL의 포트폴리오 다각화 전략을 항목별(사업, 기술, 재무, 공급망, 시장 지위)로 직접 비교하여 서술하세요. 단순 나열이 아닌 비교 관점으로 작성하세요.",
            combined_summary, combined_raw,
        )

        swot = state.get("comparative_swot", {})
        swot_table = swot.get("table", "[SWOT 테이블 데이터 없음]")
        s4_2 = f"### 4.2 Comparative SWOT\n\n{swot_table}"

        sections.append(f"## 4. 비교 분석\n\n{s4_1}\n\n{s4_2}")

        # --- 섹션 5: 종합 시사점 ---
        swot_insights = swot.get("insights", "[시사점 데이터 없음]")
        s5 = self._generate_section(
            "5", "종합 시사점",
            "아래 SWOT 분석 시사점을 기반으로, 두 기업의 전략적 방향성 차이, SK on 관점의 경쟁 대응 전략, 배터리 시장 전체의 구조적 함의를 포함하여 500자 내외로 작성하세요.",
            swot_insights, "",
            context=f"참고 — SWOT 테이블:\n{swot_table}",
        )
        sections.append(s5)

        # --- 섹션 6: REFERENCE ---
        references = self._format_references()
        sections.append(references)

        # --- 차트 생성 (본문 완성 후) ---
        full_body = "\n\n".join(sections)
        chart_paths = self._generate_charts(full_body)

        # --- 차트를 본문에 삽입 ---
        if chart_paths:
            full_body = self._insert_charts(full_body, chart_paths)

        # --- 섹션 1: SUMMARY (마지막 생성) ---
        summary_section = self._generate_summary(full_body)

        final_report = f"{summary_section}\n\n{full_body}"

        return {**state, "final_report": final_report, "chart_paths": chart_paths}

    # ----------------------------------------------------------------
    # 레퍼런스 매핑
    # ----------------------------------------------------------------

    def _build_ref_map(self, state: ReportState) -> None:
        self._ref_map = {}
        self._ref_list = []
        counter = 1
        for key in ["market", "sko", "catl"]:
            result = state.get(key, {})
            for item in result.get("raw", []):
                url = item.get("url", "")
                if url and url not in self._ref_map:
                    self._ref_map[url] = counter
                    self._ref_list.append({
                        "num": counter,
                        "source": item.get("source", ""),
                        "date": item.get("date", ""),
                        "title": item.get("title", ""),
                        "url": url,
                    })
                    counter += 1

    def _get_ref_num(self, url: str) -> int:
        return self._ref_map.get(url, 0)

    # ----------------------------------------------------------------
    # 데이터 포맷팅
    # ----------------------------------------------------------------

    def _format_section_data(
        self, state: ReportState, keys: List[str], categories: Optional[List[str]] = None
    ) -> tuple[str, str]:
        summaries: List[str] = []
        raw_lines: List[str] = []

        for key in keys:
            result = state.get(key, {})
            if result.get("summary"):
                summaries.append(result["summary"])
            for item in result.get("raw", []):
                cat = item.get("category", "")
                if categories and cat not in categories:
                    continue
                sentiment = item.get("sentiment", "")
                title = item.get("title", "")
                content = item.get("content", "")
                url = item.get("url", "")
                ref_num = self._get_ref_num(url)
                raw_lines.append(
                    f"[{ref_num}] [{cat} / {sentiment}] {title}\n{content}"
                )

        summary_text = "\n".join(summaries) if summaries else "[요약 데이터 없음]"
        raw_text = "\n\n".join(raw_lines) if raw_lines else "[상세 데이터 없음]"
        return summary_text, raw_text

    # ----------------------------------------------------------------
    # LLM 호출
    # ----------------------------------------------------------------

    def _generate_section(
        self,
        section_number: str,
        section_title: str,
        instructions: str,
        summary: str,
        raw_data: str,
        categories: Optional[List[str]] = None,
        context: str = "",
    ) -> str:
        estimated_input = len(summary) + len(raw_data) + len(context)
        if self._token_usage + estimated_input > self.MAX_TOKENS:
            return f"### {section_number} {section_title}\n\n[분석 미완료 — 토큰 한도 초과]"

        context_block = f"\n추가 참고 자료:\n{context}" if context else ""

        messages = [
            SystemMessage(content=REPORT_SYSTEM_PROMPT),
            HumanMessage(content=REPORT_SECTION_PROMPT.format(
                section_number=section_number,
                section_title=section_title,
                summary=summary,
                raw_data=raw_data,
                context=context_block,
                instructions=instructions,
            )),
        ]
        response = self.llm.invoke(messages)
        content = self._clean_response(response.content)
        self._token_usage += len(content)
        return content

    def _generate_summary(self, full_body: str) -> str:
        if self._token_usage + len(full_body) > self.MAX_TOKENS:
            return "## 1. SUMMARY\n\n[분석 미완료 — 토큰 한도 초과]"

        messages = [
            SystemMessage(content=REPORT_SYSTEM_PROMPT),
            HumanMessage(content=REPORT_SUMMARY_PROMPT.format(full_body=full_body)),
        ]
        response = self.llm.invoke(messages)
        return self._clean_response(response.content)

    # ----------------------------------------------------------------
    # 차트 생성
    # ----------------------------------------------------------------

    def _extract_chart_data(self, report_body: str) -> Dict:
        """LLM으로 완성된 본문에서 차트용 수치를 추출."""
        messages = [
            SystemMessage(content="보고서 본문에서 수치를 정확히 추출합니다. 본문에 없는 수치는 null로 표기합니다."),
            HumanMessage(content=CHART_DATA_EXTRACTION_PROMPT.format(report_body=report_body)),
        ]
        response = self.llm.invoke(messages)
        text = self._clean_response(response.content)

        # JSON 블록만 추출 (앞뒤 텍스트 제거)
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            print("[WARN] 차트 데이터 추출 실패: JSON 블록을 찾을 수 없음")
            print(f"[DEBUG] LLM 응답:\n{text[:500]}")
            return {}

        json_str = text[start:end]
        try:
            data = json.loads(json_str)
            print(f"[INFO] 차트 데이터 추출 성공: {list(data.keys())}")
            return data
        except json.JSONDecodeError as e:
            print(f"[WARN] 차트 데이터 JSON 파싱 실패: {e}")
            print(f"[DEBUG] JSON 문자열:\n{json_str[:500]}")
            return {}

    def _generate_charts(self, report_body: str) -> List[str]:
        """본문에서 수치를 추출하고 차트 이미지를 생성."""
        from tools.chart_generator import create_all_charts

        chart_data = self._extract_chart_data(report_body)
        if not chart_data:
            print("[WARN] 차트 데이터가 비어 있어 차트를 생성하지 않음")
            return []

        chart_dir = os.path.join(self._output_dir, "charts")
        paths = create_all_charts(chart_data, chart_dir)
        print(f"[INFO] 차트 이미지 {len(paths)}개 생성 완료")
        return paths

    def _insert_charts(self, full_body: str, chart_paths: List[str]) -> str:
        """생성된 차트를 본문의 적절한 위치에 절대경로 이미지로 삽입."""
        chart_map = {}
        for path in chart_paths:
            abs_path = os.path.abspath(path)
            basename = os.path.basename(path)
            if "market_trend" in basename:
                chart_map["market_trend"] = abs_path
            elif "company_comparison" in basename:
                chart_map["company_comparison"] = abs_path

        # 섹션 2 끝에 시장 트렌드 차트 삽입
        if "market_trend" in chart_map:
            marker = "## 3. 기업별 전략 분석"
            chart_md = f"\n\n![EV vs ESS 성장률 추이]({chart_map['market_trend']})\n\n"
            full_body = full_body.replace(marker, chart_md + marker)

        # 섹션 4.1 끝(4.2 앞)에 기업 비교 차트 삽입
        if "company_comparison" in chart_map:
            marker = "### 4.2 Comparative SWOT"
            chart_md = f"\n\n![SK on vs CATL 핵심 지표 비교]({chart_map['company_comparison']})\n\n"
            full_body = full_body.replace(marker, chart_md + marker)

        return full_body

    # ----------------------------------------------------------------
    # REFERENCE
    # ----------------------------------------------------------------

    def _format_references(self) -> str:
        lines = []
        for ref in self._ref_list:
            line = REFERENCE_FORMAT_PROMPT.format(
                source=ref["source"],
                date=ref["date"],
                title=ref["title"],
                url=ref["url"],
            )
            lines.append(f"[{ref['num']}] {line}")
        return "## 6. REFERENCE\n\n" + "\n".join(lines)

    # ----------------------------------------------------------------
    # 유틸리티
    # ----------------------------------------------------------------

    def _clean_response(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[-1].strip() == "```":
                content = "\n".join(lines[1:-1]).strip()
            else:
                content = "\n".join(lines[1:]).strip()
        return content
