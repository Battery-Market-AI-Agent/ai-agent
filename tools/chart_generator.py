"""보고서용 차트 생성 모듈 (matplotlib)."""
import os
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def _setup_korean_font():
    """한국어 폰트 설정. macOS → Apple SD Gothic Neo, 없으면 fallback."""
    candidates = [
        "Apple SD Gothic Neo",
        "AppleGothic",
        "Malgun Gothic",
        "NanumGothic",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


_setup_korean_font()

# 공통 색상
COLOR_SKO = "#0066CC"
COLOR_CATL = "#CC3333"
COLOR_EV = "#555555"
COLOR_ESS = "#22AA66"


def create_market_trend_chart(chart_data: Dict, output_path: str) -> str:
    """차트 ①: EV 성장률 추이 vs ESS CAGR (듀얼 라인/바)."""
    ev = chart_data.get("ev_growth", {})
    ess_cagr = chart_data.get("ess_cagr")

    years = sorted(ev.keys())
    ev_values = [ev[y] for y in years if ev[y] is not None]
    valid_years = [y for y in years if ev[y] is not None]

    fig, ax = plt.subplots(figsize=(7, 4))

    # EV 성장률 바
    bars = ax.bar(valid_years, ev_values, color=COLOR_EV, alpha=0.7, width=0.5, label="EV 판매 성장률 (%)")
    for bar, val in zip(bars, ev_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    # ESS CAGR 수평선
    if ess_cagr is not None:
        ax.axhline(y=ess_cagr, color=COLOR_ESS, linewidth=2.5, linestyle="--", label=f"ESS CAGR ({ess_cagr}%)")

    ax.set_ylabel("성장률 (%)")
    ax.set_title("EV 성장률 둔화 vs ESS 성장 가속", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, max(ev_values + [ess_cagr or 0]) * 1.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def create_company_comparison_chart(chart_data: Dict, output_path: str) -> str:
    """차트 ③+④+⑦: 기업 비교 종합 3-panel (점유율 | ESS 비중 | 영업이익률)."""
    share = chart_data.get("market_share", {})
    ess = chart_data.get("ess_ratio", {})
    margin = chart_data.get("operating_margin", {})

    fig, axes = plt.subplots(1, 3, figsize=(10, 4))
    companies = ["SK on", "CATL"]
    colors = [COLOR_SKO, COLOR_CATL]

    panels = [
        ("시장 점유율 (%)", [share.get("sko", 0), share.get("catl", 0)]),
        ("ESS 매출 비중 (%)", [ess.get("sko", 0), ess.get("catl", 0)]),
        ("영업이익률 (%)", [margin.get("sko", 0), margin.get("catl", 0)]),
    ]

    for ax, (title, values) in zip(axes, panels):
        safe_values = [v if v is not None else 0 for v in values]
        bars = ax.bar(companies, safe_values, color=colors, width=0.5)

        for bar, val in zip(bars, safe_values):
            y_pos = bar.get_height() if val >= 0 else bar.get_height() - 1.5
            va = "bottom" if val >= 0 else "top"
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                    f"{val}%", ha="center", va=va, fontsize=11, fontweight="bold")

        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # y축 범위: 음수 포함 가능
        min_val = min(safe_values)
        max_val = max(safe_values)
        ax.set_ylim(
            min(min_val * 1.3, -5) if min_val < 0 else 0,
            max_val * 1.4 if max_val > 0 else 5,
        )
        if min_val < 0:
            ax.axhline(y=0, color="black", linewidth=0.5)

    fig.suptitle("SK on vs CATL 핵심 지표 비교", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def create_all_charts(chart_data: Dict, output_dir: str) -> List[str]:
    """모든 차트를 생성하고 파일 경로 리스트를 반환."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    path1 = os.path.join(output_dir, "chart_market_trend.png")
    create_market_trend_chart(chart_data, path1)
    paths.append(path1)

    path2 = os.path.join(output_dir, "chart_company_comparison.png")
    create_company_comparison_chart(chart_data, path2)
    paths.append(path2)

    return paths
