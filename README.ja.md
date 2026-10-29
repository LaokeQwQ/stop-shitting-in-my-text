# 私の文章でクソをするな

[中文](README.md) | [English](README.en.md) | 日本語

<p>
  <img alt="npx skills" src="https://img.shields.io/badge/npx-skills-000?style=flat-square">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green?style=flat-square">
  <img alt="languages" src="https://img.shields.io/badge/languages-中文%20%7C%20English%20%7C%20日本語-blue?style=flat-square">
</p>

文案・ドキュメント・README・コードコメント・小説のAIっぽさを検査するskillです。中国語・英語・日本語に対応しています。

## インストール

### npx skills（推奨）

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text --skill stop-shitting-in-my-text
```

グローバルに入れて、agentを指定する場合:

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text \
  --skill stop-shitting-in-my-text -g -a claude-code -y
```

`skills` はリポジトリをcloneし、ルートの `SKILL.md` を見つけて、agentのskillsディレクトリへコピーします。`skills@1.7.4` で確認済みです。skillが1件見つかり、`.claude/skills/stop-shitting-in-my-text` へ入りました。インストール後にセッションを再起動すると、agentがskillsを読み直します。

### git clone

```bash
git clone https://github.com/LaokeQwQ/stop-shitting-in-my-text.git \
  ~/.agents/skills/stop-shitting-in-my-text
```

`SKILL.md` を読むagentなら、この方法でも使えます。

## 検査するもの

| 種類 | 例 | レベル |
|---|---|---|
| 空疎な語彙 | ソリューション、シームレス、圧倒的 | warn/block |
| 偽の対比 | コストは低いが、効率は高い。 | warn |
| 根拠のない否定 | 前文にAがないのに「AではなくB」と書く | warn |
| 翻訳調 | ユーザーの声をもとに、課題を三つに分解しました。 | block |
| 過剰な安心させ方 | ご安心ください。いつでも変更できます。 | block |
| 事故報告のような文体 | すべてのプロセスが停止しました。次は復旧だけです。 | block |
| プロセス劇 | 探針、スナップショット、ゲート、89件のチェック、12時間で3/10,000本 | block/warn |
| 紫色の散文 | 神、寵愛、メス、极其极其 | block |
| 技術文書の情緒 | ようこそ。楽しんで使ってください。 | warn |
| 小説のPOV | 全知の語り、履歴書のような過去、場面の唐突な切り替え | warn |
| 小説の言葉 | 震える体温、混沌とした秩序、鯊魚夾の髪 | warn |
| 小説の構成 | 600字で会話も場面転換もなく、物語が動かない | warn |

## Before / After

| Before | After |
|---|---|
| これは効率の問題ではなく、管理の問題です。 | 承認には三人の署名が必要で、責任者がいません。 |
| ユーザーの声をもとに、課題を三つに分解しました。 | ユーザーの声を読み、課題を三つに分けました。 |
| 彼女は震える体温を彼に押し当てた。 | 彼女の手が彼に触れた。指先が震えていた。 |
| すべてのプロセスが停止しました。次は復旧だけです。 | 元に戻しました。 |

## モード

| モード | コマンド | 対象 |
|---|---|---|
| 通常の文章 | `python3 scripts/scan.py draft.md` | ドキュメント、README、メール、文案 |
| コード | `python3 scripts/scan.py --code src/foo.py` | コメント、docstring、ユーザーに見える文字列 |
| 小説 | `python3 scripts/scan.py --fiction novel.md` | POV、構成、言葉、17+8件のルール |

その他のオプション:

```bash
python3 scripts/scan.py --changed
python3 scripts/scan.py --context prompt.txt draft.md
python3 scripts/scan.py --lang zh|en|ja draft.md
python3 scripts/scan.py --format json draft.md
python3 scripts/scan.py --fail-on warn draft.md
```

## レベル

| レベル | 対応 |
|---|---|
| `block` | 納品前に0にします |
| `warn` | 一件ずつ判断します。残す場合は理由を書きます |
| `hint` | 句読点、空白、リズム。納品は止めません |

## ルール

- `scripts/lexicon.py`: 中国語・英語・日本語のルール表。編集できます。
- `references/tells-zh.md`: 中国語のAIっぽさ。
- `references/tells-en.md`: 英語のAIっぽさ。
- `references/tells-ja.md`: 日本語のAIっぽさ。
- `references/fiction-tells.md`: 小説のルール17件と補足9件。
- `references/plain-language.md`: 一般的な文章チェック。
- `references/localization-zh.md`: 中国語のローカライズ。
- `references/cases.md`: ケース別の例とbefore/after。
- `references/rewrite-recipes.md`: 書き換えの手順。

## 検証

```bash
npx skills add LaokeQwQ/stop-shitting-in-my-text --list
python3 scripts/scan.py --list-rules
python3 scripts/scan.py --list-rules --fiction
```

`npx skills add` は `skills@1.7.4` でskillを1件見つけます。`evals/evals.json` に34件のテスト用プロンプトがあります。中国語、英語、日本語、通常の文章、コード、小説、否定、技術文書、事故報告のような文体を対象にしています。`SKILL.md` の自己検査は block 0 です。

## ディレクトリ

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
