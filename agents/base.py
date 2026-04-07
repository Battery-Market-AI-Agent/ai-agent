"""
BaseAgent — 모든 Agent가 상속하는 베이스 클래스
- llm, tools를 공통으로 받음
- run(state) -> state 인터페이스 통일
- 각 Agent는 run()만 오버라이드
"""
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from state import ReportState

# JSON 직렬화를 깨뜨리는 제어 문자 패턴 (탭·개행·캐리지리턴 제외)
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\ufffd]")


def sanitize_text(text: str) -> str:
    """OpenAI API 요청을 깨뜨리는 제어 문자를 제거한다."""
    return _CONTROL_CHAR_RE.sub("", text)


class SanitizedLLM:
    """LLM 래퍼 — invoke 시 메시지 content를 자동 정제한다."""

    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    def invoke(self, messages, **kwargs):
        if isinstance(messages, str):
            return self._llm.invoke(sanitize_text(messages), **kwargs)
        cleaned = []
        for msg in messages:
            if isinstance(msg, str):
                cleaned.append(sanitize_text(msg))
            else:
                msg_copy = msg.model_copy()
                if isinstance(msg_copy.content, str):
                    msg_copy.content = sanitize_text(msg_copy.content)
                cleaned.append(msg_copy)
        return self._llm.invoke(cleaned, **kwargs)

    def __getattr__(self, name):
        return getattr(self._llm, name)


class BaseAgent(ABC):
    """모든 Agent가 상속하는 베이스 클래스."""

    def __init__(self, llm: BaseChatModel, tools: List[BaseTool] | None = None):
        self.llm = SanitizedLLM(llm)
        self.tools = tools or []

    @abstractmethod
    def run(self, state: ReportState) -> ReportState:
        """state를 받아서 자신의 결과를 추가한 state를 반환한다."""
        ...
