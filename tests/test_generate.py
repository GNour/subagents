"""Tests for deterministic dist compilation over the real committed assets (Task 4)."""

import json
import unittest
from hashlib import sha256

from catalog import repo
from catalog.generate import compile_assets


class CompileAssetsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog_text, self.manifest_text = compile_assets(repo.REPO_ROOT)
        self.catalog = json.loads(self.catalog_text)
        self.manifest = json.loads(self.manifest_text)

    def test_compilation_is_deterministic(self) -> None:
        again_catalog, again_manifest = compile_assets(repo.REPO_ROOT)
        self.assertEqual(self.catalog_text, again_catalog)
        self.assertEqual(self.manifest_text, again_manifest)

    def test_catalog_covers_the_whole_roster(self) -> None:
        roster = repo.load_roster(repo.REPO_ROOT)
        self.assertEqual(len(self.catalog["roles"]), len(roster))
        role_ids = [r["id"] for r in self.catalog["roles"]]
        self.assertEqual(len(role_ids), len(set(role_ids)))

    def test_every_role_skill_has_five_field_provenance(self) -> None:
        for role in self.catalog["roles"]:
            for skill in role["skills"]:
                self.assertEqual(
                    set(skill), {"id", "source", "version", "sha256", "license"}
                )

    def test_manifest_digest_matches_catalog_bytes(self) -> None:
        self.assertEqual(
            self.manifest["catalog_sha256"],
            sha256(self.catalog_text.encode("utf-8")).hexdigest(),
        )

    def test_manifest_carries_full_supply_chain_fields(self) -> None:
        self.assertEqual(self.manifest["source_commit"], self.catalog["source_commit"])
        self.assertIn("generator_version", self.manifest)
        sample = next(iter(self.manifest["skills"].values()))
        self.assertEqual(
            set(sample), {"source", "kind", "version", "sha256", "license"}
        )


if __name__ == "__main__":
    unittest.main()
