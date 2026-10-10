# Experimental SB2 import failure — 2026-10-10

## Test context

- Device: Fairphone 6 running LineageOS (Android).
- Reader: KursX Smart Book.
- Story: *I Found a Unicorn*. Source in `books/unicorn/` (16 English paragraphs and 16 semantically hyphenated Vietnamese paragraphs).
- Candidate packages: a generated, **unencrypted** Zip/Deflate `.sb2`, and an encrypted ZipCrypto `.sb2` using a **test-only** password.
- User tested experimental imports and supplied two screenshots. We do **not** know which specific candidate produced each screenshot.

## Observed Smart Book error text

1. `net.lingala.zip4j.exception.ZipException: invalid CRC for file: i_fou...` (filename truncated in the toast)
2. `The book has not been downloaded completely, please redownload it`

## Interpretation

An invalid CRC after ZIP extraction is consistent with a wrong ZIP decryption password or corrupt content. The test-only password is **not** the Smart Book password. A successful local `zipfile.testzip()` check only means the archive can be read by ordinary ZIP readers; it does not validate the format or compatibility with Smart Book.

The "not downloaded completely" toast may be a generic downstream error, not evidence that a network download was attempted.

Because the archive contents were based on an old Parallator JSON data model, successful decryption alone would **not** guarantee a valid book. Do not make guesses about the native serializer without a genuine plaintext sample or a supported exporter.

## Decision

**Mark synthetic SB2 generation as not working.** Stop presenting the prototypes as importable. Prioritize having the Smart Book Android app import paired UTF-8 TXT paragraphs and generate/export its own valid `.sb2`.

## Next steps

1. Stage the paired TXT files on the Android device with `scripts/stage_android.sh`.
2. On the app's book-creation screen, gather an ADB UI dump with `scripts/capture_android_ui.sh`.
3. Create a small book in the app and capture the steps needed to add Vietnamese primary and English translation.
4. Automate import/export using Android UI Automator or ADB, using dynamic element IDs where available and screen-relative coordinates where not.
5. Keep exported genuine `.sb2` files as fixtures locally; avoid committing copyrighted material or private screenshots without review.

Screenshots were supplied in the ChatGPT conversation and are intentionally not copied into this repository.
