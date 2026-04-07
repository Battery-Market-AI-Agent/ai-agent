"""마크다운 보고서를 PDF로 변환하는 모듈."""
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
h3 { font-size: 13pt; margin-top: 20px; }
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
p { margin: 8px 0; }
"""


def markdown_to_pdf(md_text: str, output_path: str) -> str:
    """마크다운 텍스트를 PDF 파일로 변환한다.

    Args:
        md_text: 마크다운 형식의 보고서 텍스트
        output_path: 저장할 PDF 파일 경로

    Returns:
        저장된 PDF 파일 경로
    """
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><style>{REPORT_CSS}</style></head>
<body>{html_body}</body>
</html>"""

    HTML(string=full_html).write_pdf(output_path)
    return output_path
