"""Fail-closed structural validation of a compiled catalog.

Mirrors the published JSON Schema (``catalog/schema/catalog.schema.json``) and the Aegis
``SubagentsCatalog`` contract using only the standard library. Every violation raises
:class:`CatalogValidationError`; nothing is silently stripped or coerced.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_MUTABLE_VERSIONS = frozenset({"", "latest", "main", "master", "head", "trunk", "*"})

_TOP_FIELDS = {
    "package_version",
    "catalog_schema_version",
    "source_commit",
    "departments",
    "roles",
}
_DEPT_FIELDS = {"id", "name"}
_ROLE_FIELDS = {
    "id",
    "department_id",
    "name",
    "title",
    "description",
    "expertise",
    "invocation",
    "standards",
    "model_hint",
    "advisory_tools",
    "skills",
    "handoffs",
}
_SKILL_FIELDS = {"id", "source", "version", "sha256", "license"}
_HANDOFF_FIELDS = {"role_id", "reason", "required"}


class CatalogValidationError(ValueError):
    """Raised when a catalog violates the structural contract."""


def _require_exact_keys(obj: object, expected: set[str], where: str) -> Mapping[str, object]:
    if not isinstance(obj, Mapping):
        raise CatalogValidationError(f"{where}: expected an object")
    keys = set(obj)
    unknown = keys - expected
    if unknown:
        raise CatalogValidationError(f"{where}: unknown field(s) {sorted(unknown)}")
    missing = expected - keys
    if missing:
        raise CatalogValidationError(f"{where}: missing field(s) {sorted(missing)}")
    return obj


def _require_str_list(value: object, where: str) -> None:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise CatalogValidationError(f"{where}: expected a list of strings")


def _validate_skill(skill: object, where: str) -> None:
    obj = _require_exact_keys(skill, _SKILL_FIELDS, where)
    if not isinstance(obj["id"], str) or not obj["id"]:
        raise CatalogValidationError(f"{where}: id is required")
    if not isinstance(obj["source"], str) or not obj["source"]:
        raise CatalogValidationError(f"{where}: source is required")
    version = obj["version"]
    if not isinstance(version, str) or version.strip().lower() in _MUTABLE_VERSIONS:
        raise CatalogValidationError(f"{where}: mutable or missing version")
    if not isinstance(obj["sha256"], str) or not _SHA256_RE.match(obj["sha256"]):
        raise CatalogValidationError(f"{where}: sha256 must be 64 lowercase hex chars")
    license_ = obj["license"]
    if not isinstance(license_, str) or not 1 <= len(license_) <= 128:
        raise CatalogValidationError(f"{where}: license is required (1-128 chars)")


def _validate_role(role: object, where: str) -> Mapping[str, object]:
    obj = _require_exact_keys(role, _ROLE_FIELDS, where)
    for field in ("id", "department_id", "name", "title", "description", "invocation", "model_hint"):
        if not isinstance(obj[field], str) or not obj[field]:
            raise CatalogValidationError(f"{where}: {field} must be a non-empty string")
    _require_str_list(obj["expertise"], f"{where}.expertise")
    _require_str_list(obj["standards"], f"{where}.standards")
    _require_str_list(obj["advisory_tools"], f"{where}.advisory_tools")
    if not isinstance(obj["skills"], list):
        raise CatalogValidationError(f"{where}.skills: expected a list")
    for i, skill in enumerate(obj["skills"]):
        _validate_skill(skill, f"{where}.skills[{i}]")
    if not isinstance(obj["handoffs"], list):
        raise CatalogValidationError(f"{where}.handoffs: expected a list")
    return obj


def _detect_required_cycle(roles: Sequence[Mapping[str, object]]) -> None:
    graph = {
        str(role["id"]): [
            str(h["role_id"])
            for h in role["handoffs"]  # type: ignore[union-attr]
            if h.get("required") is True
        ]
        for role in roles
    }
    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(graph, WHITE)

    def visit(node: str) -> None:
        color[node] = GRAY
        for nxt in graph.get(node, ()):
            if color.get(nxt) == GRAY:
                raise CatalogValidationError(f"cyclic required handoff via {node} -> {nxt}")
            if color.get(nxt) == WHITE:
                visit(nxt)
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            visit(node)


def validate_catalog(catalog: object, *, expected_schema_version: str | None = None) -> None:
    """Validate a compiled catalog dict, raising on the first violation."""
    obj = _require_exact_keys(catalog, _TOP_FIELDS, "catalog")

    if not isinstance(obj["source_commit"], str) or not _COMMIT_RE.match(obj["source_commit"]):
        raise CatalogValidationError("catalog.source_commit must be a 40-char git hash")
    schema_version = obj["catalog_schema_version"]
    if not isinstance(schema_version, str) or not schema_version.isdigit():
        raise CatalogValidationError("catalog.catalog_schema_version must be a digit string")
    if expected_schema_version is not None and schema_version != expected_schema_version:
        raise CatalogValidationError(
            f"catalog schema {schema_version} != expected {expected_schema_version}"
        )

    departments = obj["departments"]
    if not isinstance(departments, list) or not departments:
        raise CatalogValidationError("catalog.departments must be a non-empty list")
    dept_ids: list[str] = []
    for i, dept in enumerate(departments):
        entry = _require_exact_keys(dept, _DEPT_FIELDS, f"departments[{i}]")
        if not isinstance(entry["id"], str) or not isinstance(entry["name"], str):
            raise CatalogValidationError(f"departments[{i}]: id and name must be strings")
        dept_ids.append(entry["id"])
    if len(dept_ids) != len(set(dept_ids)):
        raise CatalogValidationError("duplicate department id")

    roles = obj["roles"]
    if not isinstance(roles, list) or not roles:
        raise CatalogValidationError("catalog.roles must be a non-empty list")
    validated = [_validate_role(role, f"roles[{i}]") for i, role in enumerate(roles)]

    role_ids = [str(role["id"]) for role in validated]
    if len(role_ids) != len(set(role_ids)):
        raise CatalogValidationError("duplicate role id")
    role_id_set = set(role_ids)
    dept_id_set = set(dept_ids)

    for role in validated:
        if role["department_id"] not in dept_id_set:
            raise CatalogValidationError(f"unresolved department for role {role['id']}")
        for j, handoff in enumerate(role["handoffs"]):  # type: ignore[arg-type]
            entry = _require_exact_keys(
                handoff, _HANDOFF_FIELDS, f"role {role['id']} handoff[{j}]"
            )
            if entry["role_id"] not in role_id_set:
                raise CatalogValidationError(f"unresolved handoff: {entry['role_id']}")
            if not isinstance(entry["reason"], str) or not entry["reason"]:
                raise CatalogValidationError(f"role {role['id']} handoff[{j}]: reason required")
            if not isinstance(entry["required"], bool):
                raise CatalogValidationError(
                    f"role {role['id']} handoff[{j}]: required must be a boolean"
                )

    _detect_required_cycle(validated)
