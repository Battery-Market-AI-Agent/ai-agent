"""마크다운 보고서를 PDF로 변환하는 모듈."""
import os
import re

import markdown
from weasyprint import HTML

REPORT_CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm;
}
body {
    font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #1a1a1a;
}
h1 { font-size: 20pt; margin-top: 0; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; }
h2 { font-size: 16pt; margin-top: 28px; border-bottom: 1px solid #cccccc; padding-bottom: 4px; page-break-before: always; }
h2:first-of-type { page-break-before: avoid; }
h3 { font-size: 13pt; margin-top: 20px; page-break-before: avoid; }
table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 9.5pt;
}
th, td {
    border: 1px solid #999999;
    padding: 8px 10px;
    text-align: left;
    vertical-align: top;
}
th { background-color: #f0f0f0; font-weight: bold; }
td:first-child, th:first-child { white-space: nowrap; min-width: 5em; }
p { margin: 8px 0; }
.references p {
    font-size: 8.5pt;
    line-height: 1.3;
    margin: 2px 0;
    text-indent: -1.5em;
    padding-left: 1.5em;
}
img {
    display: block;
    max-width: 50%;
    margin: 16px auto;
}
"""


def _resolve_image_paths(html_text: str, base_dir: str) -> str:
    """상대 이미지 경로를 file:// 절대 경로로 변환 (weasyprint 호환)."""
    def replace_src(match):
        src = match.group(1)
        if src.startswith(("http://", "https://", "file://")):
            return match.group(0)
        abs_path = os.path.abspath(os.path.join(base_dir, src))
        return f'src="file://{abs_path}"'
    return re.sub(r'src="([^"]+)"', replace_src, html_text)


def markdown_to_pdf(md_text: str, output_path: str, base_dir: str = ".") -> str:
    """마크다운 텍스트를 PDF 파일로 변환한다.

    Args:
        md_text: 마크다운 형식의 보고서 텍스트
        output_path: 저장할 PDF 파일 경로
        base_dir: 이미지 상대 경로의 기준 디렉토리

    Returns:
        저장된 PDF 파일 경로
    """
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html_body = _resolve_image_paths(html_body, base_dir)
    # REFERENCE 섹션을 div.references로 감싸기
    html_body = re.sub(
        r'(<h2[^>]*>6\.\s*REFERENCE</h2>)(.*)',
        r'\1<div class="references">\2</div>',
        html_body,
        flags=re.DOTALL,
    )
    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><style>{REPORT_CSS}</style></head>
<body>{html_body}</body>
</html>"""

    HTML(string=full_html).write_pdf(output_path)
    return output_path
