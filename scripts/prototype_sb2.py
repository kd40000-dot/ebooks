#!/usr/bin/env python3
"""Build a ZIP-shaped experimental SB2. NOT a verified Smart Book exporter.

Native Smart Book exports are ZIP/Deflate with encrypted metadata and chapter
entries. This standalone script deliberately makes an UNENCRYPTED prototype
using the older Parallator JSON model; import compatibility is unproven.
"""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "books" / "unicorn"
OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)

def paragraphs(name):
    text = (DATA / name).read_text(encoding="utf-8")
    return [p.strip() for p in text.split("\n\n") if p.strip()]

vi = paragraphs("vietnamese_hyphenated.txt")
en = paragraphs("english.txt")
if not vi or len(vi) != len(en):
    raise ValueError("The Vietnamese and English paragraph counts must match.")

book_id = "i_found_a_unicorn_vi_en"
metadata = {
    "direction": "vi-en",
    "name": "Tôi đã tìm-thấy một con kỳ-lân",
    "author": "Anonymous (Reddit)",
    "hash": hashlib.sha256(("\n".join(vi) + "\n".join(en)).encode()).hexdigest()[:20],
    "thumbnail": "",
    "filename": book_id + ".sb",
    "langs": [
        {"name": "Tôi đã tìm-thấy một con kỳ-lân", "lang": "vi",
         "author": "Anonymous (Reddit)"},
        {"name": "I Found a Unicorn", "lang": "en",
         "author": "Anonymous (Reddit)"},
    ],
}
chapter = {
    "chapterName": "1# I Found a Unicorn",
    "paragraphs": [{"vi": v, "en": e} for v, e in zip(vi, en)],
}

def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

name = OUT / "i_found_a_unicorn_unencrypted_EXPERIMENTAL.sb2"
with zipfile.ZipFile(name, "w") as z:
    z.writestr(book_id + "/1# i_found_a_unicorn.sb", dump(chapter),
               compress_type=zipfile.ZIP_DEFLATED)
    z.writestr(book_id + "/", b"", compress_type=zipfile.ZIP_STORED)
    z.writestr(book_id + ".sb", dump(metadata),
               compress_type=zipfile.ZIP_DEFLATED)

with zipfile.ZipFile(name) as z:
    assert z.testzip() is None
    assert json.loads(z.read(book_id + ".sb")) == metadata
    assert json.loads(z.read(book_id + "/1# i_found_a_unicorn.sb")) == chapter

print(f"Created {name}")
print(f"Vietnamese/English paragraphs: {len(vi)}/{len(en)}")
print(f"Vietnamese hyphens: {sum(p.count('-') for p in vi)}")
print("NOT confirmed to import in Smart Book.")
