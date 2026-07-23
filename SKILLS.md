# Skills Manifest

Every subagent references a set of **skills** — reusable packages of procedural
best-practice knowledge. Subagents don't install skills; they *use* them (via the
`Skill` tool). This file is the source of truth for which skills each agent expects
and how each kind is installed and kept up to date.

## Skill kinds

| Kind | Looks like | Installed by |
|---|---|---|
| **registry** | `owner/repo` | `npx skills add owner/repo` (skills.sh) |
| **local** | single word, authored in `skills/<slug>/` | `bash install.sh` copies it into each harness |
| **framework** | `gsd` | its own installer — see below |
| **bundled** | single word (e.g. `jira-ticket-planner`, `drawio`, `dataviz`) | already provided by the harness — no install |

## Install & update (one command each)

```bash
bash scaffold/install-skills.sh   # install every registry skill the fleet uses
bash scaffold/update-skills.sh    # update ALL installed registry skills to latest
bash scaffold/install-gsd.sh      # install the GSD workflow framework
bash install.sh                   # (re)install agents + local skills into harnesses
```

`update-skills.sh` runs `npx skills update`, which the skills.sh CLI uses to pull the
latest version of every installed skill across all your harnesses from one place.
Re-run `install.sh` after editing a local skill (e.g. `tailwind`) to redistribute it.

## Skills by agent

### 🛠 Engineering

| Agent | Skills |
|---|---|
| `tech-lead` | `gsd`, `find-subagents`, `getsentry/sentry-code-review`, `anthropics/mcp-builder` |
| `api-architect` | `apollographql/graphql-schema`, `apollographql/apollo-server`, `stripe/stripe-best-practices`, `openai/security-threat-model`, `anthropics/mcp-builder` |
| `python-dev` | `trailofbits/modern-python`, `microsoft/fastapi-router-py`, `microsoft/pydantic-models-py`, `testmu-ai/pytest-skill`, `getsentry/sentry-python-sdk` |
| `laravel-dev` | `testmu-ai/phpunit-skill`, `testmu-ai/laravel-dusk-skill`, `getsentry/sentry-php-sdk`, `jira-ticket-planner` |
| `nextjs-dev` | `vercel-labs/next-best-practices`, `vercel-labs/next-cache-components`, `tailwind`, `google-labs-code/shadcn-ui`, `auth0/auth0-nextjs`, `getsentry/sentry-nextjs-sdk`, `anthropics/frontend-design`, `addyosmani/core-web-vitals` |
| `reactjs-dev` | `google-labs-code/react-components`, `tailwind`, `google-labs-code/shadcn-ui`, `microsoft/zustand-store-ts`, `auth0/auth0-react`, `getsentry/sentry-react-sdk`, `anthropics/frontend-design` |
| `nestjs-dev` | `getsentry/sentry-nestjs-sdk`, `apollographql/apollo-server`, `apollographql/graphql-schema`, `better-auth/best-practices`, `testmu-ai/jest-skill` |
| `react-native-dev` | `callstackincubator/react-native-best-practices`, `expo/building-native-ui`, `expo/expo-tailwind-setup`, `expo/native-data-fetching`, `expo/expo-deployment`, `getsentry/sentry-react-native-sdk`, `auth0/auth0-react-native` |
| `fullstack-dev` | `vercel-labs/next-best-practices`, `tailwind`, `google-labs-code/shadcn-ui`, `anthropics/frontend-design`, `testmu-ai/vitest-skill` |

### ✅ Quality & Testing

| Agent | Skills |
|---|---|
| `qa-engineer` | `anthropics/webapp-testing`, `testmu-ai/cucumber-skill`, `phuryn/test-scenarios` |
| `e2e-test-engineer` | `testmu-ai/playwright-skill`, `openai/playwright`, `testmu-ai/cypress-skill`, `testmu-ai/detox-skill` |
| `unit-test-engineer` | `testmu-ai/pytest-skill`, `testmu-ai/jest-skill`, `testmu-ai/vitest-skill`, `testmu-ai/phpunit-skill`, `trailofbits/property-based-testing` |
| `code-reviewer` | `coderabbitai/code-review`, `getsentry/sentry-pr-code-review`, `garrytan/design-review` |
| `accessibility-tester` | `addyosmani/accessibility`, `addyosmani/web-quality-audit`, `anthropics/frontend-design` |
| `performance-engineer` | `addyosmani/core-web-vitals`, `addyosmani/performance`, `cloudflare/web-perf`, `datadog-labs/dd-apm` |
| `security-auditor` | `openai/security-threat-model`, `openai/security-best-practices`, `trailofbits/static-analysis`, `trailofbits/semgrep-rule-creator`, `getsentry/sentry-fix-issues` |

### 🗄 Data & AI

| Agent | Skills |
|---|---|
| `data-engineer` | `supabase/postgres-best-practices`, `duckdb/query`, `clickhouse/clickhouse-best-practices`, `tinybirdco/tinybird-best-practices`, `trailofbits/modern-python` |
| `data-analyst` | `supabase/postgres-best-practices`, `phuryn/cohort-analysis`, `phuryn/ab-test-analysis`, `dataviz` |
| `ml-engineer` | `google-gemini/gemini-api-dev`, `anthropics/mcp-builder`, `hamelsmu/write-judge-prompt`, `hamelsmu/error-analysis`, `huggingface/hugging-face-model-trainer`, `trailofbits/modern-python` |
| `database-administrator` | `supabase/postgres-best-practices`, `neondatabase/neon-postgres`, `mongodb/mongodb-schema-design`, `mongodb/mongodb-query-optimizer`, `redis/redis-development` |

### ☁️ Infrastructure

| Agent | Skills |
|---|---|
| `devops-engineer` | `hashicorp/terraform-style-guide`, `cloudflare/wrangler`, `openai/vercel-deploy`, `netlify/netlify-cli-and-deploy`, `expo/expo-cicd-workflows`, `getsentry/sentry-create-alert` |
| `cloud-architect` | `microsoft/cloud-solution-architect`, `zxkane/aws-skills`, `cloudflare/workers-best-practices`, `cloudflare/web-perf` |
| `sre-incident-responder` | `datadog-labs/dd-monitors`, `datadog-labs/dd-apm`, `redhat/sre-skillpack`, `getsentry/sentry-create-alert`, `getsentry/sentry-fix-issues` |

### 🎨 Design

| Agent | Skills |
|---|---|
| `ui-designer` | `figma/figma-implement-design`, `figma/figma-generate-design`, `anthropics/canvas-design`, `garrytan/design-consultation` |
| `ux-researcher` | `phuryn/user-personas`, `phuryn/interview-script`, `phuryn/customer-journey-map`, `deanpeters/jobs-to-be-done`, `deanpeters/discovery-interview-prep` |
| `design-system-engineer` | `google-labs-code/shadcn-ui`, `tailwind`, `figma/figma-create-design-system-rules`, `figma/figma-code-connect-components`, `anthropics/frontend-design` |

### 📋 Product & Research

| Agent | Skills |
|---|---|
| `product-owner` | `gsd`, `phuryn/create-prd`, `phuryn/user-stories`, `phuryn/prioritization-frameworks`, `deanpeters/opportunity-solution-tree`, `deanpeters/user-story-splitting`, `jira-ticket-planner` |
| `scrum-master` | `phuryn/sprint-plan`, `phuryn/retro`, `phuryn/release-notes`, `jira-ticket-planner`, `anthropics/doc-coauthoring` |
| `business-analyst` | `phuryn/swot-analysis`, `phuryn/porters-five-forces`, `deanpeters/pestel-analysis`, `anthropics/doc-coauthoring`, `drawio` |
| `market-researcher` | `sanjay3290/deep-research`, `phuryn/market-sizing`, `phuryn/competitor-analysis`, `phuryn/competitive-battlecard`, `deanpeters/company-research`, `brave/web-search` |
| `technical-writer` | `anthropics/doc-coauthoring`, `anthropics/docx`, `makenotion/research-documentation`, `phuryn/release-notes`, `brave/web-search` |
| `seo-specialist` | `addyosmani/seo`, `coreyhaines31/seo-audit`, `coreyhaines31/schema-markup`, `coreyhaines31/site-architecture`, `coreyhaines31/programmatic-seo`, `sanity-io/seo-aeo-best-practices`, `addyosmani/core-web-vitals` |

### 🧭 Meta / Orchestration

| Agent | Skills |
|---|---|
| `company-orchestrator` | `gsd`, `find-subagents`, `select-skills`, `muratcankoylan/multi-agent-patterns`, `anthropics/doc-coauthoring` |
| `context-manager` | `muratcankoylan/context-fundamentals`, `muratcankoylan/context-compression`, `makenotion/knowledge-capture`, `anthropics/doc-coauthoring` |
| `dynamic-agent` | `find-subagents`, `select-skills` |

## Registry skills — install commands (deduplicated)

```bash
npx skills add addyosmani/accessibility
npx skills add addyosmani/core-web-vitals
npx skills add addyosmani/performance
npx skills add addyosmani/seo
npx skills add addyosmani/web-quality-audit
npx skills add anthropics/canvas-design
npx skills add anthropics/doc-coauthoring
npx skills add anthropics/docx
npx skills add anthropics/frontend-design
npx skills add anthropics/mcp-builder
npx skills add anthropics/webapp-testing
npx skills add apollographql/apollo-server
npx skills add apollographql/graphql-schema
npx skills add auth0/auth0-nextjs
npx skills add auth0/auth0-react
npx skills add auth0/auth0-react-native
npx skills add better-auth/best-practices
npx skills add brave/web-search
npx skills add callstackincubator/react-native-best-practices
npx skills add clickhouse/clickhouse-best-practices
npx skills add cloudflare/web-perf
npx skills add cloudflare/workers-best-practices
npx skills add cloudflare/wrangler
npx skills add coderabbitai/code-review
npx skills add coreyhaines31/programmatic-seo
npx skills add coreyhaines31/schema-markup
npx skills add coreyhaines31/seo-audit
npx skills add coreyhaines31/site-architecture
npx skills add datadog-labs/dd-apm
npx skills add datadog-labs/dd-monitors
npx skills add deanpeters/company-research
npx skills add deanpeters/discovery-interview-prep
npx skills add deanpeters/jobs-to-be-done
npx skills add deanpeters/opportunity-solution-tree
npx skills add deanpeters/pestel-analysis
npx skills add deanpeters/user-story-splitting
npx skills add duckdb/query
npx skills add expo/building-native-ui
npx skills add expo/expo-cicd-workflows
npx skills add expo/expo-deployment
npx skills add expo/expo-tailwind-setup
npx skills add expo/native-data-fetching
npx skills add figma/figma-code-connect-components
npx skills add figma/figma-create-design-system-rules
npx skills add figma/figma-generate-design
npx skills add figma/figma-implement-design
npx skills add garrytan/design-consultation
npx skills add garrytan/design-review
npx skills add getsentry/sentry-code-review
npx skills add getsentry/sentry-create-alert
npx skills add getsentry/sentry-fix-issues
npx skills add getsentry/sentry-nestjs-sdk
npx skills add getsentry/sentry-nextjs-sdk
npx skills add getsentry/sentry-php-sdk
npx skills add getsentry/sentry-pr-code-review
npx skills add getsentry/sentry-python-sdk
npx skills add getsentry/sentry-react-native-sdk
npx skills add getsentry/sentry-react-sdk
npx skills add google-gemini/gemini-api-dev
npx skills add google-labs-code/react-components
npx skills add google-labs-code/shadcn-ui
npx skills add hamelsmu/error-analysis
npx skills add hamelsmu/write-judge-prompt
npx skills add hashicorp/terraform-style-guide
npx skills add huggingface/hugging-face-model-trainer
npx skills add makenotion/knowledge-capture
npx skills add makenotion/research-documentation
npx skills add microsoft/cloud-solution-architect
npx skills add microsoft/fastapi-router-py
npx skills add microsoft/pydantic-models-py
npx skills add microsoft/zustand-store-ts
npx skills add mongodb/mongodb-query-optimizer
npx skills add mongodb/mongodb-schema-design
npx skills add muratcankoylan/context-compression
npx skills add muratcankoylan/context-fundamentals
npx skills add muratcankoylan/multi-agent-patterns
npx skills add neondatabase/neon-postgres
npx skills add netlify/netlify-cli-and-deploy
npx skills add openai/playwright
npx skills add openai/security-best-practices
npx skills add openai/security-threat-model
npx skills add openai/vercel-deploy
npx skills add phuryn/ab-test-analysis
npx skills add phuryn/cohort-analysis
npx skills add phuryn/competitive-battlecard
npx skills add phuryn/competitor-analysis
npx skills add phuryn/create-prd
npx skills add phuryn/customer-journey-map
npx skills add phuryn/interview-script
npx skills add phuryn/market-sizing
npx skills add phuryn/porters-five-forces
npx skills add phuryn/prioritization-frameworks
npx skills add phuryn/release-notes
npx skills add phuryn/retro
npx skills add phuryn/sprint-plan
npx skills add phuryn/swot-analysis
npx skills add phuryn/test-scenarios
npx skills add phuryn/user-personas
npx skills add phuryn/user-stories
npx skills add redhat/sre-skillpack
npx skills add redis/redis-development
npx skills add sanity-io/seo-aeo-best-practices
npx skills add sanjay3290/deep-research
npx skills add stripe/stripe-best-practices
npx skills add supabase/postgres-best-practices
npx skills add testmu-ai/cucumber-skill
npx skills add testmu-ai/cypress-skill
npx skills add testmu-ai/detox-skill
npx skills add testmu-ai/jest-skill
npx skills add testmu-ai/laravel-dusk-skill
npx skills add testmu-ai/phpunit-skill
npx skills add testmu-ai/playwright-skill
npx skills add testmu-ai/pytest-skill
npx skills add testmu-ai/vitest-skill
npx skills add tinybirdco/tinybird-best-practices
npx skills add trailofbits/modern-python
npx skills add trailofbits/property-based-testing
npx skills add trailofbits/semgrep-rule-creator
npx skills add trailofbits/static-analysis
npx skills add vercel-labs/next-best-practices
npx skills add vercel-labs/next-cache-components
npx skills add zxkane/aws-skills
```

## Local skills (authored in this repo, distributed by `install.sh`)

- `find-subagents` — `skills/find-subagents/SKILL.md`
- `select-skills` — `skills/select-skills/SKILL.md`
- `tailwind` — `skills/tailwind/SKILL.md`

## Framework skills (own installer)

- `gsd` — the [GSD](https://github.com/shoootyou/get-shit-done-multi) spec-driven workflow. Install with `bash scaffold/install-gsd.sh`.

## Bundled skills (provided by the harness — no install)

- `dataviz`
- `drawio`
- `jira-ticket-planner`

> Totals: 122 registry + 3 local + 1 framework + 3 bundled skills across 35 agents.
