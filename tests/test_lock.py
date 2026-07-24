"""Tests for the deterministic, offline skills-lock builder (Task 3)."""

import unittest

from catalog.lock import build_lock, classify_kind, descriptor_digest
from catalog.provenance import provenance_for_roster, verify_lock_entry

LOCAL_SLUGS = {"tailwind", "find-subagents"}
COMMIT = "a" * 40

ROSTER = [
    {
        "name": "alpha",
        "skills": [
            ("owner/thing", "registry skill"),
            ("tailwind", "local skill"),
            ("gsd", "framework"),
            ("drawio", "bundled"),
        ],
    },
]
LOCAL_CONTENT = {"tailwind": b"# tailwind conventions\n"}


def lock():
    return build_lock(
        ROSTER,
        source_commit=COMMIT,
        local_slugs=LOCAL_SLUGS,
        local_content=LOCAL_CONTENT,
    )


class ClassifyTest(unittest.TestCase):
    def test_kinds(self) -> None:
        self.assertEqual(classify_kind("owner/thing", LOCAL_SLUGS), "registry")
        self.assertEqual(classify_kind("gsd", LOCAL_SLUGS), "framework")
        self.assertEqual(classify_kind("tailwind", LOCAL_SLUGS), "local")
        self.assertEqual(classify_kind("drawio", LOCAL_SLUGS), "bundled")


class DescriptorDigestTest(unittest.TestCase):
    def test_deterministic_64_hex(self) -> None:
        a = descriptor_digest("owner/thing", "registry", "skills.sh:owner/thing")
        b = descriptor_digest("owner/thing", "registry", "skills.sh:owner/thing")
        self.assertEqual(a, b)
        self.assertRegex(a, r"^[0-9a-f]{64}$")


class BuildLockTest(unittest.TestCase):
    def test_covers_every_roster_skill(self) -> None:
        skills = lock()["skills"]
        self.assertEqual(set(skills), {"owner/thing", "tailwind", "gsd", "drawio"})

    def test_local_entry_is_content_addressed(self) -> None:
        entry = lock()["skills"]["tailwind"]
        self.assertEqual(entry["kind"], "local")
        self.assertEqual(entry["version"], COMMIT)
        self.assertEqual(entry["license"], "MIT")
        self.assertEqual(entry["source"], "local:GNour/subagents")
        # content-addressed digest of the injected bytes
        from hashlib import sha256

        self.assertEqual(entry["sha256"], sha256(LOCAL_CONTENT["tailwind"]).hexdigest())

    def test_registry_entry_is_declared_advisory(self) -> None:
        entry = lock()["skills"]["owner/thing"]
        self.assertEqual(entry["kind"], "registry")
        self.assertEqual(entry["source"], "skills.sh:owner/thing")
        self.assertEqual(entry["license"], "advisory-unverified")
        self.assertTrue(entry["version"].startswith("advisory-"))

    def test_every_entry_passes_provenance_verification(self) -> None:
        for skill_id, entry in lock()["skills"].items():
            verify_lock_entry(skill_id, entry)

    def test_projection_yields_aegis_fields(self) -> None:
        prov = provenance_for_roster(ROSTER, lock()["skills"])
        self.assertEqual(
            set(prov["owner/thing"]), {"id", "source", "version", "sha256", "license"}
        )

    def test_build_is_deterministic(self) -> None:
        self.assertEqual(lock(), lock())

    def test_missing_local_content_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "local skill content"):
            build_lock(
                ROSTER,
                source_commit=COMMIT,
                local_slugs=LOCAL_SLUGS,
                local_content={},
            )


if __name__ == "__main__":
    unittest.main()
