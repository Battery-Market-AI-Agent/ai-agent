"""보고서용 차트 생성 모듈 (matplotlib).

차트 라이브러리:
  bar_comparison   — 두 기업 지표 비교 (막대)
  line_trend       — 시계열 추이 (라인)
  dual_bar_line    — 막대 + 기준선 복합
  grouped_bar      — 다항목 그룹 막대
  pie_comparison   — 비중 비교 (파이 2개)
"""
import os
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def _setup_korean_font():
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

COLOR_A = "#0066CC"
COLOR_B = "#CC3333"
COLOR_NEUTRAL = "#555555"
COLOR_ACCENT = "#22AA66"


# ================================================================
# 차트 라이브러리
# ================================================================

def bar_comparison(spec: Dict, output_path: str) -> str:
    """두 기업(또는 항목)의 지표를 막대로 비교.

    spec:
      title: str
      labels: [str, str]
      values: [float, float]
      unit: str  (예: "%", "조원")
    """
    labels = spec["labels"]
    values = [v if v is not None else 0 for v in spec["values"]]
    unit = spec.get("unit", "")

    fig, ax = plt.subplots(figsize=(5, 4))
    colors = [COLOR_A, COLOR_B]
    bars = ax.bar(labels, values, color=colors, width=0.5)

    for bar, val in zip(bars, values):
        y = bar.get_height() if val >= 0 else bar.get_height() - 0.5
        va = "bottom" if val >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width() / 2, y,
                f"{val}{unit}", ha="center", va=va, fontsize=12, fontweight="bold")

    ax.set_title(spec["title"], fontsize=13, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    min_v, max_v = min(values), max(values)
    ax.set_ylim(
        min(min_v * 1.3, -3) if min_v < 0 else 0,
        max_v * 1.4 if max_v > 0 else 5,
    )
    if min_v < 0:
        ax.axhline(y=0, color="black", linewidth=0.5)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def line_trend(spec: Dict, output_path: str) -> str:
    """시계열 추이 라인 차트.

    spec:
      title: str
      x_labels: [str, ...]
      lines: [{"label": str, "values": [float, ...]}, ...]
    """
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = [COLOR_A, COLOR_B, COLOR_ACCENT, COLOR_NEUTRAL]

    for i, line in enumerate(spec["lines"]):
        vals = [v if v is not None else 0 for v in line["values"]]
        c = colors[i % len(colors)]
        ax.plot(spec["x_labels"], vals, marker="o", color=c, linewidth=2.5, label=line["label"])
        for x, y in zip(spec["x_labels"], vals):
            ax.text(x, y + max(vals) * 0.03, f"{y}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_title(spec["title"], fontsize=13, fontweight="bold", pad=12)
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def dual_bar_line(spec: Dict, output_path: str) -> str:
    """막대 + 기준선(수평선) 복합 차트.

    spec:
      title: str
      bar_labels: [str, ...]
      bar_values: [float, ...]
      bar_unit: str
      line_value: float
      line_label: str
    """
    labels = spec["bar_labels"]
    values = [v if v is not None else 0 for v in spec["bar_values"]]
    unit = spec.get("bar_unit", "")

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, values, color=COLOR_NEUTRAL, alpha=0.7, width=0.5, label=spec.get("bar_label", ""))

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val}{unit}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    line_val = spec.get("line_value")
    if line_val is not None:
        ax.axhline(y=line_val, color=COLOR_ACCENT, linewidth=2.5, linestyle="--",
                   label=spec.get("line_label", f"{line_val}{unit}"))

    ax.set_title(spec["title"], fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, max(values + [line_val or 0]) * 1.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def grouped_bar(spec: Dict, output_path: str) -> str:
    """다항목 그룹 막대 (두 기업 × N개 지표).

    spec:
      title: str
      categories: [str, ...]       (지표명)
      group_a: {"label": str, "values": [float, ...]}
      group_b: {"label": str, "values": [float, ...]}
      unit: str
    """
    import numpy as np

    cats = spec["categories"]
    a_vals = [v if v is not None else 0 for v in spec["group_a"]["values"]]
    b_vals = [v if v is not None else 0 for v in spec["group_b"]["values"]]
    unit = spec.get("unit", "")

    x = np.arange(len(cats))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(7, len(cats) * 2), 4))
    bars_a = ax.bar(x - width / 2, a_vals, width, label=spec["group_a"]["label"], color=COLOR_A)
    bars_b = ax.bar(x + width / 2, b_vals, width, label=spec["group_b"]["label"], color=COLOR_B)

    for bar, val in zip(list(bars_a) + list(bars_b), a_vals + b_vals):
        y = bar.get_height() if val >= 0 else bar.get_height() - 0.5
        va = "bottom" if val >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width() / 2, y,
                f"{val}{unit}", ha="center", va=va, fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    ax.set_title(spec["title"], fontsize=13, fontweight="bold", pad=12)
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    all_vals = a_vals + b_vals
    min_v, max_v = min(all_vals), max(all_vals)
    ax.set_ylim(
        min(min_v * 1.3, -3) if min_v < 0 else 0,
        max_v * 1.4 if max_v > 0 else 5,
    )
    if min_v < 0:
        ax.axhline(y=0, color="black", linewidth=0.5)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def pie_comparison(spec: Dict, output_path: str) -> str:
    """비중 비교 파이 차트 (2개 나란히).

    spec:
      title: str
      pie_a: {"label": str, "highlight": float, "highlight_label": str}
      pie_b: {"label": str, "highlight": float, "highlight_label": str}
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

    for ax, pie in [(ax1, spec["pie_a"]), (ax2, spec["pie_b"])]:
        val = pie["highlight"] if pie["highlight"] is not None else 0
        rest = 100 - val
        sizes = [val, rest]
        labels = [pie["highlight_label"], "기타"]
        colors_p = [COLOR_A if ax == ax1 else COLOR_B, "#E0E0E0"]
        explode = (0.05, 0)
        ax.pie(sizes, explode=explode, labels=labels, colors=colors_p,
               autopct="%1.1f%%", startangle=90, textprops={"fontsize": 10})
        ax.set_title(pie["label"], fontsize=11, fontweight="bold", pad=8)

    fig.suptitle(spec["title"], fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


# ================================================================
# 차트 타입 레지스트리
# ================================================================

CHART_REGISTRY = {
    "bar_comparison": bar_comparison,
    "line_trend": line_trend,
    "dual_bar_line": dual_bar_line,
    "grouped_bar": grouped_bar,
    "pie_comparison": pie_comparison,
}


def create_charts(chart_specs: List[Dict], output_dir: str) -> List[Dict[str, str]]:
    """LLM이 선택한 차트 스펙 리스트를 받아 이미지를 생성.

    Args:
        chart_specs: [{"chart_type": str, "spec": dict, "section": str}, ...]
        output_dir: 이미지 저장 디렉토리

    Returns:
        [{"path": str, "section": str, "title": str}, ...]
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for i, item in enumerate(chart_specs):
        chart_type = item.get("chart_type", "")
        spec = item.get("spec", {})
        section = item.get("section", "")

        render_fn = CHART_REGISTRY.get(chart_type)
        if not render_fn:
            print(f"[WARN] 알 수 없는 차트 타입: {chart_type}")
            continue

        filename = f"chart_{i + 1}_{chart_type}.png"
        output_path = os.path.join(output_dir, filename)

        try:
            render_fn(spec, output_path)
            results.append({
                "path": os.path.abspath(output_path),
                "section": section,
                "title": spec.get("title", ""),
            })
            print(f"[INFO] 차트 생성: {filename} → 섹션 {section}")
        except Exception as e:
            print(f"[WARN] 차트 생성 실패 ({chart_type}): {e}")

    return results
