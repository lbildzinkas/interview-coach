"""The `coach` command-line interface: `coach ask "<question>"`."""

import argparse
import sys
from collections.abc import Callable, Sequence

from langchain_core.language_models.chat_models import BaseChatModel

from interview_coach.config import MissingApiKeyError, Settings, load_settings
from interview_coach.graph import ask
from interview_coach.model import build_model

# Injected in tests so the CLI runs against a fake chat model, not the network.
ModelFactory = Callable[[Settings], BaseChatModel]


def main(argv: Sequence[str] | None = None, model_factory: ModelFactory = build_model) -> int:
    """Run the CLI and return the process exit code."""
    parser = argparse.ArgumentParser(prog="coach", description="The interview coach.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    ask_parser = subcommands.add_parser("ask", help="ask one question and print the answer")
    ask_parser.add_argument("question", help="the question to ask, in quotes")
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except MissingApiKeyError as error:
        # A readable error, not a stack trace (issue #5).
        print(f"coach: error: {error}", file=sys.stderr)
        return 1

    model = model_factory(settings)
    print(ask(model=model, question=args.question))
    return 0


if __name__ == "__main__":
    sys.exit(main())
