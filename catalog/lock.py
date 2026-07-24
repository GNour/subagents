"""Build ``config/skills.lock.json`` from the roster.

The initial (declared-advisory) lock is fully deterministic and offline:

* **local** skills are content-addressed (SHA-256 of the committed ``SKILL.md``);
* **registry / framework / bundled** skills are *declared* with a digest over a canonical
  ``{id,kind,source}`` descriptor, an ``advisory-<digest>`` version, and an
  ``advisory-unverified`` license.

A future ``lock --upgrade`` can promote any declared entry to a verified upstream pin;
that is the only path that would touch the network. ``build_lock`` itself never does.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from hashlib import sha256

from catalog.provenance import roster_skill_ids

FRAMEWORK_IDS = frozenset({"gsd"})
_ADVISORY_LICENSE = "advisory-unverified"
_FRAMEWORK_SOURCES = {
    "gsd": "framework:github.com/shoootyou/get-shit-done-multi",
}


def classify_kind(skill_id: str, local_slugs: frozenset[str] | set[str]) -> str:
    """Classify a skill id the same way ``scaffold/generate.py`` does."""
    if "/" in skill_id:
        return "registry"
    if skill_id in FRAMEWORK_IDS:
        return "framework"
    if skill_id in local_slugs:
        return "local"
    return "bundled"


def descriptor_digest(skill_id: str, kind: str, source: str) -> str:
    """Deterministic SHA-256 over the canonical declaration descriptor."""
    payload = json.dumps(
        {"id": skill_id, "kind": kind, "source": source},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def _declared_entry(skill_id: str, kind: str, source: str) -> dict[str, str]:
    digest = descriptor_digest(skill_id, kind, source)
    return {
        "source": source,
        "kind": kind,
        "version": f"advisory-{digest[:12]}",
        "sha256": digest,
        "license": _ADVISORY_LICENSE,
    }


def _local_entry(skill_id: str, content: bytes, source_commit: str, license_: str) -> dict[str, str]:
    return {
        "source": "local:GNour/subagents",
        "kind": "local",
        "version": source_commit,
        "sha256": sha256(content).hexdigest(),
        "license": license_,
    }


def build_lock(
    roster: Sequence[Mapping[str, object]],
    *,
    source_commit: str,
    local_slugs: frozenset[str] | set[str],
    local_content: Mapping[str, bytes],
    license_: str = "MIT",
) -> dict[str, object]:
    """Build the deterministic skills lock. ``local_content`` maps slug -> SKILL.md bytes."""
    skills: dict[str, dict[str, str]] = {}
    for skill_id in roster_skill_ids(roster):
        kind = classify_kind(skill_id, local_slugs)
        if kind == "local":
            if skill_id not in local_content:
                raise ValueError(f"missing local skill content: {skill_id}")
            skills[skill_id] = _local_entry(
                skill_id, local_content[skill_id], source_commit, license_
            )
        elif kind == "framework":
            source = _FRAMEWORK_SOURCES.get(skill_id, f"framework:{skill_id}")
            skills[skill_id] = _declared_entry(skill_id, kind, source)
        elif kind == "bundled":
            skills[skill_id] = _declared_entry(skill_id, kind, "bundled:claude-code")
        else:  # registry
            skills[skill_id] = _declared_entry(skill_id, kind, f"skills.sh:{skill_id}")
    return {"schema_version": 1, "skills": dict(sorted(skills.items()))}
