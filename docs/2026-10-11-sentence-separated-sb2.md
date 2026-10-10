# Second real Smart Book export — End of sentence

This is a **new native Smart Book export** of the same bilingual
*I Found a Unicorn* test story, created after the user confirmed the original
export imported successfully on Fairphone 6 / LineageOS.

The single intentional change from the previous export was **Paragraph
separator: End of sentence**, instead of **Empty string**.

## Build and artifact

- [Successful generation run](https://github.com/kd40000-dot/ebooks/actions/runs/38095979232)
- GitHub artifact: `smartbook-android-evidence`, containing
  `artifacts/I_Found_a_Unicorn_native.sb2`
- Output size: **9,916 bytes**
- SHA-256: `7c552075459c0f476a23b9fdb33138f16ffc89ce1fff0c17f5aa55456cb459cd`
- Native encrypted `.sb` entries: 2 (book metadata and one chapter)
- Archive contains 3 entries including the directory.
- Vietnamese source: `books/unicorn/vietnamese_hyphenated.txt`
- English source: `books/unicorn/english.txt`

## Verified logs

- `PARAGRAPH_SEPARATOR_VERIFIED: End of sentence`
- `ENGLISH_TRANSLATION_ATTACHED_BEFORE_SAVE`
- `GENUINE_APP_GENERATED_SB2`

The export's encrypted internal content wasn't decrypted, but these logs
and the ZIP entries confirm a new app-produced package. Importing
and checking sentence/translation behavior on a separate device are still
pending.

**Known semantic caveat:** Vietnamese and English sentence boundaries
do not always coincide. The user's requested End of sentence mode is
worth testing specifically for translation alignment and tapping behavior.
If misaligned, retaining the original 16-paragraph mode is the fallback.

The previous verified app-generated export is documented in
[the first export report](2026-10-10-first-real-sb2.md).
