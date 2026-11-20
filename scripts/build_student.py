#!/usr/bin/env python3
"""從教師版產生學生版。用法：python3 scripts/build_student.py <教師版.html> <輸出的學生版.html>

教師版放在 repo 外，不要 commit。教師版裡用下列標記：

- 只給老師看的內容（教師模式、教學提示、答案、講解）包起來，學生版會整段刪掉：
    HTML： <!-- teacher:start --> … <!-- teacher:end -->
    JS/CSS：/* teacher:start */ … /* teacher:end */
- 只在學生版出現的替代內容（教師版裡是註解）：
    HTML： <!--student: … :student-->
    JS/CSS：/*student: … :student*/

產生後會檢查：不能殘留任何標記、teacher-mode 開關或 teacher-note 區塊；有殘留就報錯、不寫檔。
只用 Python 標準函式庫。
"""
import re
import sys
from pathlib import Path

DROP = [
    re.compile(r"<!--\s*teacher:start\s*-->.*?<!--\s*teacher:end\s*-->", re.S),
    re.compile(r"/\*\s*teacher:start\s*\*/.*?/\*\s*teacher:end\s*\*/", re.S),
]
KEEP = [
    re.compile(r"<!--student:(.*?):student-->", re.S),
    re.compile(r"/\*student:(.*?):student\*/", re.S),
]
LEFTOVER = re.compile(r"teacher:start|teacher:end|student:|:student|id=\"teacher-mode\"|class=\"teacher-note\"|st\.teacher")


def build(src: str) -> str:
    out = src
    for p in DROP:
        # 整行只有教師區塊時，連同那一行一起刪掉，不留空行
        out = re.sub(r"(?m)^[ \t]*(?:" + p.pattern + r")[ \t]*\n", "", out, flags=re.S)
        out = p.sub("", out)
    for p in KEEP:
        out = p.sub(lambda m: m.group(1), out)
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    text = src.read_text(encoding="utf-8")
    if not LEFTOVER.search(text):
        print(f"WARN  {src.name} 沒有任何教師標記：如果它有教師內容，要先標記", file=sys.stderr)
    out = build(text)
    bad = sorted({m.group(0) for m in LEFTOVER.finditer(out)})
    if bad:
        sys.exit(f"ERROR 學生版還有教師內容或標記：{', '.join(bad)}（沒有寫檔）")
    dst.write_text(out, encoding="utf-8")
    print(f"OK    {src.name} → {dst}（{len(text)} → {len(out)} 字元）")


if __name__ == "__main__":
    main()
