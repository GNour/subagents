"""Pure ``roster -> catalog`` transform.

No I/O, no network, no clock. Callers pass the roster list, a resolved skill
``provenance`` mapping (id -> provenance dict, produced by ``catalog.provenance``), and
the release ``source_commit``. The output is a plain ``dict`` shaped for the Aegis
``SubagentsCatalog`` contract (Aegis Plan 1a Task 2), which re-validates it strictly.

Model, tool, skill, and handoff data are advisory: they describe the fleet but confer no
runtime authority.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from catalog import CATALOG_SCHEMA_VERSION, PACKAGE_VERSION

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

# Plain (emoji-free) display names, ordered. Kept in one place so the derived
# department list is stable and independent of the README's decorated titles.
DEPARTMENT_NAMES: dict[str, str] = {
    "engineering": "Engineering",
    "quality": "Quality & Testing",
    "data-ai": "Data & AI",
    "infrastructure": "Infrastructure",
    "design": "Design",
    "product": "Product & Research",
    "meta": "Meta / Orchestration",
}


def parse_tools(tools: str) -> tuple[str, ...]:
    """Split a comma-separated advisory tool string into trimmed, non-empty names."""
    return tuple(part.strip() for part in tools.split(",") if part.strip())


def render_invocation(steps: Sequence[str]) -> str:
    """Render a role's ``when`` steps into a numbered invocation procedure."""
    return "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))


def _handoff_reason(role_id: str) -> str:
    return f"Collaborate with {role_id} when the work crosses into their specialism."


def build_departments(roster: Sequence[Mapping[str, object]]) -> list[dict[str, str]]:
    """Derive the unique department list in canonical order from the roster."""
    present = {str(entry["department"]) for entry in roster}
    unknown = present - DEPARTMENT_NAMES.keys()
    if unknown:
        raise ValueError(f"unknown department(s): {sorted(unknown)}")
    return [
        {"id": dept, "name": DEPARTMENT_NAMES[dept]}
        for dept in DEPARTMENT_NAMES
        if dept in present
    ]


def _build_role(
    entry: Mapping[str, object],
    provenance: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    skills: list[Mapping[str, object]] = []
    for skill_id, _note in entry["skills"]:  # type: ignore[union-attr]
        if skill_id not in provenance:
            raise ValueError(f"missing skill provenance: {skill_id}")
        skills.append(provenance[skill_id])
    handoffs = [
        {"role_id": target, "reason": _handoff_reason(target), "required": False}
        for target in entry["handoffs"]  # type: ignore[union-attr]
    ]
    return {
        "id": entry["name"],
        "department_id": entry["department"],
        "name": entry["name"],
        "title": entry["title"],
        "description": entry["description"],
        "expertise": list(entry["expertise"]),  # type: ignore[arg-type]
        "invocation": render_invocation(entry["when"]),  # type: ignore[arg-type]
        "standards": list(entry["standards"]),  # type: ignore[arg-type]
        "model_hint": entry["model"],
        "advisory_tools": list(parse_tools(str(entry["tools"]))),
        "skills": skills,
        "handoffs": handoffs,
    }


def build_catalog(
    roster: Sequence[Mapping[str, object]],
    *,
    source_commit: str,
    provenance: Mapping[str, Mapping[str, object]],
    package_version: str = PACKAGE_VERSION,
    catalog_schema_version: str = CATALOG_SCHEMA_VERSION,
) -> dict[str, object]:
    """Build the catalog dict from the roster and resolved skill provenance."""
    if not _COMMIT_RE.match(source_commit):
        raise ValueError("source_commit must be a 40-char lowercase git hash")

    departments = build_departments(roster)
    department_ids = {dept["id"] for dept in departments}

    roles = [_build_role(entry, provenance) for entry in roster]

    role_ids = [role["id"] for role in roles]
    if len(role_ids) != len(set(role_ids)):
        raise ValueError("duplicate role id")
    role_id_set = set(role_ids)

    for role in roles:
        if role["department_id"] not in department_ids:
            raise ValueError(f"unresolved department for role {role['id']}")
        for handoff in role["handoffs"]:  # type: ignore[union-attr]
            if handoff["role_id"] not in role_id_set:
                raise ValueError(f"unresolved handoff: {handoff['role_id']}")

    return {
        "package_version": package_version,
        "catalog_schema_version": catalog_schema_version,
        "source_commit": source_commit,
        "departments": departments,
        "roles": roles,
    }
