# Aegis Catalog Package Implementation Plan

> **For agentic workers:** Use a spec-driven, test-first workflow to implement this
> plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a versioned, data-oriented Subagents *catalog package* that Aegis can
consume as a verified source input — emitting a machine-readable role catalog and a
provenance manifest that satisfy the Aegis `SubagentsCatalog` contract, gated by three
package-local commands.

**Why this exists:** Aegis treats this repository as a required first-party companion
package (pinned Git submodule at `packages/subagents`). Aegis's
[companion integration plan](../../../aegis/docs/plans/01a-companion-packages-and-stage-packets.md)
has an **entry gate** that will not open until this repository exposes:

```bash
bin/subagents-catalog validate          # exit 0; catalog + provenance are valid
bin/subagents-catalog generate --check  # exit 0; committed assets match the source
bin/subagents-catalog version --json    # exit 0; strict JSON version block
```

and the emitted catalog matches the strict `SubagentsCatalog` model in Aegis Plan 1a
Task 2. This plan closes the P0 items in
[`aegis/docs/maintainer-handoff-promptx-subagents.md`](../../../aegis/docs/maintainer-handoff-promptx-subagents.md).

**Non-goals / authority boundary:** This package only *describes* roles and skills. It
marks every model, tool, skill, and handoff field **advisory**. It never grants runtime
authority — Aegis maps advisory metadata to real model aliases, typed tools, and
capability profiles on its side.

**Tech stack:** Python 3.12 **standard library only** (no `uv`, no third-party runtime
deps — Aegis re-validates with its own Pydantic models, so this side must merely *emit*
correct JSON, publish a JSON Schema, and self-validate). Tests use `unittest`. Git for
provenance; `curl`/`urllib` for the networked `lock` step only.

---

## Design decisions

### D1 — `roster.py` stays the single source of truth
The catalog is *derived* from `scaffold/roster.py`. No role data is hand-authored in the
catalog. `catalog/build.py` is a pure function `roster → catalog dict`.

### D2 — Field mapping (roster → Aegis `SubagentsRole`)
| Aegis field | Source | Notes |
|---|---|---|
| `id` | roster `name` | stable slug |
| `department_id` | roster `department` | must resolve to a department |
| `name` | roster `name` | slug (matches existing `agents.json`) |
| `title` | roster `title` | human title |
| `description` | roster `description` | |
| `expertise` | roster `expertise` | tuple |
| `invocation` | roster `when` | joined into a numbered procedure string |
| `standards` | roster `standards` | tuple |
| `model_hint` | roster `model` | **advisory** |
| `advisory_tools` | roster `tools` | split on `,`, trimmed — **advisory** |
| `skills` | roster `skills` ids → `skills.lock.json` | provenance (see D3) |
| `handoffs` | roster `handoffs` | `{role_id, reason, required=false}` (see D4) |

### D3 — Skill provenance (`config/skills.lock.json`)
Every skill referenced by the roster gets an immutable lock entry:
`{id, source, kind, version, sha256, license}` — `version` is a commit SHA or fixed
semver, **never `latest`**. `sha256` is a lowercase 64-hex digest. Resolution by kind:

- **local** (`find-subagents`, `select-skills`, `tailwind`): `source=local:GNour/subagents`,
  `version=` repo release commit, `sha256=` SHA-256 of the skill's `SKILL.md` bytes,
  `license=` repo `LICENSE`. **Fully offline / content-addressed.**
- **framework** (`gsd`): `source=` upstream repo URL, `version=` pinned commit,
  `sha256=` digest of the pinned tarball, `license=` upstream SPDX. **Networked pin.**
- **registry** (122 × `owner/repo`, skills.sh): `source=` resolved GitHub repo,
  `version=` pinned commit, `sha256=` digest of the pinned tarball, `license=` upstream
  SPDX. **Networked pin (batch).**
- **bundled** (`dataviz`, `drawio`, `jira-ticket-planner`): harness-provided, no repo
  content. `source=bundled:claude-code`, `version=` fixed harness version,
  `sha256=` digest over the canonical provenance descriptor, and the entry is flagged
  `kind=bundled` so downstream can treat it as a *declaration*, not a content hash.

`config/skills.lock.json` is committed. `generate` is pure and only reads the lock; the
networked `lock` command is the *only* code path that touches the network, and it is
never invoked by `validate`, `generate`, or `version`.

### D4 — Handoffs
Roster handoffs are role-name lists with no reason/required flag. Emit each as
`{role_id, reason, required: false}` with a templated, truthful reason. Keeping all
`required=false` also means required-handoff cycles cannot occur (the corpus still tests
that a required cycle *would* be rejected).

### D5 — Deterministic `source_commit`
The catalog's `source_commit` is read from a committed `config/catalog.meta.json`
(set at release/pin time), **not** from live `git HEAD`, so `generate --check` is
reproducible on any commit. The `lock`/release step updates it.

---

## File map
| Path | Responsibility |
|---|---|
| `bin/subagents-catalog` | executable CLI shim (`python3`, no deps) |
| `catalog/__init__.py` | `PACKAGE_VERSION`, `CATALOG_SCHEMA_VERSION` |
| `catalog/build.py` | pure `roster → catalog dict` transform |
| `catalog/provenance.py` | load/verify `skills.lock.json`; build provenance manifest |
| `catalog/lock.py` | **networked** resolver → writes `skills.lock.json` |
| `catalog/validate.py` | stdlib fail-closed validator (mirrors the JSON Schema) |
| `catalog/generate.py` | deterministic write + `--check` (atomic replace) |
| `catalog/cli.py` | dispatch: `version` / `validate` / `generate` / `lock` |
| `catalog/schema/catalog.schema.json` | published JSON Schema (rejects unknown fields) |
| `config/skills.lock.json` | committed immutable skill provenance |
| `config/catalog.meta.json` | committed release metadata (`source_commit`, versions) |
| `dist/catalog.json` | committed generated catalog (checked by `generate --check`) |
| `dist/provenance.json` | committed generated provenance manifest |
| `tests/` | `unittest` suites + `tests/fixtures/` valid & malicious catalogs |

---

## Tasks

### Task 1: Package skeleton and `version --json`
- [ ] Write a failing `tests/test_cli.py` asserting `version --json` emits
  `{"package_version": ..., "catalog_schema_version": ...}` and exits 0.
- [ ] Add `catalog/__init__.py` (version constants), `catalog/cli.py` (`version`
  subcommand), and the `bin/subagents-catalog` executable shim.
- [ ] `python3 -m unittest` green; `bin/subagents-catalog version --json` prints strict
  JSON. Commit.

### Task 2: Catalog data models and roster→catalog transform
- [ ] Failing tests: unique role/department ids, resolved department + handoff refs,
  `invocation` rendered from `when`, `advisory_tools` split correctly, and that no
  authority-bearing key leaks (`Bash` etc. stay under `advisory_tools`).
- [ ] Implement `catalog/build.py` (pure) per D2. Departments derived from the roster's
  department set with stable ordering.
- [ ] Tests green. Commit.

### Task 3: Skill provenance lock + resolver
- [ ] Failing tests for `catalog/provenance.py`: lock loads, rejects `latest`/mutable
  versions, rejects non-64-hex `sha256`, rejects a roster skill with no lock entry.
- [ ] Implement `catalog/provenance.py` (pure load/verify) and `catalog/lock.py`
  (networked resolver; inject the fetcher so tests use a fake). Populate real
  content-addressed provenance for the 3 local skills; pin `gsd`; batch-resolve the 122
  registry skills; declare the 3 bundled skills per D3.
- [ ] Commit `config/skills.lock.json`. Tests green. Commit.

### Task 4: Deterministic `generate` + `generate --check`
- [ ] Failing tests: two generations produce byte-identical `dist/catalog.json` and
  `dist/provenance.json`; `--check` fails on drift without writing; write is atomic
  (temp + `os.replace`).
- [ ] Implement `catalog/generate.py`; read `source_commit` from `config/catalog.meta.json`
  (D5). Commit the generated `dist/` assets. Tests green. Commit.

### Task 5: `validate`, JSON Schema, and fixtures
- [ ] Failing tests over `tests/fixtures/`: one valid catalog passes; malicious variants
  each fail closed — unknown field, duplicate role id, unresolved handoff, cyclic
  *required* handoff, missing provenance, mutable version, unknown catalog kind.
- [ ] Author `catalog/schema/catalog.schema.json` and `catalog/validate.py` (stdlib,
  same rules). `validate` checks `dist/catalog.json` + `config/skills.lock.json`.
- [ ] Tests green; `bin/subagents-catalog validate` exits 0 on the real assets. Commit.

### Task 6: Installer supply-chain corrections (P0)
- [ ] Failing tests: no install from mutable `latest`; a required-skill install failure
  aborts (no partial catalog); destination replacement is staged/atomic with backup +
  rollback (no destructive pre-delete); framework detection reflects *actually installed*
  harnesses; installer code is separable from the data package.
- [ ] Fix `install.sh` / `scaffold/*` accordingly. Tests green. Commit.

### Task 7: Entry-gate verification + release metadata
- [ ] Add `LICENSE`, `CHANGELOG.md`, and a catalog compatibility note.
- [ ] Run the full local gate: `python3 -m unittest`, then the three entry-gate commands;
  confirm each exits 0 with strict JSON.
- [ ] Record handoff evidence (versions + digests by reference to `config/*.json`) so
  Aegis Plan 1a's entry gate can open. Commit.

## Completion gate
This plan is complete when: the three entry-gate commands exit 0 with strict JSON; the
emitted catalog validates against the Aegis `SubagentsCatalog` contract; every skill has
immutable, digested provenance with a license; generation is deterministic and
byte-checked; malicious inputs fail closed; and the installer performs atomic,
non-destructive, fail-closed installs separate from the data package.
