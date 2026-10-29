# 别在我的文案里拉屎

中文 | [English](README.en.md) | [日本語](README.ja.md)

<p>
  <img alt="npx skills" src="https://img.shields.io/badge/npx-skills-000?style=flat-square">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green?style=flat-square">
  <img alt="languages" src="https://img.shields.io/badge/languages-中文%20%7C%20English%20%7C%20日本語-blue?style=flat-square">
</p>

给文案、文档、README、代码注释和小说做 AI 味检查的 skill。中文、English、日本語。

## 安装

### npx skills（推荐）

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text --skill stop-shitting-in-my-text
```

全局安装，并指定 agent：

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text \
  --skill stop-shitting-in-my-text -g -a claude-code -y
```

`skills` 会克隆仓库，找到根目录的 `SKILL.md`，复制到对应 agent 的 skills 目录。已在 `skills@1.7.4` 验证：找到 1 个 skill，安装到 `.claude/skills/stop-shitting-in-my-text`。安装后重启会话，让 agent 重新扫描。

### git clone

```bash
git clone https://github.com/LaokeQwQ/stop-shitting-in-my-text.git \
  ~/.agents/skills/stop-shitting-in-my-text
```

任何读取 `SKILL.md` 的 agent 都可以用这种方式。

## 它抓什么

| 类别 | 例子 | 级别 |
|---|---|---|
| 黑话、空话 | 赋能、闭环、抓手、一站式 | block |
| 假转折 | 成本低，但效率高 | warn |
| 凭空否定 | 前文没提 A，却写“这不是 A，而是 B” | warn |
| 翻译腔 | 基于用户反馈，我们拆解了三个问题 | block |
| 过度安抚 | 主动权在你、随时可以修改 | block |
| 事故报告腔 | 当前所有进程已停止，下一步只做恢复 | block |
| 过程表演 | 探针、快照、门禁、89 个门禁、12 小时只转移 3/10,000 | block/warn |
| 紫色散文 | 神明、宠溺、手术刀、极其极其 | block |
| 技术文档情绪价值 | 欢迎来到、希望你喜欢、加油 | warn |
| 小说 POV | 全知叙述、简历式前史、场景硬跳 | warn |
| 小说语言 | 颤抖的体温、混乱有序、鲨鱼夹碎发 | warn |
| 小说结构 | 600 字没有对话或场景切换，剧情没动 | warn |

## Before / After

| Before | After |
|---|---|
| 这不是效率问题，而是管理问题。 | 审批链有三个人签字，没人负责。 |
| 基于用户反馈，我们拆解了三个问题。 | 我们看了用户反馈，把问题分成三块。 |
| 她颤抖的体温贴着他。 | 她的手贴着他，指尖在抖。 |
| 当前所有进程已停止。下一步只做恢复。 | 已经改回去了。 |

## 三种模式

| 模式 | 命令 | 范围 |
|---|---|---|
| 文案 | `python3 scripts/scan.py draft.md` | 文档、README、邮件、公众号、产品文案 |
| 代码 | `python3 scripts/scan.py --code src/foo.py` | 注释、docstring、用户可见字符串 |
| 小说 | `python3 scripts/scan.py --fiction novel.md` | POV、结构、语言、17+8 条规则 |

其他参数：

```bash
python3 scripts/scan.py --changed
python3 scripts/scan.py --context prompt.txt draft.md
python3 scripts/scan.py --lang zh|en|ja draft.md
python3 scripts/scan.py --format json draft.md
python3 scripts/scan.py --fail-on warn draft.md
```

## 输出级别

| 级别 | 处理 |
|---|---|
| `block` | 交付前改到 0 |
| `warn` | 逐条判断；保留时写理由 |
| `hint` | 标点、空格、节奏；不阻塞 |

## 规则

- `scripts/lexicon.py`：中英日规则表，可编辑。
- `references/tells-zh.md`：中文 AI 痕迹。
- `references/tells-en.md`：English AI-writing tells。
- `references/tells-ja.md`：日本語のAIっぽさ。
- `references/fiction-tells.md`：小说 17 条 + 9 条补充。
- `references/plain-language.md`：通用文字卫生清单。
- `references/localization-zh.md`：中文本地化。
- `references/cases.md`：逐条情形和 before/after。
- `references/rewrite-recipes.md`：改写动作。

## 验证

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text --list
python3 scripts/scan.py --list-rules
python3 scripts/scan.py --list-rules --fiction
```

`npx skills add` 在 `skills@1.7.4` 下找到 1 个 skill。`evals/evals.json` 有 34 条测试提示，覆盖中英日、文案、代码、小说、否定句、技术文档和事故腔。`SKILL.md` 自扫 block 0。

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

## License

MIT
