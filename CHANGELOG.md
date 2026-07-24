# Changelog

## 1.0.0-aegis.0 — 2026-07-24

First Aegis companion release: a versioned, data-oriented catalog package that Aegis
consumes as a verified source input (pinned submodule at `packages/subagents`).

### Added

- `bin/subagents-catalog` CLI (Python stdlib only, no third-party runtime deps):
  `version --json`, `lock [--check]`, `generate [--check]`, `validate`.
- Deterministic role catalog `dist/catalog.json` (35 roles across 7 departments) and
  supply-chain manifest `dist/provenance.json`, derived purely from
  `scaffold/roster.py` and the committed lock/meta (no network, no clock).
- Published JSON Schema `catalog/schema/catalog.schema.json` matching the Aegis
  `SubagentsCatalog` contract; unknown fields are rejected.
- Skill provenance lock `config/skills.lock.json` (129 skills) and release metadata
  `config/catalog.meta.json`.
- Recorded valid + malicious fixtures under `tests/fixtures/` for Aegis contract tests.
- `docs/plans/01-aegis-catalog-package.md` (TDD plan) and MIT `LICENSE`.

### Fixed (installer supply-chain)

- Default install targets only harnesses actually detected; explicit flag or `--all`
  forces others.
- Atomic writes and staged tree replacement with backup + rollback replace the previous
  destructive `rmtree`.
- Cross-harness conversion now reports every dropped frontmatter field.
- `install-skills.sh` fails closed on any skill failure; both skill scripts warn that
  `npx skills` resolves mutable upstream HEAD and do not touch the pinned lock.

### Known limitations

- 117 of 122 registry skills carry **declared-advisory** provenance (descriptor digest,
  `license: advisory-unverified`) rather than verified upstream content pins, because
  their roster ids are advisory `owner/skill-name` references, not resolvable
  `owner/repo@skill` packages. A future networked `lock --upgrade` can promote any of
  them to a true pin. See `docs/plans/01-aegis-catalog-package.md` (decision D3).
