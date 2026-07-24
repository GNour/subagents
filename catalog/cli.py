"""Command dispatch for the ``subagents-catalog`` entry-gate CLI.

Only ``version`` is wired up in Task 1. ``validate``, ``generate``, and ``lock`` are
added in later tasks. No subcommand reads the network except ``lock``.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from catalog import CATALOG_SCHEMA_VERSION, PACKAGE_VERSION


def _cmd_version(args: argparse.Namespace) -> int:
    block = {
        "package_version": PACKAGE_VERSION,
        "catalog_schema_version": CATALOG_SCHEMA_VERSION,
    }
    if args.json:
        print(json.dumps(block, sort_keys=True, separators=(",", ":")))
    else:
        print(
            f"subagents-catalog {PACKAGE_VERSION} "
            f"(catalog schema {CATALOG_SCHEMA_VERSION})"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="subagents-catalog",
        description="Emit and verify the Aegis-facing Subagents catalog.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    version = sub.add_parser(
        "version", help="print package and catalog-schema versions"
    )
    version.add_argument(
        "--json", action="store_true", help="emit a strict JSON version block"
    )
    version.set_defaults(func=_cmd_version)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
