"""Tests for installer supply-chain corrections (Task 6).

Covers target detection/selection, atomic write + rollback, atomic tree replacement,
and cross-harness conversion field-loss reporting.
"""

import importlib.util
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "_install", Path(__file__).resolve().parent.parent / "scaffold" / "_install.py"
)
install = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(install)


class SelectionTest(unittest.TestCase):
    def test_none_selected_targets_only_detected(self) -> None:
        targets, skipped = install.resolve_selection(
            {"claude": False, "opencode": False, "codex": False, "pi": False},
            all_flag=False,
            detected={"claude", "pi"},
        )
        self.assertEqual(targets, ["claude", "pi"])
        self.assertEqual(set(skipped), {"opencode", "codex"})

    def test_all_flag_forces_every_harness(self) -> None:
        targets, skipped = install.resolve_selection(
            {k: False for k in install.ORDER}, all_flag=True, detected=set()
        )
        self.assertEqual(targets, list(install.ORDER))
        self.assertEqual(skipped, [])

    def test_explicit_flag_wins_even_if_undetected(self) -> None:
        targets, skipped = install.resolve_selection(
            {"claude": True, "opencode": False, "codex": False, "pi": False},
            all_flag=False,
            detected=set(),
        )
        self.assertEqual(targets, ["claude"])


class AtomicWriteTest(unittest.TestCase):
    def test_write_creates_file(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "a" / "agent.md"
            install.atomic_write(str(dest), "hello")
            self.assertEqual(dest.read_text(), "hello")

    def test_failed_write_rolls_back_previous_content(self) -> None:
        import tempfile
        from unittest import mock

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "agent.md"
            dest.write_text("original")
            with mock.patch(
                "builtins.open", side_effect=OSError("disk full")
            ), self.assertRaises(OSError):
                install.atomic_write(str(dest), "new content")
            self.assertEqual(dest.read_text(), "original")  # unchanged
            self.assertFalse((Path(tmp) / "agent.md.bak").exists())


class AtomicTreeTest(unittest.TestCase):
    def test_replace_tree_swaps_contents(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "SKILL.md").write_text("v2")
            dest = Path(tmp) / "dest"
            dest.mkdir()
            (dest / "SKILL.md").write_text("v1")
            (dest / "stale.txt").write_text("gone")
            install.atomic_replace_tree(str(src), str(dest))
            self.assertEqual((dest / "SKILL.md").read_text(), "v2")
            self.assertFalse((dest / "stale.txt").exists())
            self.assertFalse((Path(tmp) / "dest.bak").exists())


class FieldLossTest(unittest.TestCase):
    def test_claude_is_lossless_others_report_drops(self) -> None:
        specs = install.target_specs(project=False)
        self.assertEqual(install.dropped_fields(specs["claude"]), [])
        for key in ("opencode", "codex", "pi"):
            dropped = install.dropped_fields(specs[key])
            self.assertIn("model", dropped)
            self.assertIn("skills", dropped)


if __name__ == "__main__":
    unittest.main()
