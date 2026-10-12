# Working bilingual Smart Book method — checkpoint v1

**Status:** User-confirmed working end-to-end for the three-chapter *I Found a Unicorn* edition on **Fairphone 6 / LineageOS**. This file documents the **method to reuse for future stories**, not just the result of one test. Preserve this checkpoint when experimenting.

## Checkpoint identity and recovery

- **Source checkpoint branch:** [`checkpoint/smartbook-bilingual-v1-working`](https://github.com/kd40000-dot/ebooks/tree/checkpoint/smartbook-bilingual-v1-working), pinned to commit `7a41b6cb6e3c6e9e4b02db379c99f89526b44395`, the code revision that produced the successful three-chapter export.
- **Native export:** [GitHub Actions run 38099039411, attempt 2](https://github.com/kd40000-dot/ebooks/actions/runs/38099039411); successful export bytes `artifacts/I Found a Unicorn_native.sb2` within its latest `smartbook-android-evidence` artifact.
- **Golden file:** `checkpoints/smartbook-bilingual-v1/I Found a Unicorn - Three Chapters.sb2` (persisted by `.github/workflows/archive-unicorn-checkpoint.yml`).
- **SHA-256:** `c416acc906a77b40f3e8faeffdd93dc6d3f18f4b5f17e02bd04e37d854b70646`. File size 9,731 bytes.
- **Structure:** one encrypted metadata `.sb` plus **three encrypted chapter `.sb` files**, all in the app-generated encrypted ZIP format. Python's `zipfile.testzip()` cannot validate encrypted payloads without the app's password; do **not** claim decrypted-content verification.
- **Baseline input:** `books/unicorn/vietnamese_hyphenated.txt`, `books/unicorn/english.txt`, and the six UTF-8 files in `books/unicorn/chapters/{vi,en}`.

To restore the tested code after a regression: inspect the checkpoint branch versus main; recover the specific `scripts/automate_android.py`, `scripts/build_share_sink.sh`, `scripts/ci_smartbook.sh` and `.github/workflows/smartbook-emulator.yml` versions from that branch. **Do not force-reset main or overwrite later work without a deliberate comparison.** Compare the output against the golden SHA and book structure.

## Full process for a NEW story

### 1. Receive and understand the text

- Obtain the full source story in English or another source language, along with any attribution, chapter markers, formatting requirements and permission/context needed to use the text.
- Read the entire text. Identify characters, setting, idioms, timeline, tone, unusual vocabulary, chapter turning points and paragraphs/dialogue.
- If the supplied story is already Vietnamese, preserve it as the primary text and obtain or translate an English rendering for the attached translation. Otherwise create Vietnamese from the source and preserve the original English as a separate reference for factual and stylistic accuracy; the English displayed in the Smart Book is revised **after** Vietnamese is finalized, for learners.
- Never invent author credit. The benchmark uses **Anonymous** only because the source story did not supply a verified author.

### 2. Translate into learner-friendly, natural Vietnamese

- Produce complete Vietnamese text, not a synopsis. Preserve the narrative, actions, implications, character voices, register, emphases, profanity if relevant, names and story order.
- Translate idioms **by context**, not a word-for-word English gloss. Keep Vietnamese idiomatic and consistent across the whole story.
- Check proper names and pronouns; do not unintentionally change who says or does something. Keep original English as a permanent reference, then create a **learner-aligned English edition** that clarifies Vietnamese expression choices.
- Perform a deliberate accuracy read-through. Do not lose sentences, merge unrelated plot points, or add content not found in the source.

### 3. Apply contextual Vietnamese hyphenation

The goal is to make *multi-syllable Vietnamese words and useful contextual compounds* visibly readable as lexical units to a language learner. Hyphens are learning cues, **not** general punctuation to scatter throughout a sentence.

- Join syllables that form a single natural lexical item, e.g. `kỳ-lân`, `cảnh-sát-viên`, `truyện-cổ-tích`, `chuẩn-bị`, `tìm-thấy` in the benchmark's editorial style.
- Where beneficial, join short cohesive multiword expressions when context demands, rather than mechanically hyphenating every adjacent Vietnamese token.
- Use the vocabulary's **meaning in this sentence**: homographs and flexible word boundaries require human/model judgement.
- Avoid hyphenating unrelated words, attaching punctuation to the wrong token, damaging proper names or changing word order. Preserve accents and capitalization.
- Check compound consistency through each chapter, then scan for unnatural or overzealous joins. The 16-paragraph Unicorn benchmark has **155 hyphen connections**; that number is a property of the example, **not a quota** for new stories.

### 4. Rewrite English for Vietnamese learners AFTER Vietnamese is finalized

**The final natural Vietnamese text is the anchor. Do not modify it for the sake of English alignment.** Keep the original English story as an untouched reference to protect meaning and voice. Edit only the *displayed English translation* to help beginners understand which English ideas map to which Vietnamese expressions.

- The objective is a **sweet spot between literal and idiomatic**: show the relationship to Vietnamese vocabulary and phrasing while sounding like natural, straightforward English. For example: `Chào mọi người trên Reddit.` → `Hello, everyone on Reddit.` rather than merely `Hello, Reddit.`
- Prefer familiar English wording and clear subjects/objects. Where the original English uses shorthand, idioms, elliptical dialogue, or unnecessary sophistication, use simple explicit meaning when it matches Vietnamese. Keep concrete references and chronology intact.
- Preserve every event, implication, uncertainty, voice, name and register from **both** the finalized Vietnamese and the original source. Never add invented facts to explain a word. Do not over-literalize to the point of awkward or misleading English.
- Preserve purposeful colloquial/profane speech where the source and Vietnamese require it. Do not euphemize away intensity just because the reader is learning.
- **Align sentences and clauses** so that Smart Book's `End of sentence` splitting produces corresponding units. Aim to keep the sentence count within each source paragraph equal across languages; verify punctuation, direct speech and abbreviation edge cases. Match meaning, not merely punctuation.
- Do a two-direction review: Vietnamese → English checks learner word mapping; original English → revised English checks the original story's meaning. If conflict arises, flag it and seek clarification rather than silently rewriting the Vietnamese.
- Save the original English separately as `english_original_reference.txt`. Save the learner-aligned English as `english.txt` and use **only the learner edition** for native Smart Book's Translation → Upload a file.
- Only after English revision is finished, split both sides into corresponding numbered chapters and verify the passage counts.

### 4. Align English and Vietnamese before splitting

- Retain a stable sequence of narrative passages; paragraph/chunk `i` in Vietnamese must correspond to chunk `i` in English. Do **not** pair by an accidental independent sentence-splitting pass.
- Verify the number and order of aligned source units. In our test: **16 Vietnamese and 16 English passages**; the book is later split into **5 + 5 + 6** passages across chapters.
- Keep text as UTF-8 with consistent blank lines and Unicode accents. Ensure translated and source chapters each cover the **same** span of story.
- The app's requested **Paragraph separator = End of sentence**. This is the user's preferred successful setting, but Vietnamese and English sentence boundaries can differ; test that translation taps show sensible matching text on the actual reader.

### 5. Give the book clean metadata and numbered chapters

- Title case a concise natural book name; never leave underscores in **displayed** title, author or chapter names. Preserve a supplied author's actual name if known.
- Choose scene- or plot-based chapter boundaries that make navigation enjoyable, without skipping text or cutting a meaningful speech in the wrong place.
- Number consecutively, e.g. `Chương 1 - Những cái chết bí ẩn`, `Chương 2 - Dấu máu lấp lánh`, `Chương 3 - Đối mặt với kỳ lân`.
- Place aligned chapter TXT files in a book-specific directory analogous to `books/unicorn/chapters/vi/` and `.../en/`. Keep language-specific files independently readable and fully paired.
- Filenames may contain accents and spaces. Android Smart Book itself can normalize internal archive filenames to underscores; this is **not** the user-visible title.

### 5a. Generate and attach a spoiler-free native cover

- After reading the complete story and choosing chapter themes, **automatically generate a polished, spoiler-free book cover**. Keep the displayed title and author legible when reduced to a small Smart Book library thumbnail.
- Match the story's mood and genre without revealing its ending or important twists. Save an appropriately compressed JPEG (benchmark: `books/unicorn/art/cover.jpg`).
- The native creation screen has a `com.kursx.smartbook:id/thumbnail_layout` image picker. Stage the JPEG on Android and **select it before saving**. The current illustrated workflow uses `scripts/automate_android.py` to do this through the real Android image chooser.
- In native export, check that an **encrypted JPG entry** accompanies the encrypted metadata and chapter entries. The `.sb2` should be generated unchanged by Smart Book; do not inject images by editing its ZIP container.
- **Do not insert chapter-head images into `.sb2` by default:** the current native chapter creation workflow imports TXT and has not proven that chapter images survive while bilingual sentence translation continues to work. Experiment only in a separate branch and preserve the known-working checkpoint.

### 6. Configure the tested native Android automation

Currently this is a **known-good book-specific emulator pipeline**, not a fully configurable ebook SaaS. For each new book:

- Adapt `CHAPTERS`, `CHAPTERS_ROOT`, displayed title and author in `scripts/automate_android.py`, and the source paths. Do not overwrite the Unicorn baseline or the recovery branch.
- Run the GitHub Actions workflow `.github/workflows/smartbook-emulator.yml` on the updated branch/commit. It boots an Android emulator, downloads the publisher's signed Smart Book APK from `https://smart-book.net/apk`, and installs `com.kursx.smartbook`.
- The Python UI driver stages UTF-8 files using ADB, selects Vietnamese as the **book language**, sets or verifies **End of sentence**, and builds chapters through **My Books → Add Book → Create a parallel book**.
- For each chapter: **Upload a file** to import its Vietnamese content; tap that chapter's **three-dot menu → Translation → Upload a file**; choose its matching English TXT. Confirm the app's `/target` translation control exists before proceeding.
- **Only after all chapters have Vietnamese and English**: tap **Save**. Follow the first-run reader tutorial if shown.
- Navigate back to the saved-book **chapter-list screen** (not the reader's settings); use the **top-right Share icon** (`com.kursx.smartbook:id/action_share`) to export. This launches Android's Sharesheet with Smart Book's own encrypted `.sb2`.
- The CI-only share receiver built by `scripts/build_share_sink.sh` is called **Save SB2 locally**. It receives Smart Book's ACTION_SEND stream and saves its bytes **unchanged**. The automation pulls that file into `artifacts/`.
- UI automation can occasionally fail on Android Quickstep/System UI ANRs or DocumentsUI files being off-screen. Inspect debug screenshots and XML from the workflow artifact and retry only once the failed step is understood. Do not change the story content to work around emulator flakiness.

### 7. Validate the deliverable and return the actual file

- Verify the successful job log contains `PARAGRAPH_SEPARATOR_VERIFIED: End of sentence`, `BOOK_METADATA`, `BILINGUAL_CHAPTER_READY` for **every** chapter, `ALL_NUMBERED_CHAPTERS_READY`, and `GENUINE_APP_GENERATED_SB2`.
- Verify the **actual exported** `.sb2` ZIP: one encrypted metadata `.sb`, as many encrypted chapter `.sb` files as intended, Deflate as appropriate, no unexpected paths; compute SHA-256.
- Use `python scripts/verify_native_sb2.py PATH --chapters N` (read-only validation). This **cannot** prove the encrypted translation contents align; logs plus an actual import test cover that gap.
- Download the bytes from the successful GitHub Actions artifact and attach the exact file to the user; never silently substitute a hand-built ZIP, a stale single-chapter file, or source TXT.
- On the user's Android Smart Book, import and open it. Check **chapter navigation**, correct user-facing titles, Vietnamese diacritics and semantic hyphens, and **Translate** showing aligned English. Document user confirmation and retain a known-good package.

### 8. Archive a checkpoint

- Keep original and hyphenated text, English equivalents, chapter manifest, the tested script, outcome log/run ID, SHA-256, and a successfully exported `.sb2` somewhere durable. An Action artifact is not durable (seven-day retention in the current workflow).
- A new book should get its own versioned checkpoint, not overwrite this one. Distinguish **source prepared**, **native exported**, and **user import-confirmed**.
- If future work breaks, consult this file, the frozen source branch and the golden binary, then compare the changed workflow to this known-good method.

## Known limits

- Translation, contextual hyphenation and elegant chapter naming currently require language-model/editorial work in the conversation; they are not yet automated as a repository Python-only step.
- Native `.sb2` serialization and encryption are not publicly reproduced here. The genuine KursX app supplies them. **Do not use `scripts/prototype_sb2.py` for a deliverable.**
- Source-language-to-Vietnamese work for future books should preserve copyright and attribution as applicable.
- This method has been tested for one title and three chapters; adapt and validate other books rather than assuming the reader/UI and translation alignment are always identical.
