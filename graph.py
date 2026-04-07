"""
LangGraph 그래프 정의

노드: MarketAgent, SKOAgent, CATLAgent, CompareAgent, ReportAgent
엣지:
  START → MarketAgent
  MarketAgent → [SKOAgent, CATLAgent]  (fan-out, 병렬)
  [SKOAgent, CATLAgent] → CompareAgent (fan-in)
  CompareAgent → ReportAgent
  ReportAgent → END
"""
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, START, END

from state import ReportState
from agents.market_agent import MarketAgent
from agents.sko_agent import SKOAgent
from agents.catl_agent import CATLAgent
from agents.compare_agent import CompareAgent
from agents.report_agent import ReportAgent


def _make_node(agent_run, output_keys: List[str]):
    """Agent.run()을 래핑하여 변경된 키만 반환하는 노드 함수를 만든다.

    병렬 실행 시 각 노드가 전체 state를 반환하면
    LangGraph의 LastValue 채널에서 충돌이 발생한다.
    이를 방지하기 위해 각 노드가 자기 담당 키만 반환하도록 필터링한다.
    """
    def node_fn(state: ReportState) -> dict:
        result = agent_run(state)
        return {k: result[k] for k in output_keys if k in result}
    return node_fn


def build_graph(
    llm: BaseChatModel,
    vectorstore: FAISS,
    output_dir: str = "outputs",
):
    """Multi-Agent 그래프를 구성하고 컴파일된 그래프를 반환한다."""

    # 1. Agent 인스턴스 생성
    market_agent = MarketAgent(llm=llm, vectorstore=vectorstore)
    sko_agent = SKOAgent(llm=llm)
    catl_agent = CATLAgent(llm=llm)
    compare_agent = CompareAgent(llm=llm)
    report_agent = ReportAgent(llm=llm, output_dir=output_dir)

    # 2. StateGraph 생성
    graph = StateGraph(ReportState)

    # 3. 노드 추가 (각 Agent가 담당하는 state 키만 반환)
    graph.add_node("market", _make_node(market_agent.run, ["market"]))
    graph.add_node("sko", _make_node(sko_agent.run, ["sko"]))
    graph.add_node("catl", _make_node(catl_agent.run, ["catl"]))
    graph.add_node("compare", _make_node(compare_agent.run, ["comparative_swot"]))
    graph.add_node("report", _make_node(report_agent.run, ["final_report", "chart_paths"]))

    # 4. 엣지 연결
    graph.add_edge(START, "market")

    # MarketAgent → SKOAgent, CATLAgent (fan-out 병렬)
    graph.add_edge("market", "sko")
    graph.add_edge("market", "catl")

    # SKOAgent, CATLAgent → CompareAgent (fan-in)
    graph.add_edge("sko", "compare")
    graph.add_edge("catl", "compare")

    # CompareAgent → ReportAgent → END
    graph.add_edge("compare", "report")
    graph.add_edge("report", END)

    # 5. 컴파일
    return graph.compile()
