#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan prose for AI-writing tells.

Usage:
    scan.py draft.md
    scan.py --changed
    scan.py --format json draft.md
    printf '...' | scan.py

Exit codes: 0 clean at the chosen threshold, 1 threshold hit, 2 input error.

The scanner masks code fences, inline code, HTML comments, quoted lines, URLs,
YAML frontmatter, this skill's managed rules block, and ssimt:off regions.
Everything else is fair game: a rule hit is evidence, not a verdict.
"""

import argparse
import bisect
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from lexicon import FICTION_RULES, METRICS, RULES  # noqa: E402

TEXT_EXT = {
    ".md", ".markdown", ".mdx", ".txt", ".text", ".rst", ".adoc", ".org",
    ".tex", ".html", ".htm",
}
CODE_HASH = {
    ".py", ".pyw", ".sh", ".bash", ".zsh", ".rb", ".yaml", ".yml", ".toml",
    ".r", ".pl", ".ps1",
}
CODE_SLASH = {
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".go", ".rs", ".java",
    ".kt", ".kts", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".cs",
    ".swift", ".php", ".scala", ".dart", ".m", ".mm",
}
CODE_HTML = {".html", ".htm", ".xml", ".svg", ".vue", ".svelte"}
CODE_CSS = {".css", ".scss", ".less"}
CODE_SQL = {".sql"}
CODE_EXT = CODE_HASH | CODE_SLASH | CODE_HTML | CODE_CSS | CODE_SQL
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build",
    "target", ".venv", "venv", "__pycache__", ".next", ".nuxt", ".cache",
    "site-packages", "Pods", "DerivedData",
}
SEV_RANK = {"hint": 1, "warn": 2, "block": 3}
SEV_LABEL = {"block": "BLOCK", "warn": "WARN", "hint": "HINT"}

MASK_PATTERNS = [
    # Meta blocks written by this skill: rules, not prose.
    (r"<!--\s*stop-shitting-in-my-text:begin\b.*?-->.*?<!--\s*stop-shitting-in-my-text:end\s*-->", re.S),
    # Explicit opt-out regions.
    (r"<!--\s*ssimt:off\s*-->.*?(?:<!--\s*ssimt:on\s*-->|\Z)", re.S),
    # YAML frontmatter. Line-bounded: a dot-star repeat here backtracks
    # exponentially on long documents and hangs the scanner.
    (r"\A---[ \t]*\n(?:[^\n]*\n){0,200}?---[ \t]*(?:\n|\Z)", 0),
    (r"```.*?```", re.S),
    (r"~~~.*?~~~", re.S),
    (r"<!--.*?-->", re.S),
    (r"`[^`\n]+`", 0),
    (r"<(?:https?|mailto):[^>\s]+>", 0),
    (r"https?://[^\s)>\]}]+", 0),
    (r"(?m)^\s{0,3}>.*$", 0),
]


# --------------------------------------------------------------------- text

def mask_spans(text, spans):
    """Blank the given spans while preserving offsets and newlines."""
    if not spans:
        return text

    spans = sorted(spans)
    merged = []
    for start, end in spans:
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    out = []
    pos = 0
    for start, end in merged:
        out.append(text[pos:start])
        out.append(re.sub(r"[^\n]", " ", text[start:end]))
        pos = end
    out.append(text[pos:])
    return "".join(out)


def keep_spans(text, spans):
    """Blank everything outside the given spans, keeping offsets."""
    spans = sorted(spans)
    merged = []
    for start, end in spans:
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    out = []
    pos = 0
    for start, end in merged:
        out.append(re.sub(r"[^\n]", " ", text[pos:start]))
        out.append(text[start:end])
        pos = end
    out.append(re.sub(r"[^\n]", " ", text[pos:]))
    return "".join(out)


def mask_text(text):
    """Blank out non-prose regions while preserving offsets and newlines."""
    spans = []
    for pattern, flags in MASK_PATTERNS:
        for m in re.finditer(pattern, text, flags):
            if m.end() > m.start():
                spans.append((m.start(), m.end()))
    return mask_spans(text, spans)


def comment_spans(text, suffix):
    """Approximate the comment/docstring spans of a source file."""
    spans = []
    if suffix in CODE_HASH:
        spans.extend(m.span() for m in re.finditer(r"(?m)#.*$", text))
        if suffix in {".py", ".pyw"}:
            spans.extend(m.span() for m in re.finditer(
                r'(?s)""".*?"""|\'\'\'.*?\'\'\'', text))
    elif suffix in CODE_SLASH:
        for m in re.finditer(r"(?m)//.*$", text):
            line_start = text.rfind("\n", 0, m.start()) + 1
            if text[line_start:m.start()].rstrip().endswith(":"):
                continue  # http:// inside a string
            spans.append(m.span())
        spans.extend(m.span() for m in re.finditer(r"(?s)/\*.*?\*/", text))
    elif suffix in CODE_HTML:
        spans.extend(m.span() for m in re.finditer(r"(?s)<!--.*?-->", text))
    elif suffix in CODE_CSS:
        spans.extend(m.span() for m in re.finditer(r"(?s)/\*.*?\*/", text))
    elif suffix in CODE_SQL:
        spans.extend(m.span() for m in re.finditer(r"(?m)--.*$", text))
        spans.extend(m.span() for m in re.finditer(r"(?s)/\*.*?\*/", text))
    return spans


def string_spans(text, suffix):
    """Approximate user-visible string literals in a source file."""
    spans = []
    quoted = r'(?s)"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\''
    if (suffix in CODE_HASH or suffix in CODE_SLASH
            or suffix in CODE_CSS or suffix in CODE_SQL):
        spans.extend(m.span() for m in re.finditer(quoted, text))
    if suffix in {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue",
                  ".svelte", ".go"}:
        spans.extend(m.span() for m in re.finditer(
            r"(?s)`(?:[^`\\]|\\.)*`", text))
    return spans


def mask_code(text, suffix):
    """Keep comments, docstrings, and string literals; blank the code."""
    spans = comment_spans(text, suffix) + string_spans(text, suffix)
    masked = keep_spans(text, spans)
    urls = [m.span() for m in re.finditer(r"https?://[^\s)>\]}]+", masked)]
    return mask_spans(masked, urls)


class Lines:
    def __init__(self, text):
        self.starts = [0] + [m.end() for m in re.finditer(r"\n", text)]

    def line(self, offset):
        return bisect.bisect_right(self.starts, offset)


def excerpt(text, offset, width=96):
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    if end < 0:
        end = len(text)
    line = text[start:end].strip()
    if len(line) <= width:
        return line
    rel = max(0, offset - start)
    left = max(0, rel - width // 2)
    cut = line[left:left + width]
    return ("…" if left else "") + cut + ("…" if left + width < len(line) else "")


def active_langs(text, forced):
    if forced != "auto":
        return {forced}
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    kana = len(re.findall(r"[\u3040-\u30ff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    langs = set()
    if kana >= 10:
        langs.add("ja")
    elif cjk >= 10:
        langs.add("zh")
    if latin >= 20:
        langs.add("en")
    return langs or {"zh"}


def overlaps(a, b):
    return a[0] < b[1] and b[0] < a[1]


# ------------------------------------------------------------------ metrics

def _cv(values):
    if len(values) < 2:
        return 0.0
    mean = sum(values) / float(len(values))
    if not mean:
        return 0.0
    var = sum((v - mean) ** 2 for v in values) / float(len(values))
    return (var ** 0.5) / mean


def metric_findings(masked, units, fiction=False):
    findings = []

    def add(rule, severity, match, why, fix):
        findings.append({
            "rule": rule,
            "severity": severity,
            "category": "节奏",
            "match": match,
            "excerpt": "",
            "why": why,
            "fix": fix,
            "line": 0,
            "column": 0,
            "span": (0, 0),
            "density": 0.0,
        })

    sentences = [
        s.strip() for s in re.split(
            r"(?<=[。！？!?；;])\s*|(?<=[.!?])\s+|\n+", masked
        ) if len(re.sub(r"\s+", "", s.strip())) >= 4
    ]

    if len(sentences) >= METRICS["sentence_min_count"]:
        lengths = [len(re.sub(r"\s+", "", s)) for s in sentences]
        cv = _cv(lengths)
        if cv < METRICS["sentence_cv_min"]:
            add("metric-uniform-rhythm", "warn",
                "句长变异系数 %.2f" % cv,
                "句长过于均匀，读起来像同一台机器在往前走。",
                "连续两个长句后插一个短句；让重要的话单独成句。")

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", masked)
                  if len(p.strip()) >= 20]
    if len(paragraphs) >= METRICS["paragraph_min_count"]:
        cv = _cv([len(re.sub(r"\s+", "", p)) for p in paragraphs])
        if cv < METRICS["paragraph_cv_min"]:
            add("metric-uniform-paragraphs", "hint",
                "段落长度变异系数 %.2f" % cv,
                "段落长度接近，结构像模板。",
                "让复杂的段落长、结论性的段落短；允许一段只有一句。")

    lines = [line for line in masked.splitlines() if line.strip()]
    bullets = [line for line in lines
               if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\S", line)]
    if (len(lines) >= METRICS["list_min_lines"]
            and len(bullets) >= METRICS["list_min_bullets"]
            and len(bullets) / float(len(lines)) >= METRICS["list_ratio_max"]):
        add("metric-listification", "warn",
            "%d/%d 行为列表" % (len(bullets), len(lines)),
            "能写成段落的论证被拆成清单，推理关系消失。",
            "只有真正并列的步骤用列表；有因果和取舍的内容写回段落。")

    bold = re.findall(r"\*\*[^*\n]{1,60}\*\*", masked)
    if (len(bold) >= METRICS["bold_min_count"]
            and len(bold) * 1000.0 / units > METRICS["bold_per_1000_max"]):
        add("metric-bold", "warn",
            "%d 处加粗" % len(bold),
            "强调过多等于没有强调，读者会跳过整页。",
            "一段最多一处加粗，只给真正需要跳读的人。")

    if len(sentences) >= METRICS["transition_min_sentences"]:
        zh_transitions = ("此外", "同时", "因此", "然而", "所以", "另外",
                          "最后", "其次", "首先", "总之", "综上", "更重要的是",
                          "与此同时")
        en_transitions = re.compile(
            r"(?i)^(?:moreover|furthermore|additionally|however|therefore|thus|in addition)\b")
        hits = 0
        for s in sentences:
            head = re.sub(r"^[\s\W_]+", "", s)
            if head.startswith(zh_transitions) or en_transitions.match(head):
                hits += 1
        share = hits / float(len(sentences))
        if hits >= 4 and share >= METRICS["transition_share_max"]:
            add("metric-repeated-openers", "warn",
                "%d/%d 句以过渡词开头" % (hits, len(sentences)),
                "段落靠连接词推进，不靠事实关系。",
                "删掉一半过渡词；相邻句子需要关系时，把关系写进事实。")

    triads = re.findall(r"[：:][^。\n]{0,80}、[^。\n]{0,80}、", masked)
    if len(triads) > METRICS["colon_triad_max"]:
        add("metric-colon-triads", "hint",
            "%d 处冒号三项并列" % len(triads),
            "冒号加三项并列是高频排版习惯，信息密度低。",
            "并列项确实并列就保留；不是就写成句子。")

    similes = re.findall(r"(?:就像|像是|仿佛|犹如|宛如|好似|好比)", masked)
    if len(similes) >= 3:
        add("metric-metaphor-chain", "warn",
            "%d 处比喻" % len(similes),
            "比喻成串出现，读者在追意象，不在看事实。",
            "一段最多一个比喻；其余删掉或写成机制。")

    if fiction and units >= 500:
        dialogue = len(re.findall(r"[“”\"「」]", masked))
        breaks = len(re.findall(r"\n\s*\n", masked))
        if dialogue == 0 and breaks <= 1:
            add("metric-fic-stall", "warn",
                "%d 字无对话或场景切换" % units,
                "篇幅在走，剧情可能没动；读者读完不知道发生了什么变化。",
                "压缩日常流程，跳到有变化的那一刻；或者加一条并行的线。")

    quotes = masked.count("“")
    if quotes >= 6 and quotes * 1000.0 / units > 8:
        add("metric-quote-density", "hint",
            "%d 处引号" % quotes,
            "引号过多，常用词被当成术语。",
            "删掉不必要的引号，只留引用、反讽或真正的术语。")

    return findings


# ------------------------------------------------------------------ scanning


def unmotivated_negation_findings(text, masked, context, lines):
    """Flag negations whose A never appeared before the sentence or in context."""
    findings = []
    patterns = [
        (r"(?:不是|并非)([^。！？\n]{1,20}?)(?:而是|，是)[^。！？\n]{1,25}", 1),
        (r"[^。！？\n]{1,20}?[，,]\s*(?:而)?不是([^。！？\n]{1,20})", 1),
    ]
    for pattern, group in patterns:
        for match in re.finditer(pattern, masked):
            a = match.group(group).strip(" \t，,。！？、；;：:")
            a = re.sub(r"^(?:这|那|一个|一种|这个|那个)", "", a).strip()
            if len(a) < 2:
                continue
            prior = masked[:match.start()] + "\n" + context
            if a in prior:
                continue
            start = match.start()
            findings.append({
                "rule": "zh-unmotivated-negation",
                "severity": "warn",
                "category": "逻辑",
                "match": match.group(0).strip()[:80],
                "excerpt": excerpt(text, start),
                "why": "A 在前文和用户输入里都没出现；读者没往这个方向想，否定像是凭空插进来的。",
                "fix": "删掉否定，直接说 B；A 真出现过时，指出出处再否定。",
                "line": lines.line(start),
                "column": start - text.rfind("\n", 0, start),
                "span": match.span(),
                "density": 0.0,
            })
    return findings


def scan_text(text, path, forced_lang="auto", max_per_rule=20, code=False,
              fiction=False, context=""):
    suffix = Path(path).suffix.lower()
    code_mode = bool(code and suffix in CODE_EXT)
    fiction_mode = bool(fiction and not code_mode)
    masked = mask_code(text, suffix) if code_mode else mask_text(text)
    lines = Lines(text)
    units = max(1, len(re.sub(r"\s+", "", masked)))
    langs = active_langs(masked, forced_lang)

    raw = []
    rules = RULES + (FICTION_RULES if fiction_mode else [])
    for rule in rules:
        if not (set(rule["langs"]) & (langs | {"any"})):
            continue
        try:
            rx = re.compile(rule["pattern"])
        except re.error as exc:
            print("bad pattern %s: %s" % (rule["id"], exc), file=sys.stderr)
            continue

        matches = list(rx.finditer(masked))
        count = len(matches)
        if count < rule["min_count"]:
            continue

        density = count * 1000.0 / units
        max_density = rule.get("max_per_1000")
        severity = rule["severity"]
        if max_density is not None:
            if density <= max_density:
                continue
            if severity == "warn" and density > max_density * 2.5:
                severity = "block"

        for m in matches[:max_per_rule]:
            start, end = m.span()
            raw.append({
                "rule": rule["id"],
                "severity": severity,
                "category": rule["category"],
                "match": m.group(0).strip()[:80],
                "excerpt": excerpt(text, start),
                "why": rule["why"],
                "fix": rule["fix"],
                "line": lines.line(start),
                "column": start - text.rfind("\n", 0, start),
                "span": (start, end),
                "density": round(density, 2),
                "dedupe_with": rule.get("dedupe_with", []),
            })

    # Drop lower-severity duplicate hits (e.g. generic stack vs precise stack).
    kept = []
    raw.sort(key=lambda f: (-SEV_RANK[f["severity"]], f["span"][0],
                            -(f["span"][1] - f["span"][0])))
    for finding in raw:
        ruled_out = False
        for other in kept:
            if other["rule"] in finding["dedupe_with"] and overlaps(
                    finding["span"], other["span"]):
                ruled_out = True
                break
        if not ruled_out:
            kept.append(finding)

    context_findings = unmotivated_negation_findings(text, masked, context, lines)
    if context_findings:
        kept = [f for f in kept if not (
            f["rule"] == "zh-negative-escalation"
            and any(overlaps(f["span"], c["span"]) for c in context_findings))]
        kept.extend(context_findings)
    if not code_mode:
        kept.extend(metric_findings(masked, units, fiction_mode))
    kept.sort(key=lambda f: (f["line"] or 10 ** 9, -SEV_RANK[f["severity"]],
                             f["rule"]))

    counts = {"block": 0, "warn": 0, "hint": 0}
    for finding in kept:
        counts[finding["severity"]] += 1
        finding.pop("dedupe_with", None)

    return {
        "path": path,
        "mode": "code" if code_mode else ("fiction" if fiction_mode else "prose"),
        "units": units,
        "langs": sorted(langs),
        "counts": counts,
        "findings": kept,
    }


def read_text(path):
    data = path.read_bytes()
    if b"\x00" in data[:8192]:
        return None
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def iter_text_files(path, code=False):
    extensions = TEXT_EXT | (CODE_EXT if code else set())
    if path.is_file():
        yield path
        return
    for root, dirs, files in os.walk(str(path)):
        dirs[:] = sorted(d for d in dirs
                         if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(files):
            candidate = Path(root) / name
            if candidate.suffix.lower() in extensions:
                yield candidate


def git_changed(root, code=False):
    proc = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                          capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError("not a git repository: %s" % root)
    top = Path(proc.stdout.decode("utf-8", "replace").strip())

    proc = subprocess.run(
        ["git", "-C", str(top), "status", "--porcelain", "-z",
         "--untracked-files=all"],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip())

    entries = proc.stdout.split(b"\0")
    paths = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        status = entry[:2].decode("utf-8", "replace")
        name = entry[3:].decode("utf-8", "replace")
        if "R" in status or "C" in status:
            index += 1  # the next NUL entry is the original path
        if "D" in status:
            continue
        candidate = top / name
        extensions = TEXT_EXT | (CODE_EXT if code else set())
        if candidate.is_file() and candidate.suffix.lower() in extensions:
            paths.append(candidate)
    return paths


# ------------------------------------------------------------------- output

def render_text(results):
    chunks = []
    for result in results:
        counts = result["counts"]
        mode = result.get("mode")
        label = "（代码）" if mode == "code" else ("（小说）" if mode == "fiction" else "")
        chunks.append("%s%s  %d 字符  block %d  warn %d  hint %d" % (
            result["path"], label, result["units"],
            counts["block"], counts["warn"], counts["hint"]))
        if not result["findings"]:
            chunks.append("  干净。没有命中。")
            continue
        current = None
        for finding in result["findings"]:
            if finding["severity"] != current:
                current = finding["severity"]
                chunks.append("")
                chunks.append("[%s]" % SEV_LABEL[current])
            location = "L%d" % finding["line"] if finding["line"] else "全局"
            shown = finding["match"] or finding["excerpt"]
            chunks.append("  %-6s %s  “%s”" % (location, finding["rule"], shown))
            chunks.append("         改法: %s" % finding["fix"])
    return "\n".join(chunks)


def _md_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(results):
    chunks = []
    for result in results:
        counts = result["counts"]
        chunks.append("## %s" % result["path"])
        chunks.append("")
        chunks.append("%d 字符 · block %d · warn %d · hint %d" % (
            result["units"], counts["block"], counts["warn"], counts["hint"]))
        chunks.append("")
        if not result["findings"]:
            chunks.append("干净。没有命中。")
            chunks.append("")
            continue
        chunks.append("| 行 | 级别 | 规则 | 片段 | 改法 |")
        chunks.append("|---|---|---|---|---|")
        for finding in result["findings"]:
            chunks.append("| %s | %s | %s | %s | %s |" % (
                finding["line"] or "全局",
                finding["severity"],
                finding["rule"],
                _md_cell(finding["match"] or finding["excerpt"]),
                _md_cell(finding["fix"]),
            ))
        chunks.append("")
    return "\n".join(chunks)


def render_json(results, fail_on):
    totals = {"block": 0, "warn": 0, "hint": 0}
    clean = []
    for result in results:
        for severity, count in result["counts"].items():
            totals[severity] += count
        clean.append({
            "path": result["path"],
            "mode": result.get("mode", "prose"),
            "units": result["units"],
            "langs": result["langs"],
            "counts": result["counts"],
            "findings": [
                {key: value for key, value in finding.items() if key != "span"}
                for finding in result["findings"]
            ],
        })
    ok = not any(
        SEV_RANK[finding["severity"]] >= SEV_RANK[fail_on]
        for result in results for finding in result["findings"]
    ) if fail_on != "never" else True
    return json.dumps({
        "version": 1,
        "fail_on": fail_on,
        "ok": ok,
        "totals": totals,
        "files": clean,
    }, ensure_ascii=False, indent=2)


def list_rules(fiction=False):
    lines = ["id\tseverity\tlangs\tmin\tmax/1k\tcategory\tpattern"]
    for rule in RULES + (FICTION_RULES if fiction else []):
        lines.append("%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
            rule["id"], rule["severity"], ",".join(rule["langs"]),
            rule["min_count"],
            "" if rule["max_per_1000"] is None else rule["max_per_1000"],
            rule["category"], rule["pattern"]))
    return "\n".join(lines)


# --------------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Scan prose and code comments for AI-writing tells.")
    parser.add_argument("paths", nargs="*", help="files or directories")
    parser.add_argument("--changed", action="store_true",
                        help="scan text files changed in git")
    parser.add_argument("--code", action="store_true",
                        help="for source files, scan comments, docstrings, "
                             "and string literals only")
    parser.add_argument("--fiction", action="store_true",
                        help="add fiction-specific rules (novels, stories)")
    parser.add_argument("--context",
                        help="file with user prompt / prior text for negation checks")
    parser.add_argument("--root", default=".",
                        help="repository root for --changed (default: .)")
    parser.add_argument("--format", choices=["text", "markdown", "json"],
                        default="text")
    parser.add_argument("--fail-on", choices=["block", "warn", "hint", "never"],
                        default="block")
    parser.add_argument("--lang", choices=["auto", "zh", "en", "ja"], default="auto")
    parser.add_argument("--list-rules", action="store_true",
                        help="print the rule table and exit")
    parser.add_argument("--max", type=int, default=20,
                        help="max hits per rule per file (default: 20)")
    args = parser.parse_args(argv)

    if args.list_rules:
        print(list_rules(args.fiction))
        return 0

    context = ""
    if args.context:
        try:
            context = Path(args.context).read_text(encoding="utf-8")
        except OSError as exc:
            print("context: %s" % exc, file=sys.stderr)
            return 2
    if args.changed and args.paths:
        parser.error("--changed cannot be combined with explicit paths")
    if args.code and args.fiction:
        parser.error("--code cannot be combined with --fiction")

    results = []
    errors = []
    if args.changed:
        try:
            paths = git_changed(Path(args.root), args.code)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if not paths:
            print("no changed text files", file=sys.stderr)
            return 0
    elif args.paths:
        paths = []
        for raw in args.paths:
            candidate = Path(raw)
            if not candidate.exists():
                errors.append("no such path: %s" % raw)
                continue
            paths.extend(iter_text_files(candidate, args.code))
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
        results.append(scan_text(text, "<stdin>", args.lang, args.max,
                                 args.code, args.fiction, context))
        paths = []
    else:
        parser.error("give a path, pipe text on stdin, or use --changed")

    for path in paths:
        try:
            text = read_text(path)
        except OSError as exc:
            errors.append("%s: %s" % (path, exc))
            continue
        if text is None:
            errors.append("%s: binary file, skipped" % path)
            continue
        results.append(scan_text(text, str(path), args.lang, args.max,
                                 args.code, args.fiction, context))

    for message in errors:
        print(message, file=sys.stderr)

    if not results:
        return 2

    if args.format == "json":
        print(render_json(results, args.fail_on))
    elif args.format == "markdown":
        print(render_markdown(results))
    else:
        print(render_text(results))

    if args.fail_on == "never":
        return 0
    threshold = SEV_RANK[args.fail_on]
    hit = any(SEV_RANK[finding["severity"]] >= threshold
              for result in results for finding in result["findings"])
    return 1 if hit else 0


if __name__ == "__main__":
    sys.exit(main())
