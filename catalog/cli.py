"""Command dispatch for the ``subagents-catalog`` entry-gate CLI.

Subcommands: ``version``, ``lock``. ``generate`` and ``validate`` are added in later
tasks. Only a future ``lock --upgrade`` would touch the network; nothing here does.
"""

from __future__ import annotations

import argparse
import json
import sys
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


def _cmd_lock(args: argparse.Namespace) -> int:
    from catalog import repo
    from catalog.io import canonical_json, write_json_atomic
    from catalog.lock import build_lock

    root = repo.REPO_ROOT
    meta = repo.load_meta(root)
    slugs = repo.local_slugs(root)
    lock = build_lock(
        repo.load_roster(root),
        source_commit=str(meta["source_commit"]),
        local_slugs=slugs,
        local_content=repo.local_content(root, slugs),
        license_=str(meta.get("license", "MIT")),
    )
    path = root / "config" / "skills.lock.json"
    rendered = canonical_json(lock)
    if args.check:
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != rendered:
            print(
                "config/skills.lock.json is out of date; run: subagents-catalog lock",
                file=sys.stderr,
            )
            return 1
        print("config/skills.lock.json is up to date")
        return 0
    write_json_atomic(path, lock)
    print(f"wrote {path.relative_to(root)} ({len(lock['skills'])} skills)")
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    from catalog import repo
    from catalog.generate import asset_targets
    from catalog.io import write_text_atomic

    root = repo.REPO_ROOT
    targets = asset_targets(root)
    if args.check:
        drift = [
            path
            for path, text in targets.items()
            if (path.read_text(encoding="utf-8") if path.exists() else "") != text
        ]
        if drift:
            names = ", ".join(str(p.relative_to(root)) for p in drift)
            print(
                f"dist assets out of date ({names}); run: subagents-catalog generate",
                file=sys.stderr,
            )
            return 1
        print("dist assets are up to date")
        return 0
    for path, text in targets.items():
        write_text_atomic(path, text)
    print("wrote dist/catalog.json and dist/provenance.json")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    import json

    from catalog import CATALOG_SCHEMA_VERSION, repo
    from catalog.provenance import ProvenanceError, load_lock
    from catalog.validate import CatalogValidationError, validate_catalog

    root = repo.REPO_ROOT
    catalog_path = root / "dist" / "catalog.json"
    lock_path = root / "config" / "skills.lock.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        validate_catalog(catalog, expected_schema_version=CATALOG_SCHEMA_VERSION)
        load_lock(lock_path)
    except FileNotFoundError as error:
        print(f"missing asset: {error.filename}", file=sys.stderr)
        return 1
    except (CatalogValidationError, ProvenanceError) as error:
        print(f"invalid catalog: {error}", file=sys.stderr)
        return 1
    print(
        f"catalog valid: {len(catalog['roles'])} roles, "
        f"{len(catalog['departments'])} departments"
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

    lock = sub.add_parser(
        "lock", help="build config/skills.lock.json from the roster (offline)"
    )
    lock.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed lock is out of date instead of writing",
    )
    lock.set_defaults(func=_cmd_lock)

    generate = sub.add_parser(
        "generate", help="write dist/catalog.json and dist/provenance.json (offline)"
    )
    generate.add_argument(
        "--check",
        action="store_true",
        help="fail if committed dist assets are out of date instead of writing",
    )
    generate.set_defaults(func=_cmd_generate)

    validate = sub.add_parser(
        "validate", help="validate the committed catalog and skills lock"
    )
    validate.set_defaults(func=_cmd_validate)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
