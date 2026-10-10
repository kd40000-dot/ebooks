# Ebooks — Smart Book Vietnamese learning project

We convert English stories into **Vietnamese primary / English translation** editions for KursX Smart Book, joining learner-useful Vietnamese vocabulary and contextual expressions using hyphens.

## Current test book

`books/unicorn/vietnamese_hyphenated.txt` — 16 Vietnamese paragraphs with 155 hyphen connections.  
`books/unicorn/english.txt` — the 16 aligned English paragraphs.

To create the book on Android (Fairphone 6 / LineageOS), open Smart Book → Create parallel book, import the Vietnamese first and English as its translation, select **Empty line** for the paragraph separator, then export from the app. That is presently the reliable route to an app-generated `.sb2`.

## Reverse engineering and experimental packages

Previously supplied app-generated `.sb2` samples have a ZIP container, one metadata `.sb` file and separate chapter `.sb` entries using Deflate and classic ZipCrypto. Their password and current native payload serialization remain unknown.

The sample `.sb2` packages produced in this experiment are **confirmed to fail in Smart Book** (2026-10-10). They use an older Parallator-style JSON model and either no ZIP encryption or a test-only password. Passing ZIP validation does not mean passing Smart Book's import validation.

The helper script `scripts/prototype_sb2.py` generates an unencrypted **experimental** archive from the paired text files. `scripts/stage_android.sh` can stage the text files using ADB.

## References

- [Official Smart Book](https://smart-book.net/)
- [KursX Parallator](https://github.com/KursX/Parallator)
- App ID on Android: `com.kursx.smartbook`

## Current result and next experiments

- **Failed import confirmed:** Smart Book showed a Zip4j invalid-CRC error and a generic incomplete-download message when trying the experimental archives. We do not know which screenshot corresponds to which experimental candidate. See [the test report](docs/2026-10-10-import-failure.md).
- **Do not use the synthetic `.sb2` generator for real books.** It is retained solely as a reverse-engineering experiment.
- **Next:** use `scripts/capture_android_ui.sh` on your Fairphone 6 with ADB while Smart Book's book creation screen is open, then identify and automate the in-app Save / Export steps.
- Android captured screenshots and UI dumps are local and excluded from Git by `.gitignore`; review for private data before sharing.

**Do not treat a ZIP-shaped candidate as a proven native Smart Book export.**
