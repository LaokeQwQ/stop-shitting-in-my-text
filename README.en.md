# Stop Shitting in My Text

[中文](README.md) | English | [日本語](README.ja.md)

<p>
  <img alt="npx skills" src="https://img.shields.io/badge/npx-skills-000?style=flat-square">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green?style=flat-square">
  <img alt="languages" src="https://img.shields.io/badge/languages-中文%20%7C%20English%20%7C%20日本語-blue?style=flat-square">
</p>

A skill that checks copy, docs, READMEs, code comments, and fiction for AI-writing tells. Chinese, English, Japanese.

## Install

### npx skills (recommended)

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text --skill stop-shitting-in-my-text
```

Install globally for one agent:

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text \
  --skill stop-shitting-in-my-text -g -a claude-code -y
```

`skills` clones the repository, finds the root `SKILL.md`, and copies the skill into the agent's skills directory. Tested with `skills@1.7.4`: one skill found, installed to `.claude/skills/stop-shitting-in-my-text`. Restart the session so the agent rescans skills.

### git clone

```bash
git clone https://github.com/LaokeQwQ/stop-shitting-in-my-text.git \
  ~/.agents/skills/stop-shitting-in-my-text
```

This works with any agent that reads `SKILL.md`.

## What it catches

| Category | Example | Level |
|---|---|---|
| Buzzwords and empty claims | leverage, seamless, holistic | warn/block |
| Fake contrast | Cost is low, but efficiency is high. | warn |
| Unmotivated negation | "This is not a management problem, but a process problem" with no prior mention of A | warn |
| Translationese | Based on user feedback, we broke down three issues. | block |
| Reassurance | You're in control. Feel free to modify this. | block |
| Incident-report theater | All processes have stopped. Next step is recovery only. | block |
| Emotional value in docs | Welcome to SuperTool! Happy coding! | warn |
| Fiction POV | Omniscient narration, resume-style backstory, hard scene jump | warn |
| Fiction language | trembling body temperature, chaotic order, shark-clip hair | warn |
| Fiction structure | 600 words with no dialogue, scene break, or plot change | warn |

## Before / After

| Before | After |
|---|---|
| This is not an efficiency problem, it is a management problem. | Three people sign the approval. Nobody owns it. |
| Based on user feedback, we broke down three issues. | We read the feedback and split the issues into three groups. |
| She pressed her trembling body temperature against him. | Her hand rested on him. Her fingertips shook. |
| All processes have stopped. The next step is recovery only. | Reverted. |

## Modes

| Mode | Command | Scope |
|---|---|---|
| Prose | `python3 scripts/scan.py draft.md` | Docs, READMEs, email, product copy |
| Code | `python3 scripts/scan.py --code src/foo.py` | Comments, docstrings, user-visible strings |
| Fiction | `python3 scripts/scan.py --fiction novel.md` | POV, structure, language, 17+8 rules |

Other options:

```bash
python3 scripts/scan.py --changed
python3 scripts/scan.py --context prompt.txt draft.md
python3 scripts/scan.py --lang zh|en|ja draft.md
python3 scripts/scan.py --format json draft.md
python3 scripts/scan.py --fail-on warn draft.md
```

## Levels

| Level | Action |
|---|---|
| `block` | Fix to zero before delivery |
| `warn` | Judge each hit; explain any that remain |
| `hint` | Punctuation, spacing, rhythm; non-blocking |

## Rules

- `scripts/lexicon.py`: editable rules for Chinese, English, Japanese.
- `references/tells-zh.md`: Chinese AI tells.
- `references/tells-en.md`: English AI-writing tells.
- `references/tells-ja.md`: Japanese AI tells.
- `references/fiction-tells.md`: 17 fiction rules plus 8 supplements.
- `references/plain-language.md`: 10 general plain-language checks.
- `references/localization-zh.md`: Chinese localization.
- `references/cases.md`: case-by-case examples and before/after.
- `references/rewrite-recipes.md`: rewrite moves.

## Verification

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text --list
python3 scripts/scan.py --list-rules
python3 scripts/scan.py --list-rules --fiction
```

`npx skills add` finds one skill under `skills@1.7.4`. `evals/evals.json` has 31 prompts covering Chinese, English, Japanese, prose, code, fiction, negation, technical docs, and incident-report tone. Self-scan of `SKILL.md`: block 0.

## Layout

```text
.
├── SKILL.md
├── README.md
├── README.en.md
├── README.ja.md
├── scripts/
│   ├── scan.py
│   ├── lexicon.py
│   └── install_rules.py
├── references/
│   ├── cases.md
│   ├── fiction-tells.md
│   ├── localization-zh.md
│   ├── plain-language.md
│   ├── rewrite-recipes.md
│   ├── scenarios.md
│   ├── tells-en.md
│   ├── tells-ja.md
│   └── tells-zh.md
└── evals/
    └── evals.json
```

## License

MIT
