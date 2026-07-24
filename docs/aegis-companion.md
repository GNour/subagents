# Aegis companion status

**Status:** P0 catalog package complete — the Aegis Plan 1a **entry gate is open**.

This repository is a required first-party companion package for Aegis. It is consumed as
a pinned Git submodule at `packages/subagents`; Aegis re-validates the emitted catalog
with its own strict models and grants runtime authority — nothing here does.

## Entry-gate commands (all exit 0)

```bash
bin/subagents-catalog validate          # catalog + skills lock are valid
bin/subagents-catalog generate --check  # committed dist assets match the source
bin/subagents-catalog version --json    # {"catalog_schema_version":"1","package_version":"1.0.0-aegis.0"}
```

## Pinned identity

Authoritative values live in these committed files (do not duplicate them in prose):

- `config/catalog.meta.json` — `package_version`, `catalog_schema_version`, `source_commit`.
- `config/skills.lock.json` — per-skill `source`, `kind`, `version`, `sha256`, `license`.
- `dist/provenance.json` — `catalog_sha256` plus the full per-skill supply-chain record.

## Provenance model

- **local** skills: content-addressed (SHA-256 of the committed `SKILL.md`), `license: MIT`.
- **registry / framework / bundled**: declared-advisory (digest over the canonical
  `{id,kind,source}` descriptor, `license: advisory-unverified`).

See `docs/plans/01-aegis-catalog-package.md` decision **D3** for the rationale (only
5 of 122 registry ids resolve as real repos) and the `lock --upgrade` upgrade path.

## Remaining (not gating the entry gate)

- Promote the 117 declared-advisory registry entries to verified upstream pins.
- P1: locked dev dependencies, CI matrix, SBOM, and a published compatibility table.
