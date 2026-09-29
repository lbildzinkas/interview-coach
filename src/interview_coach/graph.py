"""The walking-skeleton graph: one node that answers the question.

A LangGraph StateGraph is declared (state type, nodes, edges), compiled and
invoked — reference: https://langchain-ai.github.io/langgraph/concepts/graph_api/
"""

from typing import TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


class GraphState(TypedDict):
    """What flows through the graph: the question in, the answer out."""

    question: str
    answer: str


def build_graph(model: BaseChatModel) -> CompiledStateGraph:
    """Compile the one-node graph over the given chat model.

    The model is injected so tests can run the whole graph with LangChain's
    fake chat model instead of the network:
    https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.fake_chat_models.html
    """

    def answer(state: GraphState) -> dict[str, str]:
        # A plain string is accepted as one human message (LanguageModelInput).
        response = model.invoke(state["question"])
        return {"answer": response.text}

    builder = StateGraph(GraphState)
    builder.add_node("answer", answer)
    builder.add_edge(START, "answer")
    builder.add_edge("answer", END)
    return builder.compile()


def ask(model: BaseChatModel, question: str) -> str:
    """Run one question through the graph and return the answer."""
    result = build_graph(model).invoke({"question": question})
    answer: str = result["answer"]
    return answer
