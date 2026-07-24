"""Deterministic compilation of the committed ``dist/`` assets.

``compile_assets`` reads only committed files (roster, ``config/skills.lock.json``,
``config/catalog.meta.json``) and returns the exact text of ``dist/catalog.json`` and
``dist/provenance.json``. It performs no network or clock access, so ``generate --check``
is reproducible on any commit.

The provenance manifest carries the source commit, generator version, catalog digest,
and every skill's full lock record (source, kind, version, checksum, license) — the
supply-chain manifest required by the Aegis companion handoff.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from catalog import PACKAGE_VERSION, repo
from catalog.build import build_catalog
from catalog.io import canonical_json
from catalog.provenance import load_lock, provenance_for_roster


def compile_assets(repo_root: Path = repo.REPO_ROOT) -> tuple[str, str]:
    """Return ``(catalog_json_text, provenance_json_text)`` for the committed assets."""
    meta = repo.load_meta(repo_root)
    lock = load_lock(repo_root / "config" / "skills.lock.json")
    roster = repo.load_roster(repo_root)

    provenance = provenance_for_roster(roster, lock)
    catalog = build_catalog(
        roster,
        source_commit=str(meta["source_commit"]),
        provenance=provenance,
        package_version=str(meta["package_version"]),
        catalog_schema_version=str(meta["catalog_schema_version"]),
    )
    catalog_text = canonical_json(catalog)
    catalog_sha256 = sha256(catalog_text.encode("utf-8")).hexdigest()

    manifest = {
        "schema_version": 1,
        "generator_version": PACKAGE_VERSION,
        "source_commit": str(meta["source_commit"]),
        "package_version": str(meta["package_version"]),
        "catalog_schema_version": str(meta["catalog_schema_version"]),
        "catalog_sha256": catalog_sha256,
        "skills": dict(sorted(lock.items())),
    }
    return catalog_text, canonical_json(manifest)


def asset_targets(repo_root: Path = repo.REPO_ROOT) -> dict[Path, str]:
    """Map each committed dist path to its expected canonical text."""
    catalog_text, manifest_text = compile_assets(repo_root)
    return {
        repo_root / "dist" / "catalog.json": catalog_text,
        repo_root / "dist" / "provenance.json": manifest_text,
    }
