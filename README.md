# 배터리 시장 전략 분석 보고서 — Multi-Agent 시스템

SK on vs CATL 포트폴리오 다각화 전략 비교 분석 보고서를 Multi-Agent로 자동 생성하는 시스템.

## Overview

- **Objective** : SK on과 CATL의 전략을 자동으로 수집·분석하여 Comparative SWOT 기반 전략 보고서 생성
- **Method** : RAG 기반 시장 조사 → 웹 검색 기반 기업 조사(병렬) → LLM 추론 → 보고서 생성
- **Tools** : LangGraph, FAISS, Tavily Search, OpenAI GPT-4o, WeasyPrint, Matplotlib

## Features

- PDF 자료 기반 정보 추출 (RAG 활용)
- 웹 검색 기반 실시간 기업 동향 수집 (SK on, CATL 병렬 조사)
- Comparative SWOT 분석 및 전략적 인사이트 자동 생성
- 확증 편향 방지 전략 : 문서 관련성 평가(grade) + 쿼리 재작성(rewrite) 루프로 편향된 검색 결과 필터링
- 보고서 자동 출력 (Markdown + PDF + 차트)

## Tech Stack

| Category   | Details                                  |
|------------|------------------------------------------|
| Framework  | LangGraph, LangChain, Python             |
| LLM        | GPT-4o via OpenAI API                    |
| Retrieval  | FAISS (RAG, 문서 관련성 평가 포함)            |
| Embedding  | BGE-base-en-v1.5(FlagEmbedding)          |
| WebSearch  | Tavily Search API                        |
| Output     | WeasyPrint (PDF), Matplotlib (차트)       |

## Agents

- **Market Agent (T1)** : RAG 기반 배터리 시장 환경 조사 (LangGraph 서브그래프, Agentic RAG)
- **SKO Agent (T2)** : Tavily 웹 검색으로 SK on 기업 동향 조사
- **CATL Agent (T3)** : Tavily 웹 검색으로 CATL 기업 동향 조사 (T2와 병렬 실행)
- **Compare Agent (T4)** : T1~T3 결과 기반 Comparative SWOT 분석 (LLM 추론)
- **Report Agent (T5)** : 최종 전략 보고서 생성 및 차트 선택 (Markdown/PDF 출력)

## Architecture

<img width="1282" height="1168" alt="image" src="https://github.com/user-attachments/assets/8d3025e4-f85e-4f92-b116-217869b2aa7b" />


## Directory Structure

```
├── agents/                # Agent 모듈 (Market, SKO, CATL, Compare, Report)
├── prompts/               # 프롬프트 템플릿
├── tools/                 # RAG 도구, WebSearch 도구, 차트/PDF 생성
├── rag/                   # PDF 로더, 임베딩, FAISS 벡터스토어
├── data/                  # RAG용 PDF 문서 (IR/ESG 보고서)
├── outputs/               # 생성된 보고서 저장
├── app.py                 # 실행 스크립트
└── README.md
```

## Getting Started

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경 변수 설정 (.env)
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key

# 4. RAG 인덱스 빌드
python rag/build_index.py

# 5. 실행
python app.py
```


## Contributors

| 이름 | 역할 | 담당 |
|------|------|------|
| 김상현 | T5 Report Agent | 보고서 생성 에이전트, 파이프라인 연결 |
| 김은비 | T2/T3 Research Agent | SK on·CATL 웹검색 에이전트 (Tavily) |
| 나현서 | T1 Market Agent | 시장 환경 조사 에이전트 (RAG/FAISS) |
| 임유경 | T4 Compare Agent | Comparative SWOT 분석 에이전트 |
