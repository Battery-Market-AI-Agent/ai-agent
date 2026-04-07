"""
실행 진입점

1. RAG 인덱스 로드 (이미 구축된 FAISS)
2. LLM 초기화
3. Graph 컴파일 + 실행
4. state["final_report"]를 파일로 출력 (outputs/)
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from graph import build_graph
from rag.embedder import get_embeddings
from rag.vectorstore import load_vectorstore
from tools.pdf_exporter import markdown_to_pdf

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(BASE_DIR, "rag", "faiss_index")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


def main():
    load_dotenv()

    # 1. RAG 인덱스 로드
    print("[1/5] RAG 인덱스 로드 중...")
    embeddings = get_embeddings()
    vectorstore = load_vectorstore(INDEX_DIR, embeddings)
    print(f"       FAISS 인덱스 로드 완료: {INDEX_DIR}")

    # 2. LLM 초기화
    print("[2/5] LLM 초기화...")
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    # 3. Graph 빌드 및 컴파일
    print("[3/5] Multi-Agent 그래프 빌드...")
    compiled_graph = build_graph(llm=llm, vectorstore=vectorstore, output_dir=OUTPUT_DIR)

    # 4. 그래프 실행
    print("[4/5] 파이프라인 실행 (T1→T2/T3→T4→T5)...")
    print("       T1: 시장 환경 조사 (RAG)")
    print("       T2: SK on 조사 (WebSearch)  ┐ 병렬")
    print("       T3: CATL 조사 (WebSearch)   ┘")
    print("       T4: Comparative SWOT 분석")
    print("       T5: 최종 보고서 생성")
    print()

    result = compiled_graph.invoke({})

    # 5. 보고서 저장
    print("[5/5] 보고서 저장...")
    report = result.get("final_report", "")
    if not report:
        print("[ERROR] final_report가 비어 있습니다.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 마크다운 저장
    md_path = os.path.join(OUTPUT_DIR, f"report_{timestamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"       마크다운: {md_path}")

    # PDF 저장
    pdf_path = os.path.join(OUTPUT_DIR, f"report_{timestamp}.pdf")
    markdown_to_pdf(report, pdf_path, base_dir=OUTPUT_DIR)
    print(f"       PDF: {pdf_path}")

    # 차트 경로 출력
    chart_paths = result.get("chart_paths", [])
    if chart_paths:
        print(f"       차트 {len(chart_paths)}개:")
        for p in chart_paths:
            print(f"         → {p}")

    print(f"\n[완료] 보고서 생성이 완료되었습니다. (총 {len(report):,}자)")


if __name__ == "__main__":
    main()
