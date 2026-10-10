"""Heading-aware chunking on small hand-made markdown files; no network, no model."""

from pathlib import Path

import pytest
import yaml

from interview_coach.chunking import MAX_TOKENS, Chunk, chunk_file, count_tokens
from interview_coach.cli import main
from interview_coach.config import API_KEY_VAR
from interview_coach.study_material import Source

COMMIT = "0123456789abcdef0123456789abcdef01234567"
SOURCE = Source(
    name="fake-primer",
    repository="https://example.com/fake",
    commit=COMMIT,
    licence="MIT",
    local_only=False,
    download_url="https://example.com/{commit}/{path}",
    files=["README.md", "LICENSE"],
)

# A paragraph of 60 tokens: long enough to stand alone as a chunk.
PARAGRAPH = " ".join(f"word{index}" for index in range(60))

NESTED = f"""# Database

## Replication

{PARAGRAPH}

### Master-slave

The master serves reads and writes; replicas serve only reads. {PARAGRAPH}

```python
# A comment in code is not a heading
replicas = 2
```

#### Disadvantages

A short note.

### Source(s) and further reading

* [Replication](https://example.com/replication)

## Federation

{PARAGRAPH}

##### Source(s) and further reading: sharding

* [Sharding](https://example.com/sharding)
"""

MDX = f"""---
id: behavioral-interview
title: 'Behavioral interviews'
---

<head>
  <meta property="og:image" content="https://example.com/social.png" />
</head>

import InDocAd from './\\_components/InDocAd';

## What are behavioral interviews

{PARAGRAPH}

<InDocAd />

<div className="text--center">
  <img alt="A rubric"
    src={{require('@site/static/img/rubric.jpg').default}} />
</div>

See <https://example.com/autolink> for more.
"""

OVERSIZED = "## Huge\n\n" + "\n\n".join([PARAGRAPH] * 30)


def chunks_by_path(markdown: str) -> dict[str, Chunk]:
    return {
        " > ".join(chunk.heading_path): chunk for chunk in chunk_file(SOURCE, "README.md", markdown)
    }


def test_nested_headings_give_each_chunk_its_heading_path_as_prefix() -> None:
    chunks = chunks_by_path(NESTED)
    assert list(chunks) == [
        "Database > Replication",
        "Database > Replication > Master-slave",
        "Database > Federation",
    ]
    master_slave = chunks["Database > Replication > Master-slave"]
    assert master_slave.text.startswith("Database > Replication > Master-slave\n\nThe master")
    assert master_slave.source == "fake-primer"
    assert master_slave.url == f"https://example.com/{COMMIT}/README.md"


def test_a_code_comment_is_not_mistaken_for_a_heading() -> None:
    master_slave = chunks_by_path(NESTED)["Database > Replication > Master-slave"]
    assert "# A comment in code is not a heading" in master_slave.text


def test_a_tiny_section_is_merged_into_its_parent() -> None:
    master_slave = chunks_by_path(NESTED)["Database > Replication > Master-slave"].text
    # The empty "Database" section is dropped; "Disadvantages" folds into its parent.
    assert master_slave.endswith("#### Disadvantages\n\nA short note.")


def test_link_list_sections_are_dropped_at_any_heading_level() -> None:
    text = "\n".join(chunk.text for chunk in chunk_file(SOURCE, "README.md", NESTED))
    assert "Source(s)" not in text
    assert "example.com/replication" not in text
    assert "example.com/sharding" not in text


def test_mdx_components_and_front_matter_are_stripped() -> None:
    [chunk] = chunk_file(SOURCE, "README.md", MDX)
    assert chunk.heading_path == ("What are behavioral interviews",)
    for leftover in ("title:", "<head>", "og:image", "import", "InDocAd", "<div", "<img", "rubric"):
        assert leftover not in chunk.text
    assert "<https://example.com/autolink>" in chunk.text


def test_an_oversized_section_is_split_under_the_cap() -> None:
    chunks = chunk_file(SOURCE, "README.md", OVERSIZED)
    assert len(chunks) > 1
    assert all(count_tokens(chunk.text) <= MAX_TOKENS for chunk in chunks)
    assert all(chunk.text.startswith("Huge\n\n") for chunk in chunks)
    # Nothing is lost or duplicated by the split.
    words = [word for chunk in chunks for word in chunk.text.split()[1:]]
    assert words == OVERSIZED.split()[2:]


def test_ids_are_stable_across_runs_and_derived_from_the_pinned_source() -> None:
    first = [chunk.id for chunk in chunk_file(SOURCE, "README.md", NESTED)]
    second = [chunk.id for chunk in chunk_file(SOURCE, "README.md", NESTED)]
    assert first == second
    assert first == [f"fake-primer@0123456:README.md#{index}" for index in range(3)]


def test_coach_chunks_stats_prints_counts_per_source_without_an_api_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(API_KEY_VAR, raising=False)
    sources = {"sources": [SOURCE.model_dump()]}
    Path("sources.yaml").write_text(yaml.safe_dump(sources))
    folder = tmp_path / "data/study-material/fake-primer"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text(NESTED)

    assert main(["chunks", "stats"]) == 0
    assert capsys.readouterr().out.startswith("fake-primer: 3 chunks, tokens min ")


def test_coach_chunks_stats_before_setup_prints_a_readable_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    Path("sources.yaml").write_text(yaml.safe_dump({"sources": [SOURCE.model_dump()]}))

    assert main(["chunks", "stats"]) == 1
    assert "run `coach setup` first" in capsys.readouterr().err
