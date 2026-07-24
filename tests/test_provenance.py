"""Tests for pure skill-provenance loading, verification, and projection (Task 3)."""

import json
import tempfile
import unittest
from pathlib import Path

from catalog.provenance import (
    ProvenanceError,
    load_lock,
    provenance_for_roster,
    roster_skill_ids,
    verify_lock_entry,
)


def good_entry(**overrides):
    entry = {
        "source": "registry:github.com/owner/repo",
        "kind": "registry",
        "version": "a" * 40,
        "sha256": "b" * 64,
        "license": "MIT",
    }
    entry.update(overrides)
    return entry


ROSTER = [
    {"name": "alpha", "skills": [("owner/repo", "n"), ("local-x", "n")]},
    {"name": "beta", "skills": [("owner/repo", "n")]},
]


class VerifyEntryTest(unittest.TestCase):
    def test_valid_entry_passes(self) -> None:
        verify_lock_entry("owner/repo", good_entry())

    def test_mutable_version_rejected(self) -> None:
        for bad in ("latest", "main", "HEAD", ""):
            with self.assertRaisesRegex(ProvenanceError, "version"):
                verify_lock_entry("owner/repo", good_entry(version=bad))

    def test_bad_sha256_rejected(self) -> None:
        with self.assertRaisesRegex(ProvenanceError, "sha256"):
            verify_lock_entry("owner/repo", good_entry(sha256="tooshort"))

    def test_unknown_kind_rejected(self) -> None:
        with self.assertRaisesRegex(ProvenanceError, "kind"):
            verify_lock_entry("owner/repo", good_entry(kind="wild"))

    def test_missing_license_rejected(self) -> None:
        with self.assertRaisesRegex(ProvenanceError, "license"):
            verify_lock_entry("owner/repo", good_entry(license=""))


class LoadLockTest(unittest.TestCase):
    def test_load_valid_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "skills.lock.json"
            path.write_text(
                json.dumps({"schema_version": 1, "skills": {"owner/repo": good_entry()}}),
                encoding="utf-8",
            )
            lock = load_lock(path)
            self.assertIn("owner/repo", lock)

    def test_wrong_schema_version_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "skills.lock.json"
            path.write_text(json.dumps({"schema_version": 2, "skills": {}}), encoding="utf-8")
            with self.assertRaisesRegex(ProvenanceError, "schema_version"):
                load_lock(path)


class ProjectionTest(unittest.TestCase):
    def test_roster_skill_ids_dedupes_in_order(self) -> None:
        self.assertEqual(roster_skill_ids(ROSTER), ["owner/repo", "local-x"])

    def test_projection_yields_exactly_aegis_fields(self) -> None:
        lock = {
            "owner/repo": good_entry(),
            "local-x": good_entry(kind="local", source="local:GNour/subagents"),
        }
        prov = provenance_for_roster(ROSTER, lock)
        self.assertEqual(
            set(prov["owner/repo"]), {"id", "source", "version", "sha256", "license"}
        )
        self.assertNotIn("kind", prov["owner/repo"])
        self.assertEqual(prov["owner/repo"]["id"], "owner/repo")

    def test_missing_provenance_raises(self) -> None:
        with self.assertRaisesRegex(ProvenanceError, "provenance"):
            provenance_for_roster(ROSTER, {"owner/repo": good_entry()})


if __name__ == "__main__":
    unittest.main()
