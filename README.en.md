# Stop Shitting in My Text

[中文](README.md) | English | [日本語](README.ja.md)

A skill that checks copy, docs, READMEs, code comments, and fiction for AI-writing tells. It supports Chinese, English, and Japanese.

## What it does

- Scans drafts for empty vocabulary, template syntax, fake contrasts, translationese, reassurance, incident-report theater, and fiction POV or language errors.
- Writes the constraints into the project's `AGENTS.md` or an existing constraint document.
- Re-audits every text file, code comment, and fiction draft changed in the current turn.
- Three modes: prose, code comments and strings, fiction.

## Install

```bash
git clone https://github.com/LaokeQwQ/stop-shitting-in-my-text.git \
  ~/.agents/skills/stop-shitting-in-my-text
```

If your agent uses a different skills directory, put the repository there.

## Usage

```bash
# Prose
python3 scripts/scan.py draft.md

# Code comments, docstrings, and user-visible strings
python3 scripts/scan.py --code src/foo.py src/bar.ts

# Fiction
python3 scripts/scan.py --fiction novel.md

# Only git changes
python3 scripts/scan.py --changed

# Pass the user's prompt as context for negation checks
python3 scripts/scan.py --context prompt.txt draft.md
```

Language:

```bash
python3 scripts/scan.py --lang zh draft.md
python3 scripts/scan.py --lang en draft.md
python3 scripts/scan.py --lang ja draft.md
```

The default is `--lang auto`.

Output formats: `text`, `markdown`, `json`. Failure threshold: `--fail-on block|warn|hint|never`.

## Levels

- `block`: must be zero before delivery.
- `warn`: judge each hit; explain any that remain.
- `hint`: punctuation, spacing, rhythm; non-blocking.

## Rules

- `scripts/lexicon.py`: editable rule table for Chinese, English, and Japanese.
- `references/tells-zh.md`: Chinese AI tells.
- `references/tells-en.md`: English AI-writing tells.
- `references/tells-ja.md`: Japanese AI tells.
- `references/fiction-tells.md`: 17 fiction rules plus 8 supplements.
- `references/plain-language.md`: 10 general plain-language checks.
- `references/localization-zh.md`: Chinese localization.
- `references/cases.md`: case-by-case examples and before/after.
- `references/rewrite-recipes.md`: rewrite moves.

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

## Verification

```bash
python3 scripts/scan.py --list-rules
python3 scripts/scan.py --list-rules --fiction
```

`evals/evals.json` contains 31 test prompts covering Chinese, English, Japanese, prose, code, fiction, negation, technical docs, and incident-report tone.

## License

MIT
