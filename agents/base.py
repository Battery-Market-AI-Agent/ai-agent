"""
BaseAgent — 모든 Agent가 상속하는 베이스 클래스
- llm, tools를 공통으로 받음
- run(state) -> state 인터페이스 통일
- 각 Agent는 run()만 오버라이드
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from state import ReportState


class BaseAgent(ABC):
    """모든 Agent가 상속하는 베이스 클래스."""

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool] | None = None):
        self.llm = llm
        self.tools = tools or []

    @abstractmethod
    def run(self, state: ReportState) -> ReportState:
        """state를 받아서 자신의 결과를 추가한 state를 반환한다."""
        ...
