# I Found a Unicorn — learner-friendly English, native illustrated-cover SB2

The English in the attached translation was deliberately revised **after** the Vietnamese was finalized. The Vietnamese text and hyphenation are unchanged; the original English is retained as `books/unicorn/english_original_reference.txt`.

## Source changes

- 16 Vietnamese paragraphs retained exactly, unchanged in the three native chapter TXT files.
- 16 revised English paragraphs, split into 5 + 5 + 6; same chapter boundaries as the original.
- 44 sentence-ending punctuation marks across each language's 16 passages (simple heuristic; actual app alignment should still be checked on a device).
- Primary language: Vietnamese. Translation: learner-aligned English.
- Paragraph separator: **End of sentence**.
- Native generated cover: `books/unicorn/art/cover.jpg`.
- No unverified chapter-opening images added to SB2.

## Confirmed native export

- [Successful Smart Book Android export run 38210064617](https://github.com/kd40000-dot/ebooks/actions/runs/38210064617)
- GitHub Actions artifact: `smartbook-android-evidence`, ID `11729247929`
- Exported file within artifact: `artifacts/I Found a Unicorn_native.sb2`
- Size: **106,454 bytes**
- SHA-256: `97a9af5c76e1f87cc32bbf1511f9dd3d9a13a28f8217c50c284f035d7794252a`
- Native encryption/structure: exactly three encrypted chapter `.sb`, one encrypted metadata `.sb`, and one encrypted cover `.jpg` entry.
- Log confirmations: `NATIVE_COVER_IMAGE_SELECTED`, `PARAGRAPH_SEPARATOR_VERIFIED: End of sentence`, three `BILINGUAL_CHAPTER_READY`, `ALL_NUMBERED_CHAPTERS_READY 3`, `GENUINE_APP_GENERATED_SB2`.
- Durable archive path: `checkpoints/smartbook-bilingual-v2-learner-english/I Found a Unicorn - Learner-Friendly English - Illustrated Cover.sb2`.

**Status:** Genuine native export and archive structure verified. The revised-English edition still awaits import and sentence-alignment confirmation on the user's Fairphone 6; do not call that part user-verified yet. The earlier [v1 user-verified golden baseline](../checkpoints/smartbook-bilingual-v1/) remains intact.

For future requests, follow [SMARTBOOK_WORKING_METHOD.md](SMARTBOOK_WORKING_METHOD.md) and [BEGINNER_ENGLISH_ALIGNMENT.md](BEGINNER_ENGLISH_ALIGNMENT.md). Once Vietnamese is natural and high quality, **freeze it** and revise only English for beginner comprehension while cross-checking the original meaning.
