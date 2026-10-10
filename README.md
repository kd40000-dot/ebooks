# Ebooks — Smart Book Vietnamese learning project

We convert English stories into **Vietnamese primary / English translation** editions for KursX Smart Book, joining learner-useful Vietnamese vocabulary and contextual expressions using hyphens.

## Current test book

`books/unicorn/vietnamese_hyphenated.txt` — 16 Vietnamese paragraphs with 155 hyphen connections.  
`books/unicorn/english.txt` — the 16 aligned English paragraphs.

To create the book on Android (Fairphone 6 / LineageOS), open Smart Book → Create parallel book, import the Vietnamese first and English as its translation, select **Empty line** for the paragraph separator, then export from the app. That is presently the reliable route to an app-generated `.sb2`.

## Reverse engineering and experimental packages

Previously supplied app-generated `.sb2` samples have a ZIP container, one metadata `.sb` file and separate chapter `.sb` entries using Deflate and classic ZipCrypto. Their password and current native payload serialization remain unknown.

The sample `.sb2` packages produced in this experiment are **not confirmed importable**. They use an older Parallator-style JSON model and either no ZIP encryption or a test-only password. Passing ZIP validation does not mean passing Smart Book's import validation.

The helper script `scripts/prototype_sb2.py` generates an unencrypted **experimental** archive from the paired text files. `scripts/stage_android.sh` can stage the text files using ADB.

## References

- [Official Smart Book](https://smart-book.net/)
- [KursX Parallator](https://github.com/KursX/Parallator)
- App ID on Android: `com.kursx.smartbook`

## Next experiments

1. Try importing the unencrypted prototype and record the exact result.
2. Use ADB / Android UI Automator to drive the native editor and exporter on the Fairphone.
3. Compare the resulting genuine `.sb2` against our candidate.

**Do not treat a ZIP-shaped candidate as a proven native Smart Book export.**
