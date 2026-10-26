#!/usr/bin/env python3
"""網站上線前檢查。用法：python3 scripts/check.py

錯誤（ERROR）要先修好才能 commit；警告（WARN）是已知問題或需要人判斷的事。
只用 Python 標準函式庫；有安裝 node 時，會順便檢查 JS 語法。
"""
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 其他網站（同一個 cwkuo99.github.io 來源：歷史站、課程站）已使用的前綴，本站不可使用
RESERVED_PREFIXES = ("hrv-", "hre-", "pc-")
# 已知的舊問題：只發警告，不擋 commit
LEGACY_KEYS = {"periodic_game_scores", "sciUltraS"}

errors, warns = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warns.append(msg)


def html_files():
    return sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)


def rel(p):
    return p.relative_to(ROOT).as_posix()


# 1. 首頁連結與檔案是否一致
index = (ROOT / "index.html").read_text(encoding="utf-8")
links = set(re.findall(r'href="([^"#:]+\.html)"', index))
for link in sorted(links):
    if not (ROOT / link).exists():
        err(f"index.html 連到不存在的檔案：{link}")
for p in html_files():
    r = rel(p)
    if r != "index.html" and r not in links:
        warn(f"{r} 沒有出現在 index.html（孤兒頁面：要加卡片，還是刪除？）")

# 2. localStorage 鍵與前綴
key_pat = re.compile(r"""localStorage\.(?:getItem|setItem|removeItem)\(\s*['"`]([^'"`$]+)""")
key_owner = defaultdict(set)
for p in html_files():
    for key in set(key_pat.findall(p.read_text(encoding="utf-8"))):
        key_owner[key].add(rel(p))
for key, files in sorted(key_owner.items()):
    if key.startswith(RESERVED_PREFIXES):
        err(f"localStorage 鍵 {key!r} 使用了歷史站的前綴（{', '.join(sorted(files))}）")
    if len(files) > 1:
        msg = f"localStorage 鍵 {key!r} 被多個頁面共用：{', '.join(sorted(files))}"
        (warn if key in LEGACY_KEYS else err)(msg)
    if not re.search(r"[-_]", key):
        msg = f"localStorage 鍵 {key!r} 沒有前綴（{', '.join(sorted(files))}）"
        (warn if key in LEGACY_KEYS else err)(msg)

# 3. 教師版不可上線
for p in html_files():
    text = p.read_text(encoding="utf-8")
    title = re.search(r"<title>([^<]*)", text)
    if title and "教師" in title.group(1):
        err(f"{rel(p)} 的標題含「教師」，教師版不能放上公開網站")

# 4. 手機基本要求與重複 id
for p in html_files():
    text = p.read_text(encoding="utf-8")
    if 'name="viewport"' not in text:
        err(f"{rel(p)} 缺少 viewport meta，手機會縮成桌面版")
    ids = re.findall(r'\sid="([^"{}$]+)"', text)
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        warn(f"{rel(p)} 有重複的 id：{', '.join(dups[:5])}")

# 5. JS 語法（需要 node；略過 type="text/babel" 的 JSX）
node = shutil.which("node")
script_pat = re.compile(r"<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", re.S)
if node:
    for p in html_files():
        for i, (attrs, body) in enumerate(script_pat.findall(p.read_text(encoding="utf-8"))):
            if "babel" in attrs or "json" in attrs or not body.strip():
                continue
            ext = ".mjs" if 'type="module"' in attrs else ".js"
            with tempfile.NamedTemporaryFile("w", suffix=ext, delete=False, encoding="utf-8") as f:
                f.write(body)
            res = subprocess.run([node, "--check", f.name], capture_output=True, text=True)
            Path(f.name).unlink()
            if res.returncode:
                first = next((l for l in res.stderr.splitlines() if "Error" in l), res.stderr.strip()[:200])
                err(f"{rel(p)} 第 {i + 1} 個 <script> 語法錯誤：{first}")
else:
    warn("找不到 node，略過 JS 語法檢查")

for m in warns:
    print("WARN ", m)
for m in errors:
    print("ERROR", m)
print(f"\n{len(errors)} 個錯誤，{len(warns)} 個警告")
sys.exit(1 if errors else 0)
