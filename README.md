# Bilingual Smart Books — working production checkpoint

This repository contains a **proven native KursX Smart Book (.sb2) workflow** for converting a story into a Vietnamese-primary, English-translation ebook, using context-sensitive Vietnamese hyphenation. The three-chapter *I Found a Unicorn* edition has been exported by the actual Android Smart Book app and the user confirmed that edition works on their Fairphone 6 / LineageOS.

**START HERE:** [Full reusable method](docs/SMARTBOOK_WORKING_METHOD.md) · [Checkpoint source branch](https://github.com/kd40000-dot/ebooks/tree/checkpoint/smartbook-bilingual-v1-working) · [Successful export run](https://github.com/kd40000-dot/ebooks/actions/runs/38099039411)

## Proven finished example

- Title: **I Found a Unicorn**; author: **Anonymous**
- Vietnamese primary text with meaningful phrase hyphenation; English as attached translation
- Book separator setting: **End of sentence**
- Three numbered chapters with readable Vietnamese titles and **no underscores** in displayed names
- Original source: `books/unicorn/vietnamese_hyphenated.txt` and `books/unicorn/english.txt` — 16 aligned source passages, unchanged through the three-chapter split
- Chapter files: `books/unicorn/chapters/vi/` and `books/unicorn/chapters/en/`
- GitHub Actions workflow: [.github/workflows/smartbook-emulator.yml](.github/workflows/smartbook-emulator.yml)
- Native app automation: [scripts/automate_android.py](scripts/automate_android.py)
- Binary checkpoint: `checkpoints/smartbook-bilingual-v1/I Found a Unicorn - Three Chapters.sb2` (archived by a separate one-time workflow; see checkpoint method document for verification)

**Known-good file SHA-256:** `c416acc906a77b40f3e8faeffdd93dc6d3f18f4b5f17e02bd04e37d854b70646` (9,731 bytes). The ZIP container has **one encrypted book metadata `.sb` entry and three encrypted chapter `.sb` entries**.

## What is automated and what is not

1. **Content preparation:** Translation from the source language into Vietnamese, phrase-level hyphenation, editorial chapter selection, and alignment/QA are performed with language-model assistance and reviewed for fidelity. They are **not currently provided as a standalone automatic Python translator**.
2. **Native ebook production:** The repository's GitHub Actions emulator job installs the official Smart Book APK, imports each Vietnamese chapter and its English translation, and uses Smart Book's **top-right share icon on the saved-book chapter list** to export the real encrypted `.sb2`.
3. **Validation:** Check source alignment, import logs, the `.sb2` ZIP entries/encryption, and finally import/read the book on an actual Fairphone or another Smart Book installation.

The current script is configured for the Unicorn example. **Adapt its chapter manifest, title and author fields for each new book**, rather than reusing the Unicorn content.

## Important safety notes

The older `scripts/prototype_sb2.py` is an **unsuccessful experimental generator**, retained for format research only. **Never use it to create a deliverable.** Hand-built ZIPs failed to import; the official Android app must make the package.

GitHub Actions artifacts are temporary. Keep the verified baseline `.sb2` and this Git checkpoint. UI hierarchy captures may contain excerpts of the book; review before distributing diagnostics.

### References

- [KursX Smart Book](https://smart-book.net/)
- [KursX Parallator](https://github.com/KursX/Parallator)
- Android application ID: `com.kursx.smartbook`
