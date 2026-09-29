"""Local, git-ignored configuration: API key, endpoint and model name.

Values come from environment variables, with an optional `.env` file in the
working directory as the convenience source (template: `.env.example`);
a real environment variable wins over the same name in the file.
"""

import os
from dataclasses import dataclass
from pathlib import Path

ENV_FILE_NAME = ".env"
API_KEY_VAR = "INTERVIEW_COACH_API_KEY"
BASE_URL_VAR = "INTERVIEW_COACH_BASE_URL"
MODEL_VAR = "INTERVIEW_COACH_MODEL"

# Defaults for the GLM Coding Plan's OpenAI-compatible endpoint, per ADR-0001.
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/coding/paas/v4"
DEFAULT_MODEL = "glm-5.3"


class MissingApiKeyError(RuntimeError):
    """No API key is configured; the message tells the candidate how to fix it."""


@dataclass(frozen=True)
class Settings:
    """Everything the model factory needs; see `interview_coach.model`."""

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model_name: str = DEFAULT_MODEL


def load_settings(env_file: Path | None = None) -> Settings:
    """Build Settings from the environment plus an optional `.env` file."""
    file_values = _read_env_file(env_file or Path(ENV_FILE_NAME))

    def lookup(name: str) -> str | None:
        value = os.environ.get(name) or file_values.get(name)
        return value or None

    api_key = lookup(API_KEY_VAR)
    if api_key is None:
        raise MissingApiKeyError(
            f"no API key found: set {API_KEY_VAR} in .env (copy it from "
            ".env.example) or export it in your shell"
        )
    return Settings(
        api_key=api_key,
        base_url=lookup(BASE_URL_VAR) or DEFAULT_BASE_URL,
        model_name=lookup(MODEL_VAR) or DEFAULT_MODEL,
    )


def _read_env_file(path: Path) -> dict[str, str]:
    """Parse a tiny KEY=VALUE `.env` file; blanks and `#` comments are skipped.
    No dependency needed while one file of three variables is all we load.
    """
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip("'\"")
    return values
