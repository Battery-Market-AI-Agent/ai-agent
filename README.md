# 배터리 시장 전략 분석 보고서 — Multi-Agent 시스템

SK on vs CATL 포트폴리오 다각화 전략 비교 분석 보고서를 Multi-Agent로 자동 생성하는 프로젝트.

## 아키텍처

- **Distributed 패턴**: 각 Agent가 독립 수행, 공유 State로 결과 전달
- **프레임워크**: LangGraph + LangChain + Python

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

## 환경 설정

### 1. Python 가상환경 생성 및 활성화

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 API 키를 입력합니다.

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
```

### 4. RAG용 PDF 문서 준비

`data/` 디렉토리에 분석에 사용할 PDF 문서(IR/ESG 보고서)를 넣어주세요.

### 5. 실행

```bash
python app.py
```

생성된 보고서는 `outputs/` 디렉토리에 저장됩니다.

## 디렉토리 구조

| 디렉토리 | 설명 |
|----------|------|
| `agents/` | Agent 클래스 (Market, SKO, CATL, Compare, Report) |
| `tools/` | RAG 도구, WebSearch 도구 |
| `prompts/` | 각 Agent별 프롬프트 |
| `rag/` | PDF 로더, 임베딩, FAISS 벡터스토어 |
| `data/` | RAG용 PDF 문서 (IR/ESG 보고서) |
| `outputs/` | 생성된 보고서 저장 |
