# interview-coach

Learning project: a LangGraph interview coach and study buddy with measured RAG, long-term memory and evaluation at every level

Architecture diagrams of the whole planned system, marking what is built: [`docs/architecture/`](docs/architecture/README.md).

## Development

This project is managed with [uv](https://docs.astral.sh/uv/) on Python 3.13.

### Setup

```bash
git clone https://github.com/lbildzinkas/interview-coach.git
cd interview-coach
uv sync
```

`uv sync` creates a local `.venv` (git-ignored) and installs the project plus the
dev tools — [ruff](https://docs.astral.sh/ruff/), [pyright](https://microsoft.github.io/pyright/)
and [pytest](https://docs.pytest.org/) — using the committed `uv.lock` so everyone
gets the same versions.

### Asking the coach a question

`coach ask` sends one question through a one-node
[LangGraph](https://langchain-ai.github.io/langgraph/) graph that calls
GLM-5.3 on the GLM Coding Plan's OpenAI-compatible endpoint and prints the
answer. Configuration lives in environment variables, loaded from a
git-ignored `.env` file (copy [`.env.example`](.env.example) to `.env` and
fill it in; a real environment variable wins over the file):

- `INTERVIEW_COACH_API_KEY` — required, your GLM Coding Plan key
- `INTERVIEW_COACH_BASE_URL` — optional, defaults to the coding endpoint on `open.bigmodel.cn`
- `INTERVIEW_COACH_MODEL` — optional, defaults to `glm-5.3`

```bash
uv run coach ask "What is consistent hashing?"
```

Without a key, the command prints a readable error instead of a stack trace.

### Checks

One command runs the Python checks — lint and formatting (ruff), type checks
(pyright) and tests (pytest):

```bash
./scripts/check.sh
```

### CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs the same command on
every pull request and on pushes to `master`, and a second job that checks the
[architecture diagrams](docs/architecture/README.md) still render and their
committed PNGs are current
([GitHub Actions docs](https://docs.github.com/en/actions)).

### Local-only data

Two folders hold data that never leaves your machine; their contents are
git-ignored from the start:

- `data/personal/` — personal data (your notes, transcripts, answers)
- `data/study-material/` — downloaded study material (PDFs, pages to review)

## License

MIT — see [LICENSE](LICENSE).
