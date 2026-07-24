"""Tests for the pure roster -> catalog transform (Task 2)."""

import unittest

from catalog.build import build_catalog, parse_tools, render_invocation

ROSTER = [
    {
        "name": "alpha",
        "department": "engineering",
        "model": "opus",
        "tools": "Read, Bash, Skill",
        "title": "Alpha Lead",
        "description": "Leads alpha work.",
        "expertise": ["design", "delivery"],
        "skills": [("owner/skill-a", "does a")],
        "when": ["clarify the goal", "decompose the work"],
        "standards": ["every task has an owner"],
        "handoffs": ["beta"],
    },
    {
        "name": "beta",
        "department": "quality",
        "model": "sonnet",
        "tools": "Read, Grep",
        "title": "Beta QA",
        "description": "Verifies beta work.",
        "expertise": ["testing"],
        "skills": [("local-skill", "helps test")],
        "when": ["write the plan"],
        "standards": ["tests are deterministic"],
        "handoffs": [],
    },
]

PROV = {
    "owner/skill-a": {
        "id": "owner/skill-a",
        "source": "registry:github.com/owner/skill-a",
        "kind": "registry",
        "version": "a" * 40,
        "sha256": "b" * 64,
        "license": "MIT",
    },
    "local-skill": {
        "id": "local-skill",
        "source": "local:GNour/subagents",
        "kind": "local",
        "version": "c" * 40,
        "sha256": "d" * 64,
        "license": "MIT",
    },
}

COMMIT = "e" * 40


def catalog():
    return build_catalog(ROSTER, source_commit=COMMIT, provenance=PROV)


class HelperTest(unittest.TestCase):
    def test_parse_tools_splits_and_trims(self) -> None:
        self.assertEqual(parse_tools("Read, Bash, Skill"), ("Read", "Bash", "Skill"))
        self.assertEqual(parse_tools(" Read ,,Grep "), ("Read", "Grep"))

    def test_render_invocation_numbers_steps(self) -> None:
        self.assertEqual(
            render_invocation(["clarify the goal", "decompose the work"]),
            "1. clarify the goal\n2. decompose the work",
        )


class CatalogShapeTest(unittest.TestCase):
    def test_top_level_fields(self) -> None:
        cat = catalog()
        self.assertEqual(cat["source_commit"], COMMIT)
        self.assertEqual(cat["catalog_schema_version"], "1")
        self.assertRegex(
            cat["package_version"], r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$"
        )

    def test_departments_are_derived_unique_and_resolved(self) -> None:
        cat = catalog()
        dept_ids = [d["id"] for d in cat["departments"]]
        self.assertEqual(dept_ids, ["engineering", "quality"])
        self.assertEqual(len(dept_ids), len(set(dept_ids)))
        for department in cat["departments"]:
            self.assertTrue(department["name"])
        role_depts = {r["department_id"] for r in cat["roles"]}
        self.assertTrue(role_depts <= set(dept_ids))

    def test_role_field_mapping(self) -> None:
        alpha = catalog()["roles"][0]
        self.assertEqual(alpha["id"], "alpha")
        self.assertEqual(alpha["name"], "alpha")
        self.assertEqual(alpha["title"], "Alpha Lead")
        self.assertEqual(alpha["department_id"], "engineering")
        self.assertEqual(alpha["model_hint"], "opus")
        self.assertEqual(alpha["advisory_tools"], ["Read", "Bash", "Skill"])
        self.assertEqual(alpha["invocation"], "1. clarify the goal\n2. decompose the work")
        self.assertEqual(alpha["expertise"], ["design", "delivery"])
        self.assertEqual(alpha["standards"], ["every task has an owner"])

    def test_handoffs_are_shaped_and_advisory(self) -> None:
        alpha = catalog()["roles"][0]
        self.assertEqual(len(alpha["handoffs"]), 1)
        handoff = alpha["handoffs"][0]
        self.assertEqual(handoff["role_id"], "beta")
        self.assertFalse(handoff["required"])
        self.assertTrue(handoff["reason"])

    def test_skills_carry_full_provenance(self) -> None:
        alpha = catalog()["roles"][0]
        self.assertEqual(alpha["skills"], [PROV["owner/skill-a"]])


class FailClosedTest(unittest.TestCase):
    def test_unresolved_handoff_raises(self) -> None:
        roster = [dict(ROSTER[0], handoffs=["ghost"]), ROSTER[1]]
        with self.assertRaisesRegex(ValueError, "handoff"):
            build_catalog(roster, source_commit=COMMIT, provenance=PROV)

    def test_duplicate_role_id_raises(self) -> None:
        roster = [ROSTER[0], dict(ROSTER[1], name="alpha")]
        with self.assertRaisesRegex(ValueError, "duplicate role"):
            build_catalog(roster, source_commit=COMMIT, provenance=PROV)

    def test_missing_skill_provenance_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "provenance"):
            build_catalog(ROSTER, source_commit=COMMIT, provenance={})

    def test_bad_source_commit_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "source_commit"):
            build_catalog(ROSTER, source_commit="nope", provenance=PROV)


if __name__ == "__main__":
    unittest.main()
