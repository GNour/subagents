"""Fail-closed validation tests over recorded fixtures and the real catalog (Task 5)."""

import copy
import json
import unittest
from pathlib import Path

from catalog import repo
from catalog.validate import CatalogValidationError, validate_catalog

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ValidFixtureTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        validate_catalog(load("subagents-valid.json"), expected_schema_version="1")


class RecordedMaliciousFixtureTest(unittest.TestCase):
    def test_unknown_field_fails(self) -> None:
        with self.assertRaisesRegex(CatalogValidationError, "unknown field"):
            validate_catalog(load("subagents-unknown-field.json"))

    def test_duplicate_role_fails(self) -> None:
        with self.assertRaisesRegex(CatalogValidationError, "duplicate role"):
            validate_catalog(load("subagents-duplicate-role.json"))


class MutationFailClosedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.base = load("subagents-valid.json")

    def mutate(self, fn) -> dict:
        cat = copy.deepcopy(self.base)
        fn(cat)
        return cat

    def test_unresolved_handoff_fails(self) -> None:
        cat = self.mutate(lambda c: c["roles"][0]["handoffs"].append(
            {"role_id": "ghost", "reason": "x", "required": False}
        ))
        with self.assertRaisesRegex(CatalogValidationError, "unresolved handoff"):
            validate_catalog(cat)

    def test_cyclic_required_handoff_fails(self) -> None:
        def make_cycle(c):
            c["roles"][0]["handoffs"] = [{"role_id": "beta", "reason": "x", "required": True}]
            c["roles"][1]["handoffs"] = [{"role_id": "alpha", "reason": "x", "required": True}]
        with self.assertRaisesRegex(CatalogValidationError, "cyclic required"):
            validate_catalog(self.mutate(make_cycle))

    def test_mutable_version_fails(self) -> None:
        cat = self.mutate(lambda c: c["roles"][0]["skills"][0].__setitem__("version", "latest"))
        with self.assertRaisesRegex(CatalogValidationError, "mutable"):
            validate_catalog(cat)

    def test_bad_sha256_fails(self) -> None:
        cat = self.mutate(lambda c: c["roles"][0]["skills"][0].__setitem__("sha256", "nope"))
        with self.assertRaisesRegex(CatalogValidationError, "sha256"):
            validate_catalog(cat)

    def test_missing_provenance_field_fails(self) -> None:
        cat = self.mutate(lambda c: c["roles"][0]["skills"][0].pop("license"))
        with self.assertRaisesRegex(CatalogValidationError, "missing field"):
            validate_catalog(cat)

    def test_unresolved_department_fails(self) -> None:
        cat = self.mutate(lambda c: c["roles"][0].__setitem__("department_id", "ghost"))
        with self.assertRaisesRegex(CatalogValidationError, "unresolved department"):
            validate_catalog(cat)


class RealCatalogTest(unittest.TestCase):
    def test_real_dist_catalog_validates(self) -> None:
        catalog = json.loads(
            (repo.REPO_ROOT / "dist" / "catalog.json").read_text(encoding="utf-8")
        )
        validate_catalog(catalog, expected_schema_version="1")


if __name__ == "__main__":
    unittest.main()
