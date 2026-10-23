# 别在我的文案里拉屎

中文 | [English](README.en.md) | [日本語](README.ja.md)

一个给文案、文档、README、代码注释和小说做 AI 味检查的 skill。支持中文、English、日本語。

## 它做什么

- 扫描草稿里的 AI 味：空话、套式、假转折、翻译腔、过度安抚、事故报告腔、小说 POV 和语言硬伤。
- 把约束写进项目的 `AGENTS.md` 或现有约束文档。
- 交付前复审本轮改过的文本、代码注释、小说。
- 三种模式：普通文案、代码注释/字符串、小说。

## 安装

```bash
git clone https://github.com/LaokeQwQ/stop-shitting-in-my-text.git \
  ~/.agents/skills/stop-shitting-in-my-text
```

如果你的 agent 使用别的 skills 目录，把仓库放进去。

## 用法

```bash
# 普通文案
python3 scripts/scan.py draft.md

# 代码注释、docstring、用户可见字符串
python3 scripts/scan.py --code src/foo.py src/bar.ts

# 小说
python3 scripts/scan.py --fiction novel.md

# 只扫 git 改动
python3 scripts/scan.py --changed

# 把用户原文作为上下文，检查“凭空否定”
python3 scripts/scan.py --context prompt.txt draft.md
```

语言：

```bash
python3 scripts/scan.py --lang zh draft.md
python3 scripts/scan.py --lang en draft.md
python3 scripts/scan.py --lang ja draft.md
```

默认 `--lang auto`。

输出格式：`text`、`markdown`、`json`。失败阈值：`--fail-on block|warn|hint|never`。

## 输出级别

- `block`：必须改到 0。
- `warn`：逐条判断；保留时说明理由。
- `hint`：标点、空格、节奏；不阻塞。

## 规则

- `scripts/lexicon.py`：可编辑规则表，中文、English、日本語。
- `references/tells-zh.md`：中文 AI 痕迹。
- `references/tells-en.md`：English AI-writing tells。
- `references/tells-ja.md`：日本語のAIっぽさ。
- `references/fiction-tells.md`：小说 17 条 + 8 条补充。
- `references/plain-language.md`：10 条通用文字卫生。
- `references/localization-zh.md`：中文本地化。
- `references/cases.md`：逐条情形和 before/after。
- `references/rewrite-recipes.md`：改写动作。

## 目录

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

## 验证

```bash
python3 scripts/scan.py --list-rules
python3 scripts/scan.py --list-rules --fiction
```

`evals/evals.json` 有 31 条测试提示，覆盖中英日、文案、代码、小说、否定句、技术文档和事故腔。

## License

MIT
