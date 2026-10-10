"""QASPER: questions about NLP papers, mapped to the paragraphs that answer them.

QASPER (Dasigi et al., NAACL 2021, https://arxiv.org/abs/2105.03011, CC BY 4.0) has
5,049 questions over 1,585 papers; each answer lists evidence strings copied from the
paper. The relevance unit here is the paragraph: every text evidence string is mapped
to the id of the paragraph it came from, and a paragraph counts as relevant if any
annotator chose it. Dataset card: https://huggingface.co/datasets/allenai/qasper
"""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

DATASET_REPO = "allenai/qasper"
# The Hub repo only holds a `qasper.py` loading script, which `datasets` 4.0 no longer
# runs; the Hub's automatic Parquet conversion of it lives on this revision:
# https://huggingface.co/docs/dataset-viewer/parquet
PARQUET_REVISION = "refs/convert/parquet"
VALIDATION_FILE = "qasper/validation/0000.parquet"
# Git-ignored; dataset content is never committed (ADR-0002).
CACHE_DIR = Path("data/qasper")
# Evidence that points at a table or figure starts with this marker in the dataset.
FIGURE_MARKER = "FLOAT SELECTED"

ANSWERABLE = "answerable with text evidence"
UNANSWERABLE = "unanswerable"
FIGURE_ONLY = "figure-only"
UNMAPPABLE = "unmappable"
NO_EVIDENCE = "answered without evidence"
CATEGORIES = (ANSWERABLE, UNANSWERABLE, FIGURE_ONLY, UNMAPPABLE, NO_EVIDENCE)


@dataclass(frozen=True)
class Paragraph:
    id: str
    section: str
    text: str


@dataclass(frozen=True)
class Question:
    paper_id: str
    question_id: str
    text: str
    is_answerable: bool
    evidence_paragraph_ids: frozenset[str]
    has_figure_evidence: bool
    unmapped_evidence: tuple[str, ...]

    @property
    def category(self) -> str:
        if not self.is_answerable:
            return UNANSWERABLE
        if self.evidence_paragraph_ids:
            return ANSWERABLE
        if self.has_figure_evidence:
            return FIGURE_ONLY
        if self.unmapped_evidence:
            return UNMAPPABLE
        return NO_EVIDENCE


def download_validation(cache_dir: Path = CACHE_DIR) -> Path:
    """Download the dev (validation) split once and return the local Parquet path.

    One `hf_hub_download` call plus pyarrow is lighter than `datasets.load_dataset`,
    which pulls in pandas and builds an Arrow cache we do not need:
    https://huggingface.co/docs/huggingface_hub/guides/download
    """
    return Path(
        hf_hub_download(
            DATASET_REPO,
            VALIDATION_FILE,
            repo_type="dataset",
            revision=PARQUET_REVISION,
            cache_dir=cache_dir,
        )
    )


def read_papers(path: Path) -> list[dict[str, Any]]:
    """One plain dict per paper, nested exactly as the dataset card describes."""
    return pq.read_table(path).to_pylist()


def split_paragraphs(paper: dict[str, Any]) -> list[Paragraph]:
    """Number every paragraph of the paper's full text, in reading order."""
    full_text = paper["full_text"]
    pairs = zip(full_text["section_name"], full_text["paragraphs"], strict=True)
    flat = [(section or "", text) for section, texts in pairs for text in texts]
    return [
        Paragraph(id=f"{paper['id']}:{index}", section=section, text=text)
        for index, (section, text) in enumerate(flat)
    ]


def extract_questions(paper: dict[str, Any]) -> list[Question]:
    """Map every question's evidence to paragraph ids, with the union over annotators."""
    paragraphs = split_paragraphs(paper)
    headings = _headings(paper["full_text"]["section_name"])
    qas = paper["qas"]
    pairs = zip(qas["question_id"], qas["question"], qas["answers"], strict=True)
    return [
        _map_question(paper["id"], question_id, text, answers["answer"], paragraphs, headings)
        for question_id, text, answers in pairs
    ]


def load_validation_questions(cache_dir: Path = CACHE_DIR) -> list[Question]:
    path = download_validation(cache_dir)
    return [question for paper in read_papers(path) for question in extract_questions(paper)]


def format_stats(questions: list[Question]) -> str:
    counts = Counter(question.category for question in questions)
    some_unmapped = sum(1 for question in questions if question.unmapped_evidence)
    lines = [f"QASPER dev split: {len(questions)} questions"]
    lines += [f"  {category}: {counts[category]}" for category in CATEGORIES]
    lines.append(f"questions with an evidence string that did not map: {some_unmapped}")
    return "\n".join(lines)


def _map_question(
    paper_id: str,
    question_id: str,
    text: str,
    annotations: list[dict[str, Any]],
    paragraphs: list[Paragraph],
    headings: set[str],
) -> Question:
    # Annotators often pick different evidence, and some mark the same question
    # unanswerable while others answer it. So a question is answerable if any annotator
    # answered it, and every annotator's evidence counts (union, not intersection).
    answered = [annotation for annotation in annotations if not annotation["unanswerable"]]
    evidence = [item.strip() for annotation in answered for item in annotation["evidence"]]
    ids: set[str] = set()
    unmapped: list[str] = []
    for item in evidence:
        if not item or item.startswith(FIGURE_MARKER) or item in headings:
            continue  # empty, a table or figure, or a bare section heading: dropped
        paragraph = _containing_paragraph(item, paragraphs)
        if paragraph is None:
            unmapped.append(item)
            continue
        ids.add(paragraph.id)
    return Question(
        paper_id=paper_id,
        question_id=question_id,
        text=text,
        is_answerable=bool(answered),
        evidence_paragraph_ids=frozenset(ids),
        has_figure_evidence=any(item.startswith(FIGURE_MARKER) for item in evidence),
        unmapped_evidence=tuple(unmapped),
    )


def _containing_paragraph(evidence: str, paragraphs: list[Paragraph]) -> Paragraph | None:
    """The first paragraph that holds the evidence, whole or as a fragment of it."""
    return next((paragraph for paragraph in paragraphs if evidence in paragraph.text), None)


def _headings(section_names: list[str | None]) -> set[str]:
    """Full section names ("Experiments ::: Setup") and each of their parts ("Setup")."""
    names = [name for name in section_names if name]
    return {part.strip() for name in names for part in [name, *name.split(":::")]}
