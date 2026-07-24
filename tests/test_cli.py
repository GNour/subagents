"""Entry-gate CLI tests for `bin/subagents-catalog`."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "bin" / "subagents-catalog"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BIN), *args],
        capture_output=True,
        text=True,
    )


class VersionCommandTest(unittest.TestCase):
    def test_version_json_emits_strict_block(self) -> None:
        result = run("version", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"package_version", "catalog_schema_version"})
        # Aegis CompanionLock patterns (Plan 1a Task 1).
        self.assertRegex(
            payload["package_version"],
            r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$",
        )
        self.assertRegex(payload["catalog_schema_version"], r"^[0-9]+$")

    def test_no_subcommand_fails(self) -> None:
        result = run()
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
