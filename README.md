# interview-coach

Learning project: a LangGraph interview coach and study buddy with measured RAG, long-term memory and evaluation at every level

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

### Checks

One command runs every check that CI also runs — lint and formatting (ruff),
type checks (pyright) and tests (pytest):

```bash
./scripts/check.sh
```

### CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs the same command on
every pull request and on pushes to `main`
([GitHub Actions docs](https://docs.github.com/en/actions)).

### Local-only data

Two folders hold data that never leaves your machine; their contents are
git-ignored from the start:

- `data/personal/` — personal data (your notes, transcripts, answers)
- `data/study-material/` — downloaded study material (PDFs, pages to review)

## License

MIT — see [LICENSE](LICENSE).
