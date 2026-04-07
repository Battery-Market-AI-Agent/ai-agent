"""
LangGraph 그래프 정의

# LangGraph로 그래프 정의
# 노드: MarketAgent, SKOAgent, CATLAgent, CompareAgent, ReportAgent
# 엣지:
#   START → MarketAgent
#   MarketAgent → [SKOAgent, CATLAgent]  (fan-out, 병렬)
#   [SKOAgent, CATLAgent] → CompareAgent (fan-in)
#   CompareAgent → ReportAgent
#   ReportAgent → END
"""
from langgraph.graph import StateGraph, START, END

from state import ReportState
from agents.market_agent import MarketAgent
from agents.sko_agent import SKOAgent
from agents.catl_agent import CATLAgent
from agents.compare_agent import CompareAgent
from agents.report_agent import ReportAgent


def build_graph(llm, rag_tools=None, web_tools=None) -> StateGraph:
    """Multi-Agent 그래프를 구성하고 반환한다."""
    # TODO: 구현
    # 1. 각 Agent 인스턴스 생성
    # 2. StateGraph(ReportState) 생성
    # 3. 노드 추가: market, sko, catl, compare, report
    # 4. 엣지 연결:
    #    START → market
    #    market → [sko, catl]  (fan-out, 병렬)
    #    [sko, catl] → compare (fan-in)
    #    compare → report
    #    report → END
    # 5. 컴파일된 그래프 반환
    ...
