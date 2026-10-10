"""Tests for scripts/render_diagrams.py: the check fails on a diagram that does not
render, a missing PNG and a stale PNG, without needing Node or a browser.
"""

import stat
from pathlib import Path

import pytest

from render_diagrams import (
    DIAGRAMS_DIR,
    check,
    export,
    find_sources,
    find_stale,
    mmdc_renderer,
    read_hashes,
)

GOOD_SOURCE = 'flowchart LR\n    a["A"] --> b["B"]\n'
BROKEN_SOURCE = 'flowchart LR\n    a["A --> b["B"]\n'
PARSE_ERROR = "Error: Parse error on line 2"


def fake_renderer(source: Path, png: Path) -> str | None:
    """Stands in for mermaid-cli: fails like it on an unclosed quote, else writes a PNG."""
    if source.read_text().count('"') % 2:
        return PARSE_ERROR
    png.write_bytes(b"\x89PNG fake")
    return None


@pytest.fixture
def diagrams_dir(tmp_path: Path) -> Path:
    """A folder with two good diagrams, exported so their PNGs and hashes are current."""
    (tmp_path / "01-first.mmd").write_text(GOOD_SOURCE)
    (tmp_path / "02-second.mmd").write_text(GOOD_SOURCE.replace("B", "C"))
    assert export(tmp_path, fake_renderer) == []
    return tmp_path


def test_export_writes_a_png_and_a_hash_per_source(diagrams_dir: Path) -> None:
    assert (diagrams_dir / "01-first.png").is_file()
    assert (diagrams_dir / "02-second.png").is_file()
    assert set(read_hashes(diagrams_dir)) == {"01-first.mmd", "02-second.mmd"}


def test_check_passes_when_every_png_is_current(diagrams_dir: Path) -> None:
    assert check(diagrams_dir, fake_renderer) == []


def test_check_fails_on_a_diagram_that_does_not_render(diagrams_dir: Path) -> None:
    (diagrams_dir / "02-second.mmd").write_text(BROKEN_SOURCE)

    problems = check(diagrams_dir, fake_renderer)

    assert any("02-second.mmd: does not render" in p and PARSE_ERROR in p for p in problems)


def test_check_fails_on_a_missing_png(diagrams_dir: Path) -> None:
    (diagrams_dir / "01-first.png").unlink()

    assert check(diagrams_dir, fake_renderer) == [
        "01-first.mmd: has no PNG; run scripts/render_diagrams.py"
    ]


def test_check_fails_on_a_stale_png(diagrams_dir: Path) -> None:
    (diagrams_dir / "01-first.mmd").write_text(GOOD_SOURCE.replace("A", "Z"))

    assert check(diagrams_dir, fake_renderer) == [
        "01-first.mmd: changed since its PNG was exported; run scripts/render_diagrams.py"
    ]


def test_check_fails_when_there_are_no_sources(tmp_path: Path) -> None:
    assert check(tmp_path, fake_renderer) == [f"no .mmd sources found in {tmp_path}"]


def test_export_changes_nothing_when_a_diagram_fails(diagrams_dir: Path) -> None:
    png_before = (diagrams_dir / "01-first.png").read_bytes()
    hashes_before = read_hashes(diagrams_dir)
    (diagrams_dir / "01-first.mmd").write_text(GOOD_SOURCE.replace("A", "Z"))
    (diagrams_dir / "02-second.mmd").write_text(BROKEN_SOURCE)

    assert export(diagrams_dir, fake_renderer) != []
    assert (diagrams_dir / "01-first.png").read_bytes() == png_before
    assert read_hashes(diagrams_dir) == hashes_before


def write_fake_mmdc(path: Path, script_body: str) -> Path:
    """A shell script standing in for node_modules/.bin/mmdc; `$5` is the -o path."""
    path.write_text(f"#!/bin/sh\n{script_body}\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_mmdc_renderer_returns_the_renderer_error(tmp_path: Path) -> None:
    mmdc = write_fake_mmdc(tmp_path / "mmdc", f'echo "{PARSE_ERROR}" >&2\nexit 1')
    render = mmdc_renderer(mmdc, tmp_path / "puppeteer-config.json")

    assert render(tmp_path / "x.mmd", tmp_path / "x.png") == PARSE_ERROR


def test_mmdc_renderer_returns_none_when_the_png_is_written(tmp_path: Path) -> None:
    mmdc = write_fake_mmdc(tmp_path / "mmdc", 'touch "$5"')
    render = mmdc_renderer(mmdc, tmp_path / "puppeteer-config.json")

    assert render(tmp_path / "x.mmd", tmp_path / "x.png") is None


def test_committed_diagrams_have_current_pngs() -> None:
    """The committed sources each have a PNG exported from their current text."""
    assert len(find_sources(DIAGRAMS_DIR)) == 6
    assert find_stale(DIAGRAMS_DIR) == []
