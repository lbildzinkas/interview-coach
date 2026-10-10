"""Heading-aware chunking of the study material, and `coach chunks stats`.

Each markdown file is split at its headings rather than into fixed windows, so a chunk
is one topic and carries its heading path ("Database > Replication > Master-slave") as
metadata and as a text prefix: a section cut out of its page still says what it is
about, both to keyword search and to the embedding model. Sections over the cap are
split again recursively, the way LangChain's RecursiveCharacterTextSplitter does
(https://python.langchain.com/docs/how_to/recursive_text_splitter/). There is no
overlap: Chroma's chunking study (https://research.trychroma.com/evaluating-chunking)
found a ~200-token recursive split without overlap consistently strong, and OpenAI's
800-token default with 400 tokens of overlap below average.

Chunk ids come from the pinned source and the chunk's position, never from a random
uuid: an evaluation set records which chunk ids answer each question, so the same
pinned text must give the same ids on every run or the labels would point at nothing.
"""

import re
import statistics
from dataclasses import dataclass
from pathlib import Path

from interview_coach.study_material import DATA_DIR, SOURCES_FILE, Source, load_sources

# bge-small-en-v1.5, the embedding model in ADR 0003, reads at most 512 tokens:
# https://huggingface.co/BAAI/bge-small-en-v1.5
MAX_TOKENS = 512
# A section shorter than this says too little alone and is merged into its parent.
MIN_TOKENS = 50
# Split at h1-h4; h5 and h6 stay inside their section's text.
MAX_SPLIT_LEVEL = 4
# The Primer closes most topics with a list of links, at any heading level and sometimes
# with a suffix ("Source(s) and further reading: replication"); links are not teaching text.
LINK_LIST_HEADING = "Source(s) and further reading"
# Recursive split: paragraphs first, then lines, then words.
SEPARATORS = ("\n\n", "\n", " ")
PATH_SEPARATOR = " > "

# ATX headings: https://spec.commonmark.org/0.31.2/#atx-headings
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# Fenced code blocks: https://spec.commonmark.org/0.31.2/#fenced-code-blocks
FENCE = re.compile(r"^\s*(```|~~~)")
CODE_BLOCK = re.compile(r"(^\s*(?:```|~~~).*?^\s*(?:```|~~~)[^\n]*$)", re.MULTILINE | re.DOTALL)
# Docusaurus pages are MDX (https://docusaurus.io/docs/markdown-features/react): YAML
# front matter, `import` lines and JSX or HTML tags such as <InDocAd />, none of it text.
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
MDX_IMPORT = re.compile(r"^(import|export)\s.*$", re.MULTILINE)
HEAD_BLOCK = re.compile(r"<head>.*?</head>", re.DOTALL)
# A tag name then attributes, across lines; `<https://...>` autolinks do not match.
TAG = re.compile(r"</?[A-Za-z][\w.-]*(?:\s[^<>]*)?/?>")
# A rough stand-in for a subword tokenizer: each word and each punctuation mark is a
# token. No model is loaded, so counts are close to, not equal to, the embedder's.
TOKEN = re.compile(r"\w+|[^\w\s]")


@dataclass(frozen=True)
class Chunk:
    id: str
    source: str
    url: str
    heading_path: tuple[str, ...]
    # The heading path, a blank line, then the section text.
    text: str


@dataclass(frozen=True)
class _Section:
    path: tuple[str, ...]
    level: int
    body: str


def count_tokens(text: str) -> int:
    return len(TOKEN.findall(text))


def chunk_file(source: Source, path: str, markdown: str) -> list[Chunk]:
    """Split one file of a source into chunks, numbered in reading order."""
    sections = _merge_tiny(_sections(_strip_mdx(markdown)))
    pieces = [
        (section.path, piece)
        for section in sections
        for piece in _split(section.body, MAX_TOKENS - count_tokens(_prefix(section.path)))
    ]
    # e.g. system-design-primer-text@ae9bbd7:README.md#42
    stem = f"{source.name}@{source.commit[:7]}:{path}"
    return [
        Chunk(
            id=f"{stem}#{index}",
            source=source.name,
            url=source.url_for(path),
            heading_path=heading_path,
            text=_prefix(heading_path) + text,
        )
        for index, (heading_path, text) in enumerate(pieces)
    ]


def chunk_source(source: Source, data_dir: Path = DATA_DIR) -> list[Chunk]:
    """Chunk every markdown file of a downloaded source; licence files are skipped."""
    paths = [path for path in source.files if path.endswith(".md")]
    folder = data_dir / source.name
    if paths and not folder.is_dir():
        raise FileNotFoundError(f"{folder} is missing; run `coach setup` first")
    return [
        chunk
        for path in paths
        for chunk in chunk_file(source, path, (folder / path).read_text(encoding="utf-8"))
    ]


def format_stats(chunks_by_source: dict[str, list[Chunk]]) -> str:
    lines = []
    for name, chunks in chunks_by_source.items():
        sizes = [count_tokens(chunk.text) for chunk in chunks]
        lines.append(
            f"{name}: {len(chunks)} chunks, tokens min {min(sizes)}"
            f" / median {statistics.median(sizes):g} / max {max(sizes)}"
        )
    return "\n".join(lines)


def run_stats(sources_file: Path = SOURCES_FILE, data_dir: Path = DATA_DIR) -> str:
    sources = load_sources(sources_file).sources
    chunks = {source.name: chunk_source(source, data_dir) for source in sources}
    return format_stats({name: found for name, found in chunks.items() if found})


def _strip_mdx(markdown: str) -> str:
    text = FRONT_MATTER.sub("", markdown.replace("\r\n", "\n"))
    # Only prose is cleaned: code blocks keep their `<` and `import` lines.
    parts = CODE_BLOCK.split(text)
    for index in range(0, len(parts), 2):
        prose = HEAD_BLOCK.sub("", parts[index])
        parts[index] = TAG.sub("", MDX_IMPORT.sub("", prose))
    return "".join(parts)


def _sections(markdown: str) -> list[_Section]:
    """One section per h1-h4 heading, with its heading path; link lists are dropped."""
    sections: list[_Section] = []
    stack: list[tuple[int, str]] = []
    body: list[str] = []
    skip_level: int | None = None
    in_fence = False
    for line in markdown.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
        heading = None if in_fence else HEADING.match(line)
        level = len(heading.group(1)) if heading else 0
        # A dropped link list runs until the next heading at its own level or above.
        if skip_level is not None:
            if heading is None or level > skip_level:
                continue
            skip_level = None
        if heading and heading.group(2).startswith(LINK_LIST_HEADING):
            skip_level = level
            continue
        if heading is None or level > MAX_SPLIT_LEVEL:
            body.append(line)
            continue
        sections.append(_section(stack, body))
        stack = [(depth, title) for depth, title in stack if depth < level]
        stack.append((level, heading.group(2)))
        body = []
    sections.append(_section(stack, body))
    return sections


def _section(stack: list[tuple[int, str]], body: list[str]) -> _Section:
    level = stack[-1][0] if stack else 0
    return _Section(tuple(title for _, title in stack), level, "\n".join(body).strip())


def _merge_tiny(sections: list[_Section]) -> list[_Section]:
    """Fold each section under MIN_TOKENS into its parent, deepest and last first.

    Walking backwards lets a merged child make its parent big enough to stand alone,
    and inserting at the front keeps the children in reading order.
    """
    merged: list[list[str]] = [[] for _ in sections]
    kept = [True] * len(sections)
    for index in reversed(range(len(sections))):
        section = sections[index]
        text = "\n\n".join(part for part in [section.body, *merged[index]] if part)
        parent = _parent(sections, index)
        if not text or (count_tokens(text) < MIN_TOKENS and parent is not None):
            kept[index] = False
            if text and parent is not None:
                heading = "#" * section.level + " " + section.path[-1]
                merged[parent].insert(0, f"{heading}\n\n{text}")
            continue
        merged[index] = [text]
    return [
        _Section(section.path, section.level, merged[index][0])
        for index, section in enumerate(sections)
        if kept[index]
    ]


def _parent(sections: list[_Section], index: int) -> int | None:
    path = sections[index].path
    if not path:
        return None
    return next((i for i in reversed(range(index)) if sections[i].path == path[:-1]), None)


def _split(text: str, budget: int, separators: tuple[str, ...] = SEPARATORS) -> list[str]:
    """Pack pieces greedily up to `budget` tokens; an oversized piece is split again."""
    if count_tokens(text) <= budget or not separators:
        return [text]
    separator, rest = separators[0], separators[1:]
    pieces: list[str] = []
    current = ""
    for part in text.split(separator):
        candidate = f"{current}{separator}{part}" if current else part
        if count_tokens(candidate) <= budget:
            current = candidate
            continue
        smaller = _split(part, budget, rest)
        # Pack the text so far with the oversized part's first piece when both fit.
        head = f"{current}{separator}{smaller[0]}" if current else smaller[0]
        if count_tokens(head) <= budget:
            smaller[0] = head
        elif current:
            pieces.append(current)
        pieces.extend(smaller[:-1])
        current = smaller[-1]
    pieces.append(current)
    return [piece.strip() for piece in pieces if piece.strip()]


def _prefix(path: tuple[str, ...]) -> str:
    return PATH_SEPARATOR.join(path) + "\n\n" if path else ""
