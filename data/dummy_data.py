"""
더미 데이터: 각 Agent(T1~T3)가 조사해왔다고 가정한 결과물
T4(Compare Agent), T5(Report Agent) 개발 시 이 데이터로 테스트
"""

# ============================================================
# T1: Market Agent 결과 (시장 환경 조사 - RAG 기반)
# ============================================================
market_data = {
    "raw": [
        {
            "category": "시장 현황",
            "sentiment": "negative",
            "title": "글로벌 전기차 판매 성장률 둔화",
            "content": "2025년 글로벌 전기차 판매 성장률은 전년 대비 12%로, 2022년(65%)과 2023년(35%) 대비 크게 둔화되었다. 주요 원인은 보조금 축소, 충전 인프라 부족, 소비자 가격 저항 등이다.",
            "source": "SNE리서치",
            "url": "https://www.sneresearch.com/report/2025-ev-market",
            "date": "2025-06-15"
        },
        {
            "category": "시장 현황",
            "sentiment": "positive",
            "title": "ESS 시장 급성장",
            "content": "글로벌 ESS 시장은 2025년 120GWh에서 2030년 400GWh로 연평균 27% 성장이 전망된다. AI 데이터센터의 전력 수요 급증과 재생에너지 확대가 핵심 동력이다.",
            "source": "BloombergNEF",
            "url": "https://about.bnef.com/energy-storage-outlook-2025",
            "date": "2025-07-20"
        },
        {
            "category": "HEV 피벗",
            "sentiment": "positive",
            "title": "하이브리드 차량 수요 급증",
            "content": "2025년 상반기 글로벌 HEV 판매량은 전년 동기 대비 40% 증가했다. 현대차그룹은 HEV 라인업 확대로 영업이익률 9.5%를 기록하며 폭스바겐을 제쳤다.",
            "source": "연합뉴스",
            "url": "https://www.yna.co.kr/view/AKR20260311079200003",
            "date": "2026-03-11"
        },
        {
            "category": "HEV 피벗",
            "sentiment": "negative",
            "title": "혼다 100% 전동화 전략 실패",
            "content": "무리한 100% 전동화를 추진했던 혼다는 상장 후 69년 만에 첫 연간 적자가 전망되며, 부랴부랴 하이브리드 중심으로 전략을 수정하고 있다.",
            "source": "조선일보",
            "url": "https://www.chosun.com/economy/auto/2026/03/14/7454EX6YOVGHVHFB4ITC5DKU44/",
            "date": "2026-03-14"
        },
        {
            "category": "배터리 시장 구조 변화",
            "sentiment": "negative",
            "title": "K-배터리 북미 공장 독박 운영",
            "content": "글로벌 완성차 업체들이 합작을 깨고 빠져나가면서 한국 배터리 3사는 북미 공장을 단독 운영해야 하는 상황에 처했다. 고정비 부담과 가동률 저하가 심화되고 있다.",
            "source": "서울경제",
            "url": "https://www.sedaily.com/article/20020043",
            "date": "2026-02-28"
        },
        {
            "category": "배터리 시장 구조 변화",
            "sentiment": "positive",
            "title": "배터리 3사, 로봇·ESS로 사업 다각화",
            "content": "인터배터리 2026에서 한국 배터리 3사는 AI 데이터센터용 ESS와 로봇(Physical AI)용 배터리를 차세대 성장 동력으로 제시했다.",
            "source": "블로터",
            "url": "https://www.bloter.net/news/articleView.html?idxno=656400",
            "date": "2026-03-10"
        },
    ],
    "summary": "글로벌 전기차 시장은 성장률 둔화(캐즘)가 심화되는 가운데, HEV 피벗이 가속화되고 있다. 완성차 업체의 합작 이탈로 K-배터리 업계의 고정비 부담이 증가하고 있으나, ESS와 로봇용 배터리 등 포트폴리오 다각화로 돌파구를 모색 중이다. ESS 시장은 AI 데이터센터 수요에 힘입어 연평균 27% 성장이 전망된다."
}


# ============================================================
# T2: SKO Agent 결과 (SK on 조사 - WebSearch 기반)
# ============================================================
sko_data = {
    "raw": [
        # --- 사업 포트폴리오 ---
        {
            "category": "사업 포트폴리오",
            "sentiment": "positive",
            "title": "SK on ESS 사업 본격 확대",
            "content": "SK on은 2025년 북미·유럽 유틸리티 ESS 프로젝트 수주를 본격화하며 ESS 매출 비중을 전체의 12%까지 확대했다. AI 데이터센터용 대형 ESS 시장 공략에 속도를 내고 있다.",
            "source": "한국경제",
            "url": "https://www.hankyung.com/article/202506151234",
            "date": "2025-06-15"
        },
        {
            "category": "사업 포트폴리오",
            "sentiment": "negative",
            "title": "전기차 배터리 수주 감소세 지속",
            "content": "유럽 완성차 업체들의 전동화 지연으로 SK on의 전기차 배터리 신규 수주가 2025년 하반기 전년 동기 대비 20% 감소했다.",
            "source": "매일경제",
            "url": "https://www.mk.co.kr/news/business/2025-skon-order",
            "date": "2025-11-20"
        },
        # --- 기술 경쟁력 ---
        {
            "category": "기술 경쟁력",
            "sentiment": "positive",
            "title": "NCM9½½ 하이니켈 배터리 양산 개시",
            "content": "SK on은 2025년 하반기부터 니켈 함량 90% 이상의 NCM9½½ 하이니켈 배터리 양산을 시작했다. 에너지 밀도가 기존 대비 15% 향상되었으며, 현대차·포드 등에 공급 예정이다.",
            "source": "전자신문",
            "url": "https://www.etnews.com/20250815000456",
            "date": "2025-08-15"
        },
        {
            "category": "기술 경쟁력",
            "sentiment": "negative",
            "title": "전고체 배터리 개발 경쟁에서 후발 주자",
            "content": "SK on의 전고체 배터리 양산 목표는 2028년으로, 도요타(2027년)·삼성SDI(2027년) 대비 뒤처져 있다. 산화물계 전해질 기반 독자 기술 확보가 과제이다.",
            "source": "조선비즈",
            "url": "https://biz.chosun.com/20260110-skon-solid-state",
            "date": "2026-01-10"
        },
        # --- 재무 현황 ---
        {
            "category": "재무 현황",
            "sentiment": "positive",
            "title": "2025년 연간 매출 14조원, 적자 폭 축소",
            "content": "SK on은 2025년 연간 매출 14.2조원, 영업손실 3,200억원을 기록했다. 전년(-1.1조원) 대비 적자 폭이 크게 축소되었으며, IRA 보조금이 적자 축소에 기여했다.",
            "source": "SK on IR",
            "url": "https://www.skon.com/ir/2025-annual",
            "date": "2026-02-05"
        },
        {
            "category": "재무 현황",
            "sentiment": "negative",
            "title": "3년 연속 영업적자, 흑자 전환 시점 불투명",
            "content": "SK on은 2023년부터 3년 연속 영업적자를 기록 중이다. 북미 공장 초기 가동 비용과 원자재 가격 상승으로 흑자 전환 시점이 2027년 이후로 전망된다.",
            "source": "한국투자증권",
            "url": "https://www.koreainvestment.com/report/skon-2025",
            "date": "2026-02-15"
        },
        # --- 공급망/생산 ---
        {
            "category": "공급망/생산",
            "sentiment": "positive",
            "title": "조지아 2공장 가동 시작",
            "content": "SK on은 2025년 조지아 2공장(연간 33GWh) 가동을 시작했다. 현대차 조지아 공장과 인접해 물류 효율을 극대화하고 있다.",
            "source": "로이터",
            "url": "https://www.reuters.com/business/skon-georgia-plant2-2025",
            "date": "2025-10-05"
        },
        {
            "category": "공급망/생산",
            "sentiment": "negative",
            "title": "포드 합작 블루오벌SK 가동률 부진",
            "content": "포드와의 합작 공장(블루오벌SK)의 가동률이 45%에 미치지 못하고 있다. 포드의 전기차 판매 부진으로 배터리 인수 물량이 당초 계획을 크게 하회하고 있다.",
            "source": "서울경제",
            "url": "https://www.sedaily.com/article/ford-skon-utilization",
            "date": "2026-01-22"
        },
        # --- 시장 지위 ---
        {
            "category": "시장 지위",
            "sentiment": "positive",
            "title": "글로벌 시장 점유율 5위 유지",
            "content": "SK on은 2025년 글로벌 EV 배터리 사용량 기준 점유율 5.1%로 5위를 유지했다. 현대차그룹 전동화 확대에 따른 물량 증가가 점유율 방어에 기여했다.",
            "source": "SNE리서치",
            "url": "https://www.sneresearch.com/2025-battery-share",
            "date": "2026-01-30"
        },
        {
            "category": "시장 지위",
            "sentiment": "negative",
            "title": "중국 업체에 밀리는 글로벌 순위",
            "content": "CALB, 궈쉬안 등 중국 2선 업체들의 점유율 상승으로 SK on의 글로벌 5위 지위가 위협받고 있다. 비중국 시장에서의 경쟁력 확보가 시급하다.",
            "source": "블룸버그",
            "url": "https://www.bloomberg.com/skon-ranking-pressure",
            "date": "2026-02-20"
        },
        # --- 리스크 ---
        {
            "category": "리스크",
            "sentiment": "negative",
            "title": "IRA 보조금 축소 리스크",
            "content": "미국 IRA(인플레이션감축법) 배터리 제조 세액공제가 2026년부터 단계적으로 축소될 가능성이 제기되고 있다. SK on의 북미 수익성 개선 시나리오에 직접적 타격이 우려된다.",
            "source": "파이낸셜타임스",
            "url": "https://www.ft.com/ira-battery-subsidy-risk",
            "date": "2026-03-01"
        },
        {
            "category": "리스크",
            "sentiment": "negative",
            "title": "중국산 배터리 가격 공세 심화",
            "content": "CATL, BYD 등 중국 업체들의 LFP 배터리 가격이 kWh당 50달러대까지 하락하면서, 가격 경쟁력에서 한국 업체들이 크게 열위에 놓이고 있다.",
            "source": "머니투데이",
            "url": "https://www.mt.co.kr/china-battery-price-war",
            "date": "2026-02-10"
        },
    ],
    "summary": "SK on은 ESS 사업 확대(매출 비중 12%)와 NCM9½½ 하이니켈 양산으로 포트폴리오 다각화를 추진 중이다. 3년 연속 적자이나 적자 폭은 축소 추세이며, IRA 보조금이 수익성 개선의 핵심 변수이다. 조지아 2공장 가동으로 북미 생산 거점을 확보했으나, 블루오벌SK 가동률 부진과 IRA 축소 리스크가 위협 요인이다. 글로벌 5위로 중국 2선 업체의 추격을 받고 있다."
}


# ============================================================
# T3: CATL Agent 결과 (CATL 조사 - WebSearch 기반)
# ============================================================
catl_data = {
    "raw": [
        # --- 사업 포트폴리오 ---
        {
            "category": "사업 포트폴리오",
            "sentiment": "positive",
            "title": "CATL ESS 매출 비중 30% 돌파",
            "content": "CATL의 ESS 사업 매출 비중이 2025년 30%를 돌파했다. 중국 내수 신재생에너지 프로젝트뿐 아니라 아프리카, 동남아 등 신흥시장으로 ESS 공급을 확대하고 있다.",
            "source": "더구루",
            "url": "https://www.theguru.co.kr/news/article.html?no=97837",
            "date": "2025-09-10"
        },
        {
            "category": "사업 포트폴리오",
            "sentiment": "positive",
            "title": "나트륨이온 배터리 상업 배치 시작",
            "content": "CATL은 2026년 1분기부터 나트륨이온 배터리의 상업 배치를 시작했다. 리튬 대비 원가를 30% 절감할 수 있어 반값 전기차의 핵심 무기로 활용될 전망이다.",
            "source": "머니투데이",
            "url": "https://www.mt.co.kr/world/2025/12/31/2025123013512524107",
            "date": "2025-12-31"
        },
        {
            "category": "사업 포트폴리오",
            "sentiment": "negative",
            "title": "전기차 배터리 성장률 둔화",
            "content": "CATL의 전기차 배터리 부문 매출 성장률이 2024년 45%에서 2025년 18%로 급감했다. 중국 내수 전기차 시장의 성장 둔화가 주된 원인이다.",
            "source": "차이나데일리",
            "url": "https://www.chinadaily.com.cn/catl-ev-slowdown",
            "date": "2025-08-25"
        },
        # --- 기술 경쟁력 ---
        {
            "category": "기술 경쟁력",
            "sentiment": "positive",
            "title": "신닝(Shenxing) 초급속 충전 배터리 글로벌 확대",
            "content": "CATL의 신닝 LFP 배터리는 10분 충전으로 400km 주행이 가능하다. 2025년 유럽·동남아 완성차 업체 10곳 이상과 공급 계약을 체결했다.",
            "source": "로이터",
            "url": "https://www.reuters.com/catl-shenxing-global",
            "date": "2025-07-12"
        },
        {
            "category": "기술 경쟁력",
            "sentiment": "positive",
            "title": "CTP 3.0 기술로 팩 에너지 밀도 세계 최고",
            "content": "CATL의 Cell-to-Pack 3.0 기술은 셀 적재율 72%를 달성하며 팩 수준 에너지 밀도 세계 최고 기록을 보유하고 있다.",
            "source": "CATL 공식",
            "url": "https://www.catl.com/en/news/ctp3",
            "date": "2025-05-20"
        },
        {
            "category": "기술 경쟁력",
            "sentiment": "negative",
            "title": "전고체 배터리 개발 상대적 후발",
            "content": "CATL은 LFP·나트륨이온에 집중하면서 전고체 배터리 개발에서 도요타, 삼성SDI 대비 뒤처져 있다는 평가를 받고 있다. 2027년 샘플 수준에 그칠 전망이다.",
            "source": "니혼게이자이",
            "url": "https://www.nikkei.com/catl-solid-state-lag",
            "date": "2025-11-05"
        },
        # --- 재무 현황 ---
        {
            "category": "재무 현황",
            "sentiment": "positive",
            "title": "2025년 매출 60조원, 영업이익률 15.2%",
            "content": "CATL은 2025년 연간 매출 약 3,600억 위안(약 60조원), 영업이익률 15.2%를 기록했다. LFP 배터리의 원가 경쟁력과 ESS 사업 확대가 고수익 구조를 뒷받침하고 있다.",
            "source": "CATL IR",
            "url": "https://www.catl.com/ir/annual-2025",
            "date": "2026-03-15"
        },
        {
            "category": "재무 현황",
            "sentiment": "negative",
            "title": "R&D 투자 부담 증가",
            "content": "나트륨이온, 응축형 배터리 등 다양한 차세대 기술 동시 개발로 R&D 비용이 전년 대비 35% 증가했다. 수익성 유지와 투자 확대 간 균형이 과제이다.",
            "source": "중국증권보",
            "url": "https://www.cs.com.cn/catl-rd-cost",
            "date": "2026-01-18"
        },
        # --- 공급망/생산 ---
        {
            "category": "공급망/생산",
            "sentiment": "positive",
            "title": "헝가리 공장 2026년 가동 예정",
            "content": "CATL의 첫 유럽 공장(헝가리 데브레첸)이 2026년 하반기 가동 예정이다. 연간 100GWh 규모로 BMW, 메르세데스-벤츠 등에 공급할 계획이다.",
            "source": "한국경제",
            "url": "https://www.hankyung.com/catl-hungary-2026",
            "date": "2026-02-08"
        },
        {
            "category": "공급망/생산",
            "sentiment": "negative",
            "title": "미국 시장 진입 사실상 차단",
            "content": "FEOC(해외우려기업) 규정으로 CATL 배터리를 탑재한 차량은 미국 IRA 보조금을 받을 수 없다. 북미 시장 진입이 사실상 차단된 상태이다.",
            "source": "파이낸셜타임스",
            "url": "https://www.ft.com/catl-us-market-blocked",
            "date": "2025-12-10"
        },
        # --- 시장 지위 ---
        {
            "category": "시장 지위",
            "sentiment": "positive",
            "title": "글로벌 점유율 37.9%로 압도적 1위",
            "content": "CATL은 2025년 글로벌 EV 배터리 사용량 기준 37.9%의 점유율로 압도적 1위를 유지했다. 2위 BYD(16.1%)와의 격차도 21.8%p로 압도적이다.",
            "source": "SNE리서치",
            "url": "https://www.sneresearch.com/2025-battery-share",
            "date": "2026-01-30"
        },
        {
            "category": "시장 지위",
            "sentiment": "positive",
            "title": "유럽 시장 점유율 급상승",
            "content": "CATL의 유럽 EV 배터리 점유율이 2024년 28%에서 2025년 34%로 상승했다. 폭스바겐, 스텔란티스, BMW 등 주요 OEM에 공급을 확대하고 있다.",
            "source": "Benchmark Minerals",
            "url": "https://www.benchmarkminerals.com/catl-europe",
            "date": "2025-10-22"
        },
        # --- 리스크 ---
        {
            "category": "리스크",
            "sentiment": "negative",
            "title": "지정학 리스크로 탈중국 움직임",
            "content": "미·중 갈등 심화로 유럽 완성차 업체들 사이에서 CATL 의존도를 줄이려는 움직임이 나타나고 있다. 일부 OEM은 공급선 다변화를 공식 선언했다.",
            "source": "블룸버그",
            "url": "https://www.bloomberg.com/catl-geopolitical-risk",
            "date": "2026-01-05"
        },
        {
            "category": "리스크",
            "sentiment": "negative",
            "title": "LFP 배터리 기술 범용화로 진입장벽 약화",
            "content": "LFP 배터리 기술이 범용화되면서 BYD, 궈쉬안 등 후발 업체들의 추격이 가속화되고 있다. CATL의 기술적 해자(moat)가 점차 좁아지고 있다는 분석이 나온다.",
            "source": "카이싱",
            "url": "https://www.caixin.com/lfp-commoditization",
            "date": "2026-03-05"
        },
    ],
    "summary": "CATL은 글로벌 점유율 37.9%의 압도적 1위로, ESS 매출 비중 30% 돌파와 나트륨이온 배터리 상업화로 포트폴리오 다각화를 선도하고 있다. 영업이익률 15.2%의 고수익 구조와 LFP·초급속 충전 기술력이 핵심 강점이다. 다만 미국 FEOC 규정으로 북미 시장 진입이 차단되어 있고, 지정학 리스크와 LFP 기술 범용화로 인한 진입장벽 약화가 위협 요인이다."
}
