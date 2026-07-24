"""Load, verify, and project skill provenance from ``config/skills.lock.json``.

Pure and offline: no network, no clock. The networked resolver that *writes* the lock
lives in ``catalog.lock``. Every skill referenced by the roster must have a lock entry
with an immutable version, a content digest, and a license; anything else fails closed.

The projection returned by :func:`provenance_for_roster` contains exactly the five
fields of the Aegis ``SkillProvenance`` model (``extra="forbid"``): ``id``, ``source``,
``version``, ``sha256``, ``license``. The lock's ``kind`` field is retained only in the
lock and provenance manifest, never in the emitted catalog role.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_KINDS = frozenset({"local", "registry", "framework", "bundled"})
_MUTABLE_VERSIONS = frozenset({"", "latest", "main", "master", "head", "trunk", "*"})


class ProvenanceError(ValueError):
    """Raised when a lock file or entry violates the provenance contract."""


def verify_lock_entry(skill_id: str, entry: object) -> None:
    """Validate one lock entry, raising :class:`ProvenanceError` on any violation."""
    if not isinstance(entry, Mapping):
        raise ProvenanceError(f"{skill_id}: entry must be an object")
    if entry.get("kind") not in _KINDS:
        raise ProvenanceError(f"{skill_id}: unknown skill kind {entry.get('kind')!r}")
    version = entry.get("version")
    if not isinstance(version, str) or version.strip().lower() in _MUTABLE_VERSIONS:
        raise ProvenanceError(f"{skill_id}: mutable or missing version {version!r}")
    sha256 = entry.get("sha256")
    if not isinstance(sha256, str) or not _SHA256_RE.match(sha256):
        raise ProvenanceError(f"{skill_id}: sha256 must be 64 lowercase hex chars")
    source = entry.get("source")
    if not isinstance(source, str) or not source:
        raise ProvenanceError(f"{skill_id}: source is required")
    license_ = entry.get("license")
    if not isinstance(license_, str) or not 1 <= len(license_) <= 128:
        raise ProvenanceError(f"{skill_id}: license is required (1-128 chars)")


def load_lock(path: str | Path) -> dict[str, Mapping[str, object]]:
    """Load and verify the skills lock file, returning the ``skills`` mapping."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, Mapping) or data.get("schema_version") != 1:
        raise ProvenanceError("skills.lock.json must have schema_version 1")
    skills = data.get("skills")
    if not isinstance(skills, Mapping):
        raise ProvenanceError("skills.lock.json must contain a skills object")
    for skill_id, entry in skills.items():
        verify_lock_entry(skill_id, entry)
    return dict(skills)


def roster_skill_ids(roster: Sequence[Mapping[str, object]]) -> list[str]:
    """Return the distinct skill ids referenced by the roster, in first-seen order."""
    ordered: list[str] = []
    seen: set[str] = set()
    for entry in roster:
        for skill_id, _note in entry["skills"]:  # type: ignore[union-attr]
            if skill_id not in seen:
                seen.add(skill_id)
                ordered.append(skill_id)
    return ordered


def provenance_for_roster(
    roster: Sequence[Mapping[str, object]],
    lock: Mapping[str, Mapping[str, object]],
) -> dict[str, dict[str, str]]:
    """Project lock entries to Aegis ``SkillProvenance`` dicts for every roster skill."""
    result: dict[str, dict[str, str]] = {}
    for skill_id in roster_skill_ids(roster):
        if skill_id not in lock:
            raise ProvenanceError(f"missing skill provenance: {skill_id}")
        entry = lock[skill_id]
        result[skill_id] = {
            "id": skill_id,
            "source": str(entry["source"]),
            "version": str(entry["version"]),
            "sha256": str(entry["sha256"]),
            "license": str(entry["license"]),
        }
    return result
