"""The model factory builds the GLM coding-endpoint client (ADR-0001)."""

from interview_coach.config import DEFAULT_BASE_URL, DEFAULT_MODEL, Settings
from interview_coach.model import build_model


def test_factory_targets_the_glm_coding_endpoint() -> None:
    model = build_model(Settings(api_key="test-key"))
    assert model.openai_api_base == DEFAULT_BASE_URL
    assert model.openai_api_base == "https://open.bigmodel.cn/api/coding/paas/v4"
    assert model.model_name == DEFAULT_MODEL
    assert model.model_name == "glm-5.3"


def test_factory_disables_tool_choice_and_parallel_tool_calls() -> None:
    model = build_model(Settings(api_key="test-key"))
    assert model.disabled_params == {"tool_choice": None, "parallel_tool_calls": None}


def test_factory_honours_configuration_overrides() -> None:
    model = build_model(
        Settings(api_key="test-key", base_url="https://example.test/v1", model_name="glm-5.3-flash")
    )
    assert model.openai_api_base == "https://example.test/v1"
    assert model.model_name == "glm-5.3-flash"
