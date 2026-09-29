# Interview Coach

A learning agent that helps a candidate prepare for engineering interviews: it teaches from study material and runs mock interviews that probe until the answer is deep enough.
A public, MIT-licensed Python project (LangGraph) built slowly and educationally, with measured retrieval, long-term memory and evaluation at every level.

## Agent skills

### Issue tracker

Issues are tracked in this repository's GitHub Issues, using the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Ways of working

- One idea per ticket: a pull request is reviewable in about 20-30 minutes, roughly 200-300 changed lines excluding tests and lockfiles.
- Where a code comment helps a learner, write it and link the technical reference it comes from, so the owner can study while reviewing.
- Personal data and third-party study material are never committed (see ADR 0002); study material is downloaded at setup from the sources list.
- Use the glossary's terms from `CONTEXT.md`; avoid the synonyms it lists.
