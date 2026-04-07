"""T5: 최종 보고서 생성 Agent (LLM 생성)"""
import json
import os
from typing import Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool

from agents.base import BaseAgent
from prompts.report_prompt import (
    CHART_SELECTION_PROMPT,
    REFERENCE_FORMAT_PROMPT,
    REPORT_SECTION_PROMPT,
    REPORT_SUMMARY_PROMPT,
    REPORT_SYSTEM_PROMPT,
)
from state import ReportState


class ReportAgent(BaseAgent):
    """T5: 최종 보고서 생성 — state 전체를 기반으로 보고서 작성."""

    def __init__(
        self,
        llm: BaseChatModel,
        tools: List[BaseTool] | None = None,
        output_dir: str = "outputs",
    ):
        super().__init__(llm, tools)
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

        # --- 차트 생성 (본문 완성 후, LLM이 선택) ---
        full_body = "\n\n".join(sections)
        chart_results = self._generate_charts(full_body)

        # --- 차트를 본문에 삽입 ---
        if chart_results:
            full_body = self._insert_charts(full_body, chart_results)

        # --- 섹션 1: SUMMARY (마지막 생성) ---
        summary_section = self._generate_summary(full_body)

        # --- 섹션 6: REFERENCE (본문에서 인용된 것만) ---
        body_with_summary = f"{summary_section}\n\n{full_body}"
        references = self._format_references(body_with_summary)

        final_report = f"{body_with_summary}\n\n{references}"

        chart_paths = [c["path"] for c in chart_results]
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
        try:
            response = self.llm.invoke(messages)
            return self._clean_response(response.content)
        except Exception as e:
            print(f"[WARN] 섹션 {section_number} 생성 실패: {e}")
            return f"### {section_number} {section_title}\n\n[분석 미완료]"

    def _generate_summary(self, full_body: str) -> str:
        messages = [
            SystemMessage(content=REPORT_SYSTEM_PROMPT),
            HumanMessage(content=REPORT_SUMMARY_PROMPT.format(full_body=full_body)),
        ]
        try:
            response = self.llm.invoke(messages)
            return self._clean_response(response.content)
        except Exception as e:
            print(f"[WARN] SUMMARY 생성 실패: {e}")
            return "## 1. SUMMARY\n\n[분석 미완료]"

    # ----------------------------------------------------------------
    # 차트 생성
    # ----------------------------------------------------------------

    def _select_and_extract_charts(self, report_body: str) -> List[Dict]:
        """LLM이 보고서를 읽고 차트 라이브러리에서 효과적인 차트를 선택 + 데이터 추출."""
        messages = [
            SystemMessage(content="당신은 데이터 시각화 전문가입니다. 보고서 본문에 명시된 수치만 사용하세요."),
            HumanMessage(content=CHART_SELECTION_PROMPT.format(report_body=report_body)),
        ]
        response = self.llm.invoke(messages)
        text = self._clean_response(response.content)

        start = text.find("[")
        end = text.rfind("]") + 1
        if start == -1 or end == 0:
            print("[WARN] 차트 선택 실패: JSON 배열을 찾을 수 없음")
            return []

        try:
            specs = json.loads(text[start:end])
            if not isinstance(specs, list):
                return []
            print(f"[INFO] LLM이 차트 {len(specs)}개 선택: {[s.get('chart_type') for s in specs]}")
            for s in specs:
                print(f"       → {s.get('chart_type')} (섹션 {s.get('section')}): {s.get('reason', '')}")
            return specs
        except json.JSONDecodeError as e:
            print(f"[WARN] 차트 선택 JSON 파싱 실패: {e}")
            return []

    def _generate_charts(self, report_body: str) -> List[Dict[str, str]]:
        """LLM 선택 → 차트 이미지 생성. 반환: [{"path", "section", "title"}, ...]"""
        from tools.chart_generator import create_charts

        chart_specs = self._select_and_extract_charts(report_body)
        if not chart_specs:
            print("[INFO] 채택 기준에 맞는 차트가 없어 차트를 생성하지 않음")
            return []

        chart_dir = os.path.join(self._output_dir, "charts")
        return create_charts(chart_specs, chart_dir)

    def _insert_charts(self, full_body: str, chart_results: List[Dict[str, str]]) -> str:
        """생성된 차트를 해당 소제목 내용 뒤에 삽입.
        소제목은 #### 헤더 또는 **볼드** 형태 모두 지원."""
        import re

        def find_section_markers(text):
            """본문의 모든 구분점(헤더 + 볼드 소제목)의 (위치, 텍스트) 리스트."""
            markers = []
            # ## / ### / #### 헤더
            for m in re.finditer(r"^#{2,4}\s+.+", text, re.MULTILINE):
                markers.append((m.start(), m.group()))
            # **볼드 소제목** (줄 시작에 위치)
            for m in re.finditer(r"^\*\*(.+?)\*\*", text, re.MULTILINE):
                markers.append((m.start(), m.group(1)))
            markers.sort(key=lambda x: x[0])
            return markers

        # 뒤에서부터 삽입 (위치 밀림 방지)
        for chart in reversed(chart_results):
            section_name = chart.get("section", "")
            abs_path = chart.get("path", "")
            try:
                path = os.path.relpath(abs_path, self._output_dir)
            except ValueError:
                path = abs_path
            title = chart.get("title", "차트")

            markers = find_section_markers(full_body)

            # 소제목명으로 매칭 (부분 매칭)
            target_idx = None
            for i, (pos, marker_text) in enumerate(markers):
                if section_name in marker_text:
                    target_idx = i
                    break

            if target_idx is None:
                print(f"[WARN] 차트 삽입 실패: '{section_name}' 소제목을 찾을 수 없음")
                continue

            # 다음 마커 직전, 없으면 본문 끝
            if target_idx + 1 < len(markers):
                insert_pos = markers[target_idx + 1][0]
            else:
                insert_pos = len(full_body)

            chart_md = f"\n\n![{title}]({path})\n\n"
            full_body = full_body[:insert_pos] + chart_md + full_body[insert_pos:]
            print(f"[INFO] 차트 삽입: '{title}' → '{section_name}' 뒤")

        return full_body

    # ----------------------------------------------------------------
    # REFERENCE
    # ----------------------------------------------------------------

    def _format_references(self, report_body: str) -> str:
        """본문에서 실제로 [n]으로 인용된 레퍼런스만 REFERENCE에 포함."""
        import re
        cited_nums = set(int(n) for n in re.findall(r"\[(\d+)\]", report_body))

        lines = []
        for ref in self._ref_list:
            if ref["num"] not in cited_nums:
                continue
            line = REFERENCE_FORMAT_PROMPT.format(
                source=ref["source"],
                date=ref["date"],
                title=ref["title"],
                url=ref["url"],
            )
            lines.append(f"[{ref['num']}] {line}")
        return "## 6. REFERENCE\n\n" + "\n\n".join(lines)

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
