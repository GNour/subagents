"""Repository-context helpers: load the roster, local skill content, and release meta.

These read committed files only (no network). ``build`` / ``lock`` / ``validate`` logic
stays pure; this module is the thin I/O seam the CLI uses to feed them.
"""

from __future__ import annotations

import importlib.util
import json
from collections.abc import Mapping, Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_roster(repo_root: Path = REPO_ROOT) -> Sequence[Mapping[str, object]]:
    path = repo_root / "scaffold" / "roster.py"
    spec = importlib.util.spec_from_file_location("subagents_roster", path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot load roster from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ROSTER


def local_slugs(repo_root: Path = REPO_ROOT) -> set[str]:
    skills = repo_root / "skills"
    if not skills.is_dir():
        return set()
    return {p.name for p in skills.iterdir() if (p / "SKILL.md").is_file()}


def local_content(
    repo_root: Path = REPO_ROOT, slugs: set[str] | None = None
) -> dict[str, bytes]:
    resolved = slugs if slugs is not None else local_slugs(repo_root)
    return {
        slug: (repo_root / "skills" / slug / "SKILL.md").read_bytes()
        for slug in resolved
    }


def load_meta(repo_root: Path = REPO_ROOT) -> dict[str, object]:
    return json.loads(
        (repo_root / "config" / "catalog.meta.json").read_text(encoding="utf-8")
    )
