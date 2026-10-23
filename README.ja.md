# 私の文章でクソをするな

[中文](README.md) | [English](README.en.md) | 日本語

文案・ドキュメント・README・コードコメント・小説のAIっぽさを検査するskillです。中国語・英語・日本語に対応しています。

## できること

- 草稿のAIっぽさを検査します。空疎な語彙、定型構文、偽の対比、翻訳調、過剰な安心させ方、事故報告のような文体、小説のPOVと語の誤りが対象です。
- 制約をプロジェクトの `AGENTS.md` または既存の制約ドキュメントに書き込みます。
- そのターンで変更した文章、コードコメント、小説を納品前に再検査します。
- モードは三つです。通常の文章、コードコメントと文字列、小説。

## インストール

```bash
git clone https://github.com/LaokeQwQ/stop-shitting-in-my-text.git \
  ~/.agents/skills/stop-shitting-in-my-text
```

agentが別のskillsディレクトリを使う場合は、そこに置いてください。

## 使い方

```bash
# 通常の文章
python3 scripts/scan.py draft.md

# コードコメント、docstring、ユーザーに見える文字列
python3 scripts/scan.py --code src/foo.py src/bar.ts

# 小説
python3 scripts/scan.py --fiction novel.md

# gitの変更だけ
python3 scripts/scan.py --changed

# ユーザーの入力を渡して、根拠のない否定を検査
python3 scripts/scan.py --context prompt.txt draft.md
```

言語:

```bash
python3 scripts/scan.py --lang zh draft.md
python3 scripts/scan.py --lang en draft.md
python3 scripts/scan.py --lang ja draft.md
```

既定は `--lang auto` です。

出力形式は `text`、`markdown`、`json` です。失敗の基準は `--fail-on block|warn|hint|never` で変えられます。

## 出力レベル

- `block`: 納品前に0にします。
- `warn`: 一件ずつ判断します。残す場合は理由を書きます。
- `hint`: 句読点、空白、リズム。納品は止めません。

## ルール

- `scripts/lexicon.py`: 中国語・英語・日本語のルール表。編集できます。
- `references/tells-zh.md`: 中国語のAIっぽさ。
- `references/tells-en.md`: 英語のAIっぽさ。
- `references/tells-ja.md`: 日本語のAIっぽさ。
- `references/fiction-tells.md`: 小説のルール17件と補足8件。
- `references/plain-language.md`: 一般的な文章チェック10件。
- `references/localization-zh.md`: 中国語のローカライズ。
- `references/cases.md`: ケース別の例とbefore/after。
- `references/rewrite-recipes.md`: 書き換えの手順。

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

## 検証

```bash
python3 scripts/scan.py --list-rules
python3 scripts/scan.py --list-rules --fiction
```

`evals/evals.json` に31件のテスト用プロンプトがあります。中国語、英語、日本語、通常の文章、コード、小説、否定、技術文書、事故報告のような文体を対象にしています。

## License

MIT
