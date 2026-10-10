"""Render the architecture diagrams to PNG, or check that the committed PNGs are current.

    uv run python scripts/render_diagrams.py          # re-export every PNG
    uv run python scripts/render_diagrams.py --check  # fail on a bad, missing or stale PNG

Every `docs/architecture/*.mmd` source is rendered by the mermaid-cli version pinned in
`package.json` (install it with `npm ci`), which is the single judge of valid Mermaid:
https://github.com/mermaid-js/mermaid-cli. A SHA-256 hash of each source is recorded in
`docs/architecture/sources.sha256`, in the format `shasum -a 256 -c` reads, so a source
edited without re-exporting its PNG is caught without comparing images pixel by pixel.
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS_DIR = REPO_ROOT / "docs" / "architecture"
HASHES_FILE_NAME = "sources.sha256"
MMDC = REPO_ROOT / "node_modules" / ".bin" / "mmdc"
# Headless Chromium needs --no-sandbox on GitHub's Ubuntu runners, where unprivileged
# user namespaces are restricted: https://pptr.dev/troubleshooting
PUPPETEER_CONFIG = DIAGRAMS_DIR / "puppeteer-config.json"

# Renders one source to one PNG; returns None on success or the renderer's error text.
Renderer = Callable[[Path, Path], str | None]


def mmdc_renderer(mmdc: Path = MMDC, puppeteer_config: Path = PUPPETEER_CONFIG) -> Renderer:
    """A renderer that runs mermaid-cli: white background, scale 2 so text reads on screen.

    Options: https://github.com/mermaid-js/mermaid-cli#options
    """

    def render(source: Path, png: Path) -> str | None:
        command = [str(mmdc), "--quiet", "-i", str(source), "-o", str(png)]
        command += ["-b", "white", "-s", "2", "-p", str(puppeteer_config)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return (result.stderr or result.stdout).strip() or f"exit code {result.returncode}"
        if not png.is_file():
            return "mermaid-cli exited cleanly but wrote no PNG"
        return None

    return render


def source_hash(source: Path) -> str:
    return hashlib.sha256(source.read_bytes()).hexdigest()


def find_sources(diagrams_dir: Path) -> list[Path]:
    return sorted(diagrams_dir.glob("*.mmd"))


def read_hashes(diagrams_dir: Path) -> dict[str, str]:
    """Parse `<hash>  <file name>` lines, the format `shasum -a 256` writes."""
    hashes_file = diagrams_dir / HASHES_FILE_NAME
    if not hashes_file.is_file():
        return {}
    pairs = (line.split(maxsplit=1) for line in hashes_file.read_text().splitlines())
    return {name.strip(): digest for digest, name in pairs}


def write_hashes(diagrams_dir: Path, sources: Sequence[Path]) -> None:
    lines = [f"{source_hash(source)}  {source.name}\n" for source in sources]
    (diagrams_dir / HASHES_FILE_NAME).write_text("".join(lines))


def render_all(sources: Sequence[Path], out_dir: Path, renderer: Renderer) -> list[str]:
    """Render every source into out_dir; return one problem per diagram that fails."""
    problems: list[str] = []
    for source in sources:
        error = renderer(source, out_dir / f"{source.stem}.png")
        if error is not None:
            problems.append(f"{source.name}: does not render:\n{error}")
    return problems


def find_stale(diagrams_dir: Path) -> list[str]:
    """Problems for each source without a PNG or changed since its PNG was exported."""
    recorded = read_hashes(diagrams_dir)
    problems: list[str] = []
    for source in find_sources(diagrams_dir):
        if not source.with_suffix(".png").is_file():
            problems.append(f"{source.name}: has no PNG; run scripts/render_diagrams.py")
        elif recorded.get(source.name) != source_hash(source):
            problems.append(
                f"{source.name}: changed since its PNG was exported; run scripts/render_diagrams.py"
            )
    return problems


def check(diagrams_dir: Path, renderer: Renderer) -> list[str]:
    """Render everything into a temporary folder, then look for missing or stale PNGs."""
    sources = find_sources(diagrams_dir)
    if not sources:
        return [f"no .mmd sources found in {diagrams_dir}"]
    with tempfile.TemporaryDirectory() as out_dir:
        problems = render_all(sources, Path(out_dir), renderer)
    return problems + find_stale(diagrams_dir)


def export(diagrams_dir: Path, renderer: Renderer) -> list[str]:
    """Re-export every PNG and the hash file; change nothing if any diagram fails."""
    sources = find_sources(diagrams_dir)
    if not sources:
        return [f"no .mmd sources found in {diagrams_dir}"]
    with tempfile.TemporaryDirectory() as out_dir:
        problems = render_all(sources, Path(out_dir), renderer)
        if problems:
            return problems
        for source in sources:
            shutil.copyfile(Path(out_dir) / f"{source.stem}.png", source.with_suffix(".png"))
    write_hashes(diagrams_dir, sources)
    return []


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render docs/architecture/*.mmd to PNG, or check the committed PNGs."
    )
    parser.add_argument(
        "--check", action="store_true", help="render into a temporary folder and verify the PNGs"
    )
    args = parser.parse_args(argv)

    if not MMDC.is_file():
        print(f"render_diagrams: {MMDC} not found; run `npm ci` first", file=sys.stderr)
        return 2

    renderer = mmdc_renderer()
    problems = check(DIAGRAMS_DIR, renderer) if args.check else export(DIAGRAMS_DIR, renderer)
    for problem in problems:
        print(f"render_diagrams: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"render_diagrams: {len(find_sources(DIAGRAMS_DIR))} diagrams OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
