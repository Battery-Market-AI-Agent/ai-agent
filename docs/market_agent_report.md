# T1 시장 환경 조사 에이전트 — 구현 보고서

## 1. 개요

배터리 시장 분석 멀티에이전트 시스템의 T1(시장 환경 조사) 에이전트.
PDF 문서를 기반으로 Agentic RAG Loop를 수행하여 `state["market"]`에 시장 조사 결과를 저장한다.

---

## 2. 아키텍처

```
PDF 문서
   ↓ pdfplumber (텍스트 추출)
   ↓ RecursiveCharacterTextSplitter (청킹)
   ↓ BGE-M3 (임베딩)
FAISS 인덱스 (디스크 저장)
   ↓
MarketAgent.run()
   ↓ 쿼리 4개 순회
   ↓ LangGraph 서브그래프 (쿼리 1개당)
      retrieve → grade → rewrite(최대 3회) → finalize
   ↓
ResearchResult { raw: [...], summary: "..." }
```

---

## 3. RAG 파이프라인 상세

### 3.1 PDF 로더 (`rag/loader.py`)

| 항목 | 값 |
|------|----|
| 라이브러리 | `pdfplumber` |
| 최대 페이지 수 | 100페이지 (텍스트 추출 가능한 페이지 기준) |
| 페이지 카운트 방식 | 빈 페이지(텍스트 없음) 제외 후 카운트 |
| 메타데이터 | `source` (파일명), `page` (1-indexed), `date` |

### 3.2 청킹 (`rag/loader.py`)

| 항목 | 값 |
|------|----|
| Splitter | `RecursiveCharacterTextSplitter` |
| chunk_size | 700 |
| chunk_overlap | 100 |

### 3.3 임베딩 모델 (`rag/embedder.py`)

| 항목 | 값 |
|------|----|
| 모델 | `BAAI/bge-m3` |
| 제공처 | HuggingFace (로컬 실행) |
| 디바이스 | CPU |
| 정규화 | `normalize_embeddings=True` |
| 특징 | 한/영 다국어 지원, OpenAI API 비용 없음 |

### 3.4 벡터스토어 (`rag/vectorstore.py`)

| 항목 | 값 |
|------|----|
| 엔진 | FAISS (Facebook AI Similarity Search) |
| 저장 방식 | 로컬 디스크 (`rag/faiss_index/`) |
| 유사도 | L2 (기본값) |
| 인덱스 빌드 | `python -m rag.build_index` (1회성) |

### 3.5 검색 (`rag/rag_tool.py`)

| 항목 | 값 |
|------|----|
| top_k | 10 |
| 검색 방식 | `similarity_search` (FAISS 기본) |

---

## 4. Agentic RAG Loop (`agents/market_agent.py`)

LangGraph `StateGraph`로 구성된 서브그래프. 쿼리 1개당 독립적으로 invoke된다.

### 4.1 노드 구성

```
START → retrieve → grade → (조건 분기)
                              ├─ relevant → finalize → END
                              └─ not relevant → rewrite → retrieve (재시도)
                                                  └─ retry_count >= 3 → finalize → END
```

| 노드 | 역할 |
|------|------|
| `retrieve` | FAISS에서 top-10 문서 검색 |
| `grade` | LLM으로 관련성 판단 (relevant / not relevant) |
| `rewrite` | LLM으로 쿼리 재작성, retry_count +1 |
| `finalize` | 최종 결과 dict 생성 (불충분 시 fallback) |

### 4.2 재시도 정책

| 항목 | 값 |
|------|----|
| 최대 재시도 횟수 | 3회 |
| 재시도 트리거 | grade == "not relevant" |
| Fallback | `content: "검색 데이터 불충분"` |

### 4.3 Grader 판단 기준

- **relevant**: 검색 결과에 쿼리와 관련된 내용이 조금이라도 언급된 경우
- **not relevant**: 검색 결과가 쿼리와 전혀 무관한 경우

판단은 LLM 호출로 수행. `"not"` 포함 여부로 파싱.

---

## 5. RAG 쿼리 목록 (`rag/market_prompt.py`)

| 카테고리 | 쿼리 |
|----------|------|
| 글로벌 배터리 시장 현황 | global battery market size growth forecast 2024 2025 2026 |
| 전기차 캐즘 | electric vehicle EV demand slowdown sales decline chasm 2024 2025 |
| HEV 전환 트렌드 | hybrid HEV battery demand shift trend growth 2024 2025 |
| ESS 시장 성장 | battery energy storage stationary storage market growth demand 2024 2025 |

---

## 6. LLM 설정

| 항목 | 값 |
|------|----|
| 모델 | `gpt-4o-mini` (OpenAI) |
| 사용 목적 | Grader, Query Rewriter, Summary 생성 |
| API 키 | `.env` 파일의 `OPENAI_API_KEY` |

---

## 7. 출력 구조

```python
state["market"] = {
    "raw": [
        {
            "category": "글로벌 배터리 시장 현황",
            "title": "GlobalEVOutlook2025 p.5",
            "content": "...",         # 검색된 청크 전문
            "source": "GlobalEVOutlook2025",
            "url": "https://...",
            "date": "",
            "sentiment": "",
        },
        ...                           # 총 4개 (쿼리 수만큼)
    ],
    "summary": "...",                 # LLM 생성 요약 (4문단)
}
```

---

## 8. 파일 구조

```
rag/
├── data/                  # PDF 원본 파일
│   └── GlobalEVOutlook2025.pdf
├── faiss_index/           # 빌드된 FAISS 인덱스 (gitignore)
├── build_index.py         # 인덱스 빌드 스크립트
├── loader.py              # PDF 로드 + 청킹
├── embedder.py            # BGE-M3 임베딩 로드
├── vectorstore.py         # FAISS 인덱스 CRUD
├── rag_tool.py            # retrieve / grade / rewrite
└── market_prompt.py       # 쿼리 목록 + LLM 프롬프트

agents/
└── market_agent.py        # LangGraph 서브그래프 + MarketAgent

scripts/
└── run_market_agent.py    # 단독 실행 테스트 스크립트

tests/
├── rag/
│   ├── test_rag_tool.py
│   └── test_vectorstore.py
└── test_market_agent.py
```

---

## 9. 실행 방법

```bash
# 1. 최초 1회: FAISS 인덱스 빌드
python -m rag.build_index

# 2. 에이전트 단독 실행 테스트
python scripts/run_market_agent.py

# 3. 유닛 테스트
pytest tests/ -v
```
