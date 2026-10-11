# Native three-chapter Smart Book export — success

GitHub Actions [run 38099039411, attempt 2](https://github.com/kd40000-dot/ebooks/actions/runs/38099039411) generated a genuine encrypted KursX Smart Book SB2.

**Book:** I Found a Unicorn · **Author:** Anonymous · **Primary:** Vietnamese (semantic hyphenation) · **Translation:** English · **Paragraph separator:** End of sentence.

## Chapters

1. Chương 1 - Những cái chết bí ẩn (original source paragraphs 1–5)
2. Chương 2 - Dấu máu lấp lánh (paragraphs 6–10)
3. Chương 3 - Đối mặt với kỳ lân (paragraphs 11–16)

All 16 original Vietnamese and English paragraphs were compared against the chapter splits and preserved exactly.

## Verified artifact

- Artifact: `smartbook-android-evidence` (latest attempt)
- File inside: `artifacts/I Found a Unicorn_native.sb2`
- Size: **9,731 bytes**
- SHA-256: `c416acc906a77b40f3e8faeffdd93dc6d3f18f4b5f17e02bd04e37d854b70646`
- ZIP entries: 3 encrypted chapter `.sb` files, 1 encrypted metadata `.sb` file, plus directory entry.
- Logs: `PARAGRAPH_SEPARATOR_VERIFIED: End of sentence`, `BOOK_METADATA: I Found a Unicorn / Anonymous`, three `BILINGUAL_CHAPTER_READY` confirmations, `ALL_NUMBERED_CHAPTERS_READY 3` and `GENUINE_APP_GENERATED_SB2`.

The Smart Book application normalizes filenames *inside* its encrypted archive, so the internal chapter filenames contain underscores. The user-visible book title and chapter names use spaces.

**Next validation:** import this new multi-chapter edition on Fairphone 6 / LineageOS, inspect chapter navigation and English alignment. The earlier sentence-separated single-chapter edition is known to work on that device; the new file has not yet had a separate-device import check.
