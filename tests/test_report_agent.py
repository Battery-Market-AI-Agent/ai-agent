"""
T5 Report Agent 테스트 스크립트

사용법:
    # T4(Compare) + T5(Report) 전체 실행
    python -m tests.test_report_agent

    # T5만 단독 테스트 (하드코딩 SWOT 사용)
    python -m tests.test_report_agent --skip-compare
"""
import argparse
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.compare_agent import CompareAgent
from agents.report_agent import ReportAgent
from data.dummy_data import catl_data, market_data, sko_data
from state import ReportState

# 하드코딩 SWOT (--skip-compare 용)
FALLBACK_SWOT = {
    "table": (
        "| 구분 | SK on | CATL | 전략적 시사점 |\n"
        "|------|-------|------|---------------|\n"
        "| S - 내부 경쟁력 | NCM9½½ 하이니켈 양산, 현대차 밀착 공급 | LFP 원가 경쟁력, 글로벌 점유율 37.9% | SK on은 기술 차별화, CATL은 규모의 경제 |\n"
        "| W - 내부 취약점 | 3년 연속 적자, 영업이익률 미흑자 | 전고체 배터리 후발, R&D 비용 급증 | 양사 모두 차세대 기술 전환 부담 |\n"
        "| O - 외부 기회 | ESS 시장 확대, IRA 보조금 | 헝가리 공장으로 유럽 공략, 나트륨이온 | 비EV 시장(ESS, 로봇)이 새 성장축 |\n"
        "| T - 외부 리스크 | IRA 축소, 중국 가격 공세 | FEOC로 북미 차단, 탈중국 움직임 | 지정학이 시장 구도를 재편 중 |"
    ),
    "insights": (
        "SK on과 CATL은 상반된 전략적 포지션에 있다. CATL은 LFP 기반 원가 경쟁력과 "
        "37.9%의 압도적 점유율로 규모의 경제를 구축했으나, FEOC 규정으로 북미 시장 진입이 "
        "차단된 상태이다. SK on은 NCM 하이니켈 기술력과 북미 생산 거점을 보유하고 있으나, "
        "3년 연속 적자로 수익성 확보가 시급하다. 양사 모두 ESS와 차세대 배터리(전고체, "
        "나트륨이온)로의 포트폴리오 다각화를 추진 중이며, 지정학적 리스크가 시장 구도를 "
        "근본적으로 재편하고 있다."
    ),
}


def build_test_state(skip_compare: bool, llm=None) -> ReportState:
    """더미 데이터로 테스트용 state를 구성."""
    state: ReportState = {
        "market": market_data,
        "sko": sko_data,
        "catl": catl_data,
    }

    if skip_compare:
        print("[INFO] --skip-compare: 하드코딩 SWOT 사용")
        state["comparative_swot"] = FALLBACK_SWOT
    else:
        print("[INFO] CompareAgent(T4) 실행 중...")
        compare = CompareAgent(llm=llm)
        state = compare.run(state)
        print("[INFO] CompareAgent 완료")

    return state


def run_report(state: ReportState, llm, output_dir: str) -> ReportState:
    """ReportAgent(T5) 실행."""
    print("[INFO] ReportAgent(T5) 실행 중...")
    report = ReportAgent(llm=llm, output_dir=output_dir)
    state = report.run(state)
    print("[INFO] ReportAgent 완료")
    chart_paths = state.get("chart_paths", [])
    if chart_paths:
        print(f"[INFO] 차트 {len(chart_paths)}개 생성 완료")
        for p in chart_paths:
            print(f"       → {p}")
    return state


def save_report(report_text: str, output_dir: str) -> tuple[str, str]:
    """outputs/ 디렉토리에 보고서를 MD + PDF로 저장."""
    from tools.pdf_exporter import markdown_to_pdf

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 마크다운 저장
    md_path = os.path.join(output_dir, f"report_{timestamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # PDF 저장 (base_dir=output_dir로 차트 이미지 경로 해석)
    pdf_path = os.path.join(output_dir, f"report_{timestamp}.pdf")
    markdown_to_pdf(report_text, pdf_path, base_dir=output_dir)

    return md_path, pdf_path


def validate_report(report_text: str):
    """보고서 기본 검증."""
    checks = {
        "SUMMARY 섹션": "## 1. SUMMARY" in report_text or "# 1. SUMMARY" in report_text,
        "시장 배경 섹션": "시장 배경" in report_text,
        "기업별 전략 분석 섹션": "기업별 전략 분석" in report_text,
        "비교 분석 섹션": "비교 분석" in report_text,
        "종합 시사점 섹션": "종합 시사점" in report_text,
        "REFERENCE 섹션": "REFERENCE" in report_text,
        "분석 미완료 없음": "분석 미완료" not in report_text,
    }

    print("\n=== 검증 결과 ===")
    all_passed = True
    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False

    print(f"\n  총 글자 수: {len(report_text):,}")
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="T5 Report Agent 테스트")
    parser.add_argument("--skip-compare", action="store_true", help="T4 건너뛰고 하드코딩 SWOT 사용")
    args = parser.parse_args()

    load_dotenv()

    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")

    state = build_test_state(skip_compare=args.skip_compare, llm=llm)
    state = run_report(state, llm=llm, output_dir=output_dir)

    report = state.get("final_report", "")
    if not report:
        print("[ERROR] final_report가 비어 있습니다.")
        sys.exit(1)

    md_path, pdf_path = save_report(report, output_dir)
    print(f"\n[INFO] 마크다운 저장: {md_path}")
    print(f"[INFO] PDF 저장: {pdf_path}")

    passed = validate_report(report)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
