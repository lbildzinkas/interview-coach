"""The GLM model behind the coach, built by one small factory (ADR-0001).

Keeping construction in one function means moving to a pay-per-token key or a
local model is a configuration change, not a code change.
"""

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from interview_coach.config import Settings


def build_model(settings: Settings) -> ChatOpenAI:
    """Build the chat model the coach talks to.

    The endpoint and model name come from Settings, defaulting to the GLM
    Coding Plan's OpenAI-compatible endpoint (https://open.bigmodel.cn/);
    ChatOpenAI talks to any OpenAI-compatible endpoint via `base_url`:
    https://python.langchain.com/docs/integrations/chat/openai/

    GLM only accepts `tool_choice: "auto"` and agent runtimes add
    `parallel_tool_calls` when binding tools, so neither should reach the
    endpoint — the reason ADR-0001 exists.

    `disabled_params` covers only part of that. LangChain consults it in one
    place: `with_structured_output(method="function_calling")` passes the
    `tool_choice` and `parallel_tool_calls` it adds itself through
    `_filter_disabled_params`, which drops any key mapped to `None`. Arguments a
    caller passes to `bind_tools(...)` or `invoke(...)` are sent unfiltered; the
    field's own docstring says it "does not prevent a user from directly passed
    in the parameter during invocation". Code that binds tools must keep both
    parameters out itself. References (langchain-openai 1.6.6):
    https://github.com/langchain-ai/langchain/blob/langchain-openai%3D%3D1.6.6/libs/partners/openai/langchain_openai/chat_models/base.py#L1174-L1189
    https://github.com/langchain-ai/langchain/blob/langchain-openai%3D%3D1.6.6/libs/partners/openai/langchain_openai/chat_models/base.py#L2867-L2879
    """
    return ChatOpenAI(
        base_url=settings.base_url,
        model=settings.model_name,
        api_key=SecretStr(settings.api_key),
        disabled_params={"tool_choice": None, "parallel_tool_calls": None},
    )
