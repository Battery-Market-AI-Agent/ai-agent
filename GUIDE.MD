# 배터리 시장 전략 분석 보고서 — Multi-Agent 프로젝트 스캐폴딩

## 프로젝트 개요

- SK on vs CATL 포트폴리오 다각화 전략 비교 분석 보고서를 Multi-Agent로 자동 생성
- Distributed 패턴 (각 Agent가 독립 수행, 공유 State로 결과 전달)
- LangGraph + LangChain + Python

## 아키텍처

```
[Market Agent(T1)] ─── RAG(FAISS)
        ↓
[SKO Agent(T2)] ──┐ ── WebSearch     (병렬)
[CATL Agent(T3)] ─┘ ── WebSearch
        ↓
[Compare Agent(T4)] ── LLM 추론
        ↓
[Report Agent(T5)] ── LLM 생성
```

## 디렉토리 구조 (이 구조대로 생성해줘)

```
├── data/                      # RAG용 PDF 문서 (IR/ESG 보고서)
├── agents/
│   ├── __init__.py
│   ├── base.py                # BaseAgent 클래스
│   ├── market_agent.py        # T1: 시장 환경 조사 (RAG)
│   ├── sko_agent.py           # T2: SK on 조사 (WebSearch)
│   ├── catl_agent.py          # T3: CATL 조사 (WebSearch)
│   ├── compare_agent.py       # T4: Comparative SWOT (LLM 추론)
│   └── report_agent.py        # T5: 최종 보고서 생성 (LLM 생성)
├── tools/
│   ├── __init__.py
│   ├── rag_tool.py            # RAG Retrieve + Grader
│   └── web_search_tool.py     # WebSearch + 확증 편향 방지 (긍/부정 병렬)
├── prompts/
│   ├── market_prompt.py       # T1 프롬프트
│   ├── research_prompt.py     # T2, T3 공통 프롬프트 (회사명만 변수)
│   ├── compare_prompt.py      # T4 프롬프트
│   └── report_prompt.py       # T5 프롬프트
├── rag/
│   ├── __init__.py
│   ├── loader.py              # PDF 로드 + 청킹
│   ├── embedder.py            # multilingual-e5-large 임베딩
│   └── vectorstore.py         # FAISS 인덱스 생성/검색
├── outputs/                   # 생성된 보고서 저장
├── state.py                   # 공유 State 정의
├── graph.py                   # LangGraph 그래프 정의 (노드 연결, 병렬)
├── app.py                     # 실행 스크립트
├── requirements.txt
└── README.md
```

## State 정의 (state.py)

```python
from typing import TypedDict, List, Dict, Literal

class ResearchResult(TypedDict, total=False):
    """각 조사 Agent의 결과물"""
    raw: List[Dict]
    # raw 내부 dict 구조:
    # {
    #     "category": str,       # 6가지 항목 중 하나 (사업 포트폴리오, 기술 경쟁력, 재무 현황, 공급망/생산, 시장 지위, 리스크)
    #     "sentiment": str,      # "positive" 또는 "negative"
    #     "title": str,          # 기사/자료 제목
    #     "content": str,        # 조사 내용
    #     "source": str,         # 출처 기관명
    #     "url": str,            # URL
    #     "date": str            # YYYY-MM-DD
    # }
    summary: str

class SWOTResult(TypedDict, total=False):
    """Comparative SWOT 분석 결과"""
    table: str       # S/W/O/T × LG/CATL/전략적 시사점 테이블
    insights: str    # 종합 시사점

class ReportState(TypedDict, total=False):
    # Research Layer
    market: ResearchResult
    sko: ResearchResult
    catl: ResearchResult
    # Analysis Layer
    comparative_swot: SWOTResult
    # Report Layer
    final_report: str
```

## Agent 클래스 구조 (agents/base.py)

```python
# 모든 Agent가 상속하는 베이스 클래스
# - llm, tools를 공통으로 받음
# - run(state) -> state 인터페이스 통일
# - 각 Agent는 run()만 오버라이드
```

## 각 파일별 가이드 (주석으로만 작성, 구현은 비워둬)

### agents/market_agent.py (T1)

```
# BaseAgent 상속
# Tool: RAG (FAISS 검색)
# Agentic RAG Loop:
#   1. 쿼리 생성 (배터리 시장 환경, 캐즘, HEV 피벗 등)
#   2. RAG 검색
#   3. Grader(LLM)로 관련성 판단 (relevant / not relevant)
#   4. not relevant → 쿼리 재작성 → 재검색 (max 2회, 로컬 변수로 관리)
#   5. 2회 실패 시 해당 항목 "[데이터 불충분]" 처리
# 결과를 state["market"]에 ResearchResult 형태로 저장
```

### agents/sko_agent.py (T2)

```
# BaseAgent 상속
# Tool: WebSearch
# 확증 편향 방지: 긍정 쿼리 + 부정 쿼리 병렬 검색
#   - 긍정: "SK on ESS 성장 전략 포트폴리오 다각화 2025 2026"
#   - 부정: "SK on 실적 부진 리스크 가동률 하락 약점 2025 2026"
# 6가지 조사 항목: 사업 포트폴리오, 기술 경쟁력, 재무 현황, 공급망/생산, 시장 지위, 리스크
# 각 결과를 raw list[dict] 형태로 저장 (category, sentiment, title, content, source, url, date)
# 검색 실패 시 쿼리 변경 후 1회 재시도
# 결과를 state["sko"]에 저장
```

### agents/catl_agent.py (T3)

```
# BaseAgent 상속
# sko_agent.py와 동일 구조, 회사명만 CATL로 변경
# T2와 병렬 실행됨
# 결과를 state["catl"]에 저장
```

### agents/compare_agent.py (T4)

```
# BaseAgent 상속
# Tool: 없음 (LLM 추론만)
# 입력: state["sko"]["summary"] + state["catl"]["summary"] (필요시 raw 참조)
# Comparative SWOT 테이블 생성:
#   | 구분 | SK on | CATL | 전략적 시사점 |
#   | S - 내부 경쟁력 | ... | ... | ... |
#   | W - 내부 취약점 | ... | ... | ... |
#   | O - 외부 기회   | ... | ... | ... |
#   | T - 외부 리스크 | ... | ... | ... |
# 결과를 state["comparative_swot"]에 SWOTResult(table, insights)로 저장
```

### agents/report_agent.py (T5)

```
# BaseAgent 상속
# Tool: 없음 (LLM 생성)
# 입력: state 전체 (raw 기반으로 작성 — 요약 손실 방지)
# 보고서 목차:
#   1. SUMMARY (반 페이지)
#   2. 시장 배경
#      2.1 글로벌 배터리 시장 현황
#      2.2 전기차 캐즘과 HEV 피벗
#   3. 기업별 전략 분석
#      3.1 SK on 포트폴리오 다각화
#      3.2 CATL 포트폴리오 다각화
#   4. 비교 분석
#      4.1 핵심 전략 비교
#      4.2 Comparative SWOT (state["comparative_swot"]["table"] 활용)
#   5. 종합 시사점 (state["comparative_swot"]["insights"] 활용)
#   6. REFERENCE (raw 내 source, url, date에서 추출, 형식 준수)
# REFERENCE 형식:
#   - 웹페이지: 기관명(YYYY-MM-DD). 제목. URL
# state["final_report"]에 저장
```

### tools/rag_tool.py

```
# RAG Retrieve: FAISS에서 유사도 검색
# Grader: LLM에게 검색 결과 관련성 판단 시키는 함수 (relevant / not relevant)
# 쿼리 재작성: not relevant 시 LLM으로 쿼리 리포뮬레이션
```

### tools/web_search_tool.py

```
# WebSearch 실행 함수
# 확증 편향 방지: 긍정 쿼리 + 부정 쿼리를 받아서 각각 검색
# 결과를 raw dict 형태로 반환
# 2025년 이후 자료만 필터링
```

### rag/loader.py

```
# PDF 로드 (PyPDF, PDFPlumber 등)
# 청킹: 500~800 tokens, overlap 100
# 총 100페이지 이내 제한
```

### rag/embedder.py

```
# 임베딩 모델: multilingual-e5-large (오픈소스, 한중영 다국어)
# HuggingFace에서 로드
```

### rag/vectorstore.py

```
# FAISS 인덱스 생성
# 검색 함수 (쿼리 → top-k 문서 반환)
```

### graph.py

```
# LangGraph로 그래프 정의
# 노드: MarketAgent, SKOAgent, CATLAgent, CompareAgent, ReportAgent
# 엣지:
#   START → MarketAgent
#   MarketAgent → [SKOAgent, CATLAgent]  (fan-out, 병렬)
#   [SKOAgent, CATLAgent] → CompareAgent (fan-in)
#   CompareAgent → ReportAgent
#   ReportAgent → END
```

### app.py

```
# 실행 진입점
# 1. RAG 인덱스 로드 (이미 구축된 FAISS)
# 2. LLM 초기화
# 3. Graph 컴파일 + 실행
# 4. state["final_report"]를 파일로 출력 (outputs/)
```

## 핵심 제약사항

- 토큰 총합 200,000 초과 시 완성된 섹션만 출력, 미완성은 "분석 미완료" 명시
- RAG 재검색 max 2회 (Agent 내부 로컬 변수)
- WebSearch 실패 시 쿼리 변경 후 1회 재시도
- 근거 없는 주장은 보고서에 포함하지 않음

## 요청사항

- 위 디렉토리 구조대로 파일을 생성해줘
- 각 파일에는 위 가이드를 **주석으로만** 작성하고 구현은 비워둬
- import문과 클래스/함수 시그니처(껍데기)만 작성
- requirements.txt에 필요한 패키지 목록 작성
