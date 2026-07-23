# Tech Company Subagent Fleet

A cross-functional **tech company built from 35 specialised subagents** —
engineering, quality, data, infrastructure, design, and product — each paired with the
real, installable **skills** it needs. Inspired by
[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
and the [skills.sh](https://www.skills.sh) ecosystem.

## Departments

### 🛠 Engineering (9)

- **`tech-lead`** — Use to break a feature or epic into engineering tasks, choose the right specialist (Python/Laravel/Next/Nest/React Native/React), set architecture direction, and coordinate delivery across the engineering department.
- **`api-architect`** — Use to design REST/GraphQL API contracts, versioning, pagination, error models, auth flows, and payment integrations that all backend specialists implement against.
- **`python-dev`** — Use to build Python services and APIs (FastAPI/Django), data-processing scripts, and typed, well-tested Python 3.12+ code.
- **`laravel-dev`** — Use to build Laravel 10+ applications and APIs: Eloquent models, queues, jobs, policies, resources, and PHP 8.2+ code with strong test coverage.
- **`nextjs-dev`** — Use to build Next.js (App Router) applications: server/client components, server actions, routing, data fetching, auth, and performance-tuned frontends.
- **`reactjs-dev`** — Use to build client-side React applications (Vite/SPA): component architecture, state management, hooks, forms, and accessible UI.
- **`nestjs-dev`** — Use to build NestJS backend services: modules, providers, guards, interceptors, DTO validation, GraphQL/REST endpoints, and typed Node services.
- **`react-native-dev`** — Use to build cross-platform mobile apps with React Native + Expo: native UI, navigation, data fetching, deployment, and OTA updates.
- **`fullstack-dev`** — Use for small, self-contained features that span frontend and backend and don't warrant splitting across specialists — prototypes, glue code, and end-to-end vertical slices.

### ✅ Quality & Testing (7)

- **`qa-engineer`** — Use to define the overall test strategy, write test plans and acceptance criteria, do exploratory testing, and coordinate the specialist test agents.
- **`e2e-test-engineer`** — Use to write and maintain end-to-end browser and mobile tests (Playwright, Cypress, Detox): user-flow coverage, auth reuse, stable locators, and CI wiring.
- **`unit-test-engineer`** — Use to add fast, focused unit and integration tests across the stack (pytest, Jest, Vitest, PHPUnit) and to raise coverage on critical logic.
- **`code-reviewer`** — Use to review diffs and PRs for correctness, security, readability, and adherence to conventions before merge. Read-only — reports findings, does not edit.
- **`accessibility-tester`** — Use to audit UIs against WCAG, check keyboard/screen-reader flows, color contrast, and semantics, and report prioritized accessibility fixes.
- **`performance-engineer`** — Use to profile and optimize frontend and backend performance: Core Web Vitals, bundle size, query/latency hotspots, and load behavior.
- **`security-auditor`** — Use for defensive security review of code and configuration: authn/authz flaws, injection, secrets handling, dependency risk, and remediation guidance. Authorized/defensive use only.

### 🗄 Data & AI (4)

- **`data-engineer`** — Use to build data pipelines, ETL/ELT, warehouse models, and reliable ingestion; schema design and data quality across Postgres and analytics stores.
- **`data-analyst`** — Use to answer product/business questions with data: SQL analysis, metrics definitions, cohort/funnel analysis, and clear visualized findings.
- **`ml-engineer`** — Use to build ML and LLM-powered features: model integration, RAG, prompt/tooling design, evaluation, and productionizing inference.
- **`database-administrator`** — Use to design schemas, write and review migrations, tune indexes and slow queries, and plan for scale and reliability (primarily Postgres).

### ☁️ Infrastructure (3)

- **`devops-engineer`** — Use to build CI/CD pipelines, containerization, infrastructure-as-code, and deployment automation across environments.
- **`cloud-architect`** — Use to design cloud architecture: service topology, networking, scaling, cost, and reliability trade-offs across providers.
- **`sre-incident-responder`** — Use to define SLOs, monitoring, and alerting, and to lead incident diagnosis and blameless postmortems.

### 🎨 Design (3)

- **`ui-designer`** — Use to design interfaces and visual layouts, translate Figma into implementation-ready specs, and ensure visual consistency and polish.
- **`ux-researcher`** — Use to plan and analyze user research: interview guides, usability findings, journey maps, and evidence-based product recommendations.
- **`design-system-engineer`** — Use to build and maintain the component library and design tokens that all frontend agents consume — accessible, documented, versioned.

### 📋 Product & Research (6)

- **`product-owner`** — Use to translate goals into a prioritized backlog: user stories, acceptance criteria, roadmap, and scope/trade-off decisions.
- **`scrum-master`** — Use to facilitate agile delivery: sprint planning, backlog grooming, ceremony structure, and removing delivery blockers.
- **`business-analyst`** — Use to elicit and document requirements, model processes, and bridge business needs to technical specifications.
- **`market-researcher`** — Use for market sizing, competitive analysis, trend scanning, and evidence-based product/positioning recommendations.
- **`technical-writer`** — Use to write and maintain docs: API references, guides, READMEs, changelogs, and onboarding — accurate, tested, and reader-focused.
- **`seo-specialist`** — Use to plan and audit organic search: technical SEO, on-page and content strategy, structured data/schema, site architecture, Core Web Vitals, and programmatic/AI-search (AEO) optimization.

### 🧭 Meta / Orchestration (3)

- **`company-orchestrator`** — Use as the top-level entry point for a large initiative: it routes work to the right department lead (tech-lead, product-owner, cloud-architect, etc.), sequences cross-department work, and tracks the initiative end-to-end.
- **`context-manager`** — Use to capture, organize, and hand off shared project context (decisions, glossary, current state) between agents and across long-running work.
- **`dynamic-agent`** — Use for a delegated task that doesn't map cleanly to one fixed specialist, or when you want a single agent to receive a task, discover the right role, dynamically load the matching skills, and execute end-to-end. It has no fixed specialism — it adopts one per task.

## Layout

```
agents/
  engineering/    # 🛠 Engineering (9)
  quality/    # ✅ Quality & Testing (7)
  data-ai/    # 🗄 Data & AI (4)
  infrastructure/    # ☁️ Infrastructure (3)
  design/    # 🎨 Design (3)
  product/    # 📋 Product & Research (6)
  meta/    # 🧭 Meta / Orchestration (3)
skills/                # locally-authored skills (e.g. tailwind/SKILL.md)
SKILLS.md              # which skills each agent uses + install/update commands
install.sh             # install agents (+ local skills) into all four harnesses
scaffold/
  roster.py            # single source of truth for the fleet
  generate.py          # regenerates agents/, SKILLS.md, README.md
  install-skills.sh    # installs all skills.sh registry skills the fleet uses
  update-skills.sh     # updates ALL installed registry skills to latest (one cmd)
  install-gsd.sh       # installs the GSD spec-driven workflow framework
```

## Install the agents

The installer targets four harnesses and converts formats as needed:

| Harness | Destination | Format |
|---|---|---|
| Claude Code | `~/.claude/agents/<dept>/` | Markdown + frontmatter (native subagents) |
| opencode | `~/.config/opencode/agent/` | Markdown + frontmatter |
| Codex | `~/.codex/agents/` | TOML (auto-converted) |
| pi | `~/.pi/agent/prompts/` | Markdown prompt templates |

```bash
# install into every detected harness (global)
bash install.sh

# or target specific harnesses
bash install.sh --claude --opencode
bash install.sh --codex
bash install.sh --pi

# install into the current project instead of the home dir
bash install.sh --claude --project

# preview without writing anything
bash install.sh --all --dry-run
```

## Install & update the skills

See [`SKILLS.md`](./SKILLS.md) for the full agent→skill mapping and the four skill
kinds (registry / local / framework / bundled).

```bash
bash scaffold/install-skills.sh   # install every skills.sh registry skill
bash scaffold/update-skills.sh    # update ALL installed skills to latest (one command)
bash scaffold/install-gsd.sh      # install the GSD workflow framework
```

`update-skills.sh` wraps `npx skills update` — the skills.sh CLI keeps every installed
skill in sync with its upstream source across all harnesses from a single command.

Referenced across the fleet: **122 registry**, **3 local**, **1 framework**, and **3 bundled** skills.

### Web styling: Tailwind + shadcn/ui

Web agents (`nextjs-dev`, `reactjs-dev`, `fullstack-dev`, `design-system-engineer`)
carry the `tailwind` local skill plus `google-labs-code/shadcn-ui`; `react-native-dev`
uses `expo/expo-tailwind-setup` (NativeWind). Edit `skills/tailwind/SKILL.md` to change
your Tailwind conventions, then re-run `bash install.sh`.

### Workflow framework: GSD (not Superpowers)

This fleet standardises on **[GSD (Get Shit Done)](https://github.com/shoootyou/get-shit-done-multi)**
— a spec-driven *plan → execute → verify* workflow — as its orchestration layer, rather
than the Superpowers (obra/*) TDD skills, to avoid two competing workflow philosophies.
`company-orchestrator`, `tech-lead`, and `product-owner` drive work through GSD; language
and testing skills (testmu, trailofbits, etc.) remain as techniques on top of it.

## Discovery & dynamic delegation

Three pieces let the fleet route work and load skills on the fly:

- **`find-subagents`** (local skill) — a generated team directory: every agent by
  department with when-to-use guidance, plus a machine-readable `agents.json`. Any
  agent (or you) can invoke it to answer *"who should do this task?"*
- **`select-skills`** (local skill) — a generated skill router: the skills relevant to
  each domain, plus a machine-readable `skills.json` (id, kind, what-for, used-by). Answers
  *"which skills should I load for this task?"* so agents use the **proper** skills per task.
- **`dynamic-agent`** — a generalist with no fixed specialism. Give it a delegated task;
  it uses `find-subagents` to adopt the right persona, `select-skills` to load the matching
  skills dynamically, executes, and escalates to a fixed specialist when depth is needed.

Both skills are regenerated from the roster on every `generate.py` run, so the directory
and catalog never drift from the actual agents.

## Customise / extend

`scaffold/roster.py` is the single source of truth. Add or edit an agent there, then:

```bash
python3 scaffold/generate.py   # regenerates agents/, SKILLS.md, README.md
```

Then re-run `install.sh` to push the changes to your harnesses.

## How subagents and skills fit together

- A **subagent** is a role: a persona, a tool scope, and a working protocol.
- A **skill** is portable know-how the agent loads on demand.
- The orchestrators (`company-orchestrator`, `tech-lead`) decompose an initiative and
  route each piece to the right specialist, who pulls in its skills to do the work.
