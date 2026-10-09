"""The graph runs end to end with LangChain's fake chat model — no network.

Fake chat models reference:
https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.fake_chat_models.html
"""

from collections.abc import Iterator
from typing import Any

import pytest
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatResult

from interview_coach.graph import ask, build_graph

ANSWER = "Consistent hashing spreads keys around a ring of nodes."


class RecordingFakeChatModel(GenericFakeChatModel):
    """A fake that also records every message list it is invoked with."""

    received: list[list[BaseMessage]] = []

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.received.append(list(messages))
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


@pytest.fixture
def fake_model() -> RecordingFakeChatModel:
    messages: Iterator[AIMessage] = iter([AIMessage(content=ANSWER)])
    return RecordingFakeChatModel(messages=messages)


def test_ask_returns_the_models_answer(fake_model: RecordingFakeChatModel) -> None:
    assert ask(model=fake_model, question="What is consistent hashing?") == ANSWER


def test_the_question_reaches_the_model_as_a_human_message(
    fake_model: RecordingFakeChatModel,
) -> None:
    ask(model=fake_model, question="What is consistent hashing?")
    (message,) = fake_model.received[0]
    assert message.type == "human"
    assert message.content == "What is consistent hashing?"


def test_the_graph_is_a_single_node(fake_model: RecordingFakeChatModel) -> None:
    graph = build_graph(fake_model)
    user_nodes = {name for name in graph.nodes if not name.startswith("__")}
    assert user_nodes == {"answer"}
