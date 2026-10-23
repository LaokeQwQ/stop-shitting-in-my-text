#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install the anti-slop rules into the project's constraint document.

Priority: nearest AGENTS.md, CLAUDE.md, .cursorrules / .cursor/rules/*.mdc,
.github/copilot-instructions.md, CONTRIBUTING.md,
docs/style-guide.md, STYLE.md, WRITING.md.

The block is wrapped in markers and replaced in place, so repeated runs are
safe. When no constraint document exists, AGENTS.md is created only in a
project directory (git repo or common project markers), never in $HOME by
accident.

Exit codes: 0 installed/current, 1 check failed or nothing installed, 2 error.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BEGIN = "<!-- stop-shitting-in-my-text:begin v2 -->"
END = "<!-- stop-shitting-in-my-text:end -->"
BLOCK = BEGIN + """
## 文案约束：别在我的文案里拉屎

目标：写具体、可核对、有人承担的文字。

1. 先给事实：谁做了什么、多少、什么时候、结果如何；再给解释。
2. 一段只推进一步；句子有主语；长短句交替。
3. 删掉不承担信息的铺垫、总结、安抚和流程表演。
4. 中文用中文语序，英文和日文用各自语序；代码注释写行为、约束、原因和坑。
5. 约束写正向状态和边界；能删掉的错误内容直接删。
6. 只改风格；事实、数字、专名、引用保持原样。
7. 缺失事实列在正文外；成品里不留编辑备注。
8. README、技术文档、代码注释默认干练，只给信息；用户明确要求友好语气时按用户。
9. 只回应用户输入里存在的内容；不造反对意见、不自问自答；开头直接给结果。否定句先查 A：前文或用户输入没出现，就删掉否定直接写 B；不把思维链里的备选写进正文。
10. 交付前跑 `scan.py`（小说用 `--fiction`）；`block` 清零，`warn` 逐条判断。

具体模式由 `scripts/lexicon.py` 维护。扫描命令：
`python3 ~/.agents/skills/stop-shitting-in-my-text/scripts/scan.py <files>`
""" + END

BLOCK_RE = re.compile(
    r"<!--\s*stop-shitting-in-my-text:begin\b.*?-->.*?"
    r"<!--\s*stop-shitting-in-my-text:end\s*-->",
    re.S,
)

CANDIDATES = [
    "AGENTS.md",
    "CLAUDE.md",
    ".cursorrules",
    ".github/copilot-instructions.md",
    "CONTRIBUTING.md",
    "docs/CONTRIBUTING.md",
    "docs/style-guide.md",
    "STYLE.md",
    "WRITING.md",
]

PROJECT_MARKERS = [
    ".git", "package.json", "pyproject.toml", "setup.py", "setup.cfg",
    "go.mod", "Cargo.toml", "Makefile", "Gemfile", "pom.xml",
    "build.gradle", "composer.json", ".omp", ".agents",
]


def git_root(start):
    try:
        proc = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode == 0:
        return Path(proc.stdout.strip()).resolve()
    return None


def projectish(directory):
    if any((directory / marker).exists() for marker in PROJECT_MARKERS):
        return True
    if any(directory.glob("*.sln")) or any(directory.glob("*.csproj")):
        return True
    return False


def find_existing(start):
    current = start.resolve()
    root = git_root(current)
    while True:
        for relative in CANDIDATES:
            candidate = current / relative
            if candidate.is_file():
                return candidate
        rules_dir = current / ".cursor" / "rules"
        if rules_dir.is_dir():
            mdc = sorted(rules_dir.glob("*.mdc"))
            if mdc:
                return mdc[0]
        if root is None or current == root or current.parent == current:
            break
        current = current.parent
    return None


def apply_block(existing, filename):
    match = BLOCK_RE.search(existing)
    if match:
        if match.group(0).strip() == BLOCK.strip():
            return existing, "unchanged"
        before = existing[:match.start()].rstrip("\n")
        after = existing[match.end():].lstrip("\n")
        parts = [part for part in (before, BLOCK, after) if part]
        return "\n\n".join(parts) + "\n", "replaced"

    if not existing.strip():
        if filename == "AGENTS.md":
            return "# AGENTS\n\n" + BLOCK + "\n", "installed"
        return BLOCK + "\n", "installed"

    return existing.rstrip("\n") + "\n\n" + BLOCK + "\n", "installed"


def write_atomic(path, content, existed):
    mode = path.stat().st_mode if existed else None
    fd, temporary = tempfile.mkstemp(
        dir=str(path.parent), prefix=".ssimt-", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Install anti-slop rules into AGENTS.md or another "
                    "constraint document.")
    parser.add_argument("--root", default=".",
                        help="start searching here (default: .)")
    parser.add_argument("--target",
                        help="write to this file instead of searching")
    parser.add_argument("--check", action="store_true",
                        help="report status without writing")
    parser.add_argument("--print", dest="print_block", action="store_true",
                        help="print the rules block and exit")
    parser.add_argument("--create", action="store_true",
                        help="create AGENTS.md even outside a project")
    parser.add_argument("--no-create", action="store_true",
                        help="never create a constraint document")
    args = parser.parse_args(argv)

    if args.print_block:
        print(BLOCK)
        return 0

    start = Path(args.root).expanduser().resolve()
    if not start.is_dir():
        print("not a directory: %s" % start, file=sys.stderr)
        return 2

    target = None
    if args.target:
        target = Path(args.target).expanduser().resolve()
        if not target.parent.is_dir():
            print("parent directory does not exist: %s" % target.parent,
                  file=sys.stderr)
            return 2
    else:
        target = find_existing(start)

    if target is None and not args.no_create:
        base = git_root(start) or start
        if args.create or projectish(base):
            target = base / "AGENTS.md"

    if target is None:
        if args.check:
            print("target: none")
            print("status: none")
            return 1
        print(BLOCK)
        print("", file=sys.stderr)
        print("no constraint document found; printed the block instead. "
              "Use --create to write AGENTS.md here.", file=sys.stderr)
        return 1

    if args.check:
        print("target: %s" % target)
        if not target.is_file():
            print("status: missing")
            return 1
        existing = target.read_text(encoding="utf-8-sig", errors="replace")
        match = BLOCK_RE.search(existing)
        if match and match.group(0).strip() == BLOCK.strip():
            print("status: current")
            return 0
        print("status: stale" if match else "status: missing")
        return 1

    existed = target.is_file()
    existing = target.read_text(encoding="utf-8-sig") if existed else ""
    updated, action = apply_block(existing, target.name)
    if action != "unchanged":
        write_atomic(target, updated, existed)
    print("target: %s" % target)
    print("action: %s" % action)
    return 0


if __name__ == "__main__":
    sys.exit(main())
