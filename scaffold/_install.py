#!/usr/bin/env python3
"""
Install the subagent fleet into multiple AI coding harnesses.

Source of truth: the Claude-Code-style markdown files in agents/**/*.md.
For each target harness the agent is written in that harness's native shape:

  Claude Code  ~/.claude/agents/<dept>/<name>.md      markdown + frontmatter (verbatim)
  opencode     ~/.config/opencode/agent/<name>.md      markdown + opencode frontmatter
  Codex        ~/.codex/agents/<name>.toml             TOML (best-effort conversion)
  pi           ~/.pi/agent/prompts/<name>.md           markdown prompt template

Project mode (--project) writes to the equivalent in-repo dirs where the harness
supports it (.claude/agents, .opencode/agent, .pi/prompts). Codex agents are
global-only, so --project falls back to the global Codex dir with a note.

Format conversions for opencode/Codex/pi are best-effort: the exact frontmatter/
schema each harness accepts evolves, and models are left to each harness's default
rather than hard-coding possibly-stale model ids. The Claude Code install is exact.
"""
import argparse
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(ROOT, "agents")
SKILLS_DIR = os.path.join(ROOT, "skills")
HOME = os.path.expanduser("~")


def parse_agent(path):
    with open(path) as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError(f"No frontmatter in {path}")
    raw_fm, body = m.group(1), m.group(2).lstrip("\n")
    fm = {"skills": []}
    in_skills = False
    for line in raw_fm.splitlines():
        if line.startswith("skills:"):
            in_skills = True
            continue
        if in_skills:
            sm = re.match(r"\s*-\s*(.+)$", line)
            if sm:
                fm["skills"].append(sm.group(1).strip())
                continue
            in_skills = False
        km = re.match(r"^(\w+):\s*(.*)$", line)
        if km:
            key, val = km.group(1), km.group(2).strip()
            fm[key] = val.strip('"')
    return fm, body, text


def collect_agents():
    out = []
    for dept in sorted(os.listdir(AGENTS_DIR)):
        d = os.path.join(AGENTS_DIR, dept)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".md"):
                out.append((dept, os.path.join(d, fn)))
    return out


def collect_local_skills():
    """Repo-authored skills: skills/<slug>/ dirs containing a SKILL.md."""
    if not os.path.isdir(SKILLS_DIR):
        return []
    return [
        (slug, os.path.join(SKILLS_DIR, slug))
        for slug in sorted(os.listdir(SKILLS_DIR))
        if os.path.isfile(os.path.join(SKILLS_DIR, slug, "SKILL.md"))
    ]


# ── format converters ─────────────────────────────────────────────────────
def to_claude(fm, body, raw):
    return raw  # verbatim — this is the native format


def to_opencode(fm, body, raw):
    fmt = [
        "---",
        f'description: "{fm.get("description", "").replace(chr(34), chr(39))}"',
        "mode: subagent",
        "---",
        "",
    ]
    return "\n".join(fmt) + body


def to_codex_toml(fm, body, raw):
    def esc(s):
        return s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    lines = [
        f'name = "{fm.get("name", "")}"',
        f'description = "{fm.get("description", "").replace(chr(34), chr(39))}"',
        "# model: set to a Codex-supported model id if you want to pin one",
        'instructions = """',
        esc(body).rstrip(),
        '"""',
        "",
    ]
    return "\n".join(lines)


def to_pi_prompt(fm, body, raw):
    header = [
        "---",
        f'description: "{fm.get("description", "").replace(chr(34), chr(39))}"',
        "---",
        "",
    ]
    return "\n".join(header) + body


# ── target definitions ────────────────────────────────────────────────────
def target_specs(project):
    return {
        "claude": {
            "label": "Claude Code",
            "base": os.path.join(ROOT, ".claude", "agents") if project else os.path.join(HOME, ".claude", "agents"),
            "skill_base": os.path.join(ROOT, ".claude", "skills") if project else os.path.join(HOME, ".claude", "skills"),
            "nested": True,
            "ext": ".md",
            "convert": to_claude,
            "project_ok": True,
        },
        "opencode": {
            "label": "opencode",
            "base": os.path.join(ROOT, ".opencode", "agent") if project else os.path.join(HOME, ".config", "opencode", "agent"),
            "skill_base": os.path.join(ROOT, ".opencode", "skill") if project else os.path.join(HOME, ".config", "opencode", "skill"),
            "nested": False,
            "ext": ".md",
            "convert": to_opencode,
            "project_ok": True,
        },
        "codex": {
            "label": "Codex",
            "base": os.path.join(HOME, ".codex", "agents"),  # Codex agents are global-only
            "skill_base": os.path.join(HOME, ".codex", "skills"),
            "nested": False,
            "ext": ".toml",
            "convert": to_codex_toml,
            "project_ok": False,
        },
        "pi": {
            "label": "pi",
            "base": os.path.join(ROOT, ".pi", "prompts") if project else os.path.join(HOME, ".pi", "agent", "prompts"),
            "skill_base": os.path.join(ROOT, ".pi", "skills") if project else os.path.join(HOME, ".pi", "agent", "skills"),
            "nested": False,
            "ext": ".md",
            "convert": to_pi_prompt,
            "project_ok": True,
        },
    }


def install_target(key, spec, agents, dry_run, project):
    if project and not spec["project_ok"]:
        print(f"  ! {spec['label']}: agents are global-only — using {spec['base']}")
    print(f"\n== {spec['label']} → {spec['base']}")
    n = 0
    for dept, path in agents:
        fm, body, raw = parse_agent(path)
        name = fm.get("name") or os.path.splitext(os.path.basename(path))[0]
        if spec["nested"]:
            dest_dir = os.path.join(spec["base"], dept)
        else:
            dest_dir = spec["base"]
        dest = os.path.join(dest_dir, name + spec["ext"])
        content = spec["convert"](fm, body, raw)
        rel = os.path.relpath(dest, HOME)
        if dry_run:
            print(f"  would write ~/{rel}")
        else:
            os.makedirs(dest_dir, exist_ok=True)
            with open(dest, "w") as f:
                f.write(content)
            print(f"  ✓ {name}{spec['ext']}")
        n += 1
    print(f"  {'would install' if dry_run else 'installed'} {n} agents")
    return n


def install_local_skills(spec, skills, dry_run):
    """Copy repo-authored skills/<slug>/ into a harness's skills dir."""
    if not skills:
        return 0
    base = spec["skill_base"]
    for slug, src in skills:
        dest = os.path.join(base, slug)
        rel = os.path.relpath(dest, HOME)
        if dry_run:
            print(f"  would copy skill → ~/{rel}/")
        else:
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            print(f"  ✓ skill {slug}/")
    print(f"  {'would install' if dry_run else 'installed'} {len(skills)} local skill(s)")
    return len(skills)


def main():
    ap = argparse.ArgumentParser(description="Install the subagent fleet into AI coding harnesses.")
    ap.add_argument("--claude", action="store_true")
    ap.add_argument("--opencode", action="store_true")
    ap.add_argument("--codex", action="store_true")
    ap.add_argument("--pi", action="store_true")
    ap.add_argument("--all", action="store_true", help="all four harnesses (default if none specified)")
    ap.add_argument("--project", action="store_true", help="install into this repo instead of the home dir")
    ap.add_argument("--dry-run", action="store_true", help="print what would be written, write nothing")
    ap.add_argument("--no-skills", action="store_true", help="skip installing repo-authored local skills")
    args = ap.parse_args()

    selected = [k for k in ("claude", "opencode", "codex", "pi") if getattr(args, k)]
    if args.all or not selected:
        selected = ["claude", "opencode", "codex", "pi"]

    agents = collect_agents()
    if not agents:
        print("No agents found under agents/. Run: python3 scaffold/generate.py", file=sys.stderr)
        sys.exit(1)
    skills = [] if args.no_skills else collect_local_skills()

    specs = target_specs(args.project)
    print(f"Fleet: {len(agents)} agents + {len(skills)} local skill(s) → "
          f"{', '.join(specs[k]['label'] for k in selected)}"
          + ("  (dry run)" if args.dry_run else "") + ("  [project]" if args.project else "  [global]"))
    total = 0
    for k in selected:
        total += install_target(k, specs[k], agents, args.dry_run, args.project)
        install_local_skills(specs[k], skills, args.dry_run)
    print(f"\nDone. {total} agent installs across {len(selected)} harness(es).")


if __name__ == "__main__":
    main()
