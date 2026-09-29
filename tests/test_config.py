"""Settings loading: the `.env` file, environment precedence, the missing key."""

from pathlib import Path

import pytest

from interview_coach.config import (
    API_KEY_VAR,
    BASE_URL_VAR,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    MODEL_VAR,
    MissingApiKeyError,
    load_settings,
)


@pytest.fixture
def no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in (API_KEY_VAR, BASE_URL_VAR, MODEL_VAR):
        monkeypatch.delenv(var, raising=False)


def test_reads_key_and_overrides_from_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, no_env: None
) -> None:
    (tmp_path / ".env").write_text(
        "# a comment\n"
        'INTERVIEW_COACH_API_KEY="file-key"\n'
        "INTERVIEW_COACH_MODEL=glm-5.3-flash\n"
        "IGNORED_LINE_WITHOUT_EQUALS\n"
    )
    settings = load_settings(env_file=tmp_path / ".env")
    assert settings.api_key == "file-key"
    assert settings.model_name == "glm-5.3-flash"
    assert settings.base_url == DEFAULT_BASE_URL


def test_environment_variable_wins_over_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, no_env: None
) -> None:
    (tmp_path / ".env").write_text(f"{API_KEY_VAR}=file-key\n")
    monkeypatch.setenv(API_KEY_VAR, "os-key")
    assert load_settings(env_file=tmp_path / ".env").api_key == "os-key"


def test_defaults_when_only_the_key_is_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, no_env: None
) -> None:
    monkeypatch.setenv(API_KEY_VAR, "os-key")
    settings = load_settings(env_file=tmp_path / "missing.env")
    assert settings == type(settings)("os-key", DEFAULT_BASE_URL, DEFAULT_MODEL)


def test_missing_key_raises_a_readable_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, no_env: None
) -> None:
    monkeypatch.chdir(tmp_path)  # no .env anywhere
    with pytest.raises(MissingApiKeyError, match=API_KEY_VAR):
        load_settings()
