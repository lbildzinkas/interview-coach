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

    `disabled_params` drops request parameters before they are sent; a value
    of `None` always removes the parameter (see `BaseChatOpenAI.disabled_params`
    in langchain-openai). GLM only accepts `tool_choice: "auto"`, and agent
    runtimes add `parallel_tool_calls` when binding tools, so neither may ever
    reach the endpoint — the reason ADR-0001 exists.
    """
    return ChatOpenAI(
        base_url=settings.base_url,
        model=settings.model_name,
        api_key=SecretStr(settings.api_key),
        disabled_params={"tool_choice": None, "parallel_tool_calls": None},
    )
