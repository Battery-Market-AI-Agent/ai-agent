"""
실행 진입점

# 1. RAG 인덱스 로드 (이미 구축된 FAISS)
# 2. LLM 초기화
# 3. Graph 컴파일 + 실행
# 4. state["final_report"]를 파일로 출력 (outputs/)
"""
from graph import build_graph


def main():
    # TODO: 구현
    # 1. RAG 인덱스 로드 (data/ 디렉토리의 PDF → FAISS)
    # 2. LLM 초기화
    # 3. Graph 빌드 및 컴파일
    # 4. 초기 state로 그래프 실행
    # 5. state["final_report"]를 outputs/ 디렉토리에 파일로 저장
    ...


if __name__ == "__main__":
    main()
