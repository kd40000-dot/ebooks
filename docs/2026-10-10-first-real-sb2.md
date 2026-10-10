# First genuine Smart Book SB2 export — 2026-10-10

## Result

The GitHub-hosted Android emulator workflow successfully generated a real, encrypted
KursX Smart Book `.sb2` from the user-provided *I Found a Unicorn* bilingual source.

- [Successful generation run](https://github.com/kd40000-dot/ebooks/actions/runs/38095221920)
- Artifact: `smartbook-android-evidence` (the downloaded artifact contains
  `artifacts/I_Found_a_Unicorn_native.sb2`)
- Native file: `i_found_a_unicorn.sb2`
- Size: **9,309 bytes**
- SHA-256: `6079dc2b1fe49f20462b3d3aee4ae4428e26b38ffc6e170d7364b423e95f6a8d`
- ZIP: Deflate compression; one encrypted metadata `.sb`, one encrypted chapter `.sb`, plus directory entry.
- Filename pattern: `i_found_a_unicorn_1791675299276.sb` and
  `i_found_a_unicorn_1791675299276/1# vietnamese_hyphenated.sb`.

**Verification status:** The output is from the real Android Smart Book app and the ZIP
container and encryption flags were inspected. Importing and testing its bilingual
translation on the user's Fairphone 6 has **not yet** been verified. Do not label
reader compatibility as verified until an import test succeeds.

## User-recorded UI workflow

The uploaded screen recordings `54310.mp4` and `54311.mp4` demonstrate:

1. Library → My Books → Add Book → Create a parallel book.
2. Set book name, primary language **Vietnamese**, and UTF-8.
3. Import `books/unicorn/vietnamese_hyphenated.txt` as a chapter.
4. Open the chapter's adjacent **three-dot menu**, choose **Translation**,
   then **Upload a file** and select `books/unicorn/english.txt`.
5. Save the bilingual book.
6. From the library, open the saved book's **chapter-list screen**.
7. Tap the **top-right Share icon** on that screen (not the reader hamburger
   or Book settings).
8. The Android Sharesheet is offered a native `.sb2` file; select a compatible
   receiving app to save a copy.

These source recordings were supplied privately in the conversation and were
not committed to GitHub.

## Automation specifics

`scripts/automate_android.py` drives Smart Book itself and installs a local
ACTION_SEND receiving application (`scripts/build_share_sink.sh`) inside the
emulator. The receiver writes the bytes shared by Smart Book unchanged to an
Android app-specific external directory. The automation pulls those bytes, then
checks for the app-native encrypted `.sb` metadata/chapter structure.

The working receiver/saved copy is included in the GitHub Actions artifact.
Workflow artifacts have limited retention (currently seven days), so keep a
separate copy of the final `.sb2` for permanent archiving.

## Next milestones

- Import the package into Smart Book on the Fairphone 6 and confirm Vietnamese
  primary text, semantic hyphens, and English translation display correctly.
- Package the successful automation into a repeatable converter taking arbitrary
  aligned Vietnamese and English TXT chapters as input.
- Persist successful exports durably (for example as GitHub Release assets)
  instead of relying solely on short-lived GitHub Actions artifacts.
