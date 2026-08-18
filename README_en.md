**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md)


# manga-mobi2cbz

A batch-conversion CLI tool built for Kindle manga: convert DRM-free MOBI / AZW / AZW3 ebooks into standard CBZ comic packages with one command.
It natively follows the OPF spine reading order to extract images, and comes with a full set of practical capabilities: automatic cover repair, same-volume multi-format deduplication, batch timeout protection, file integrity verification, and multi-language auto output. It also includes an `--inspect` exploration mode that lets you inspect comic metadata, resolution, NCX table of contents, and DRM status without packing. Cross-platform, efficient and stable for batch organizing your manga library.

> ⚠️ Only supports DRM-free Kindle comics. Store-purchased DRM-protected eBooks cannot be parsed.
>
> ⚠️ The code is entirely AI-generated. I cannot audit it line by line; please evaluate the risks before use.
>
> 📝 Note: This project is for personal use, intended to preserve AI-generated scripts for future reuse.
>
> **Project Origin**: It began with converting my own Kindle comics, having AI generate scripts each time. To simplify reuse and avoid losing scripts, I uploaded them to GitHub.
> Later usage revealed issues such as incorrect page order, missing covers, and batch processing hangs, prompting continuous modification requests to the AI. Unable to read code, I adopted a workflow of submitting the same code to different AIs for cross-validation to ensure reliability. What started as a one-off script evolved through iteration into its current form. The code is entirely AI-generated; I only define requirements and verify results. It is not professional, but significantly more complete than the initial version. If you have similar needs, feel free to use it; if you find issues, feedback is welcome—I will continue to have the AI fix them.


## Features

- **Batch conversion** — convert a single file or an entire directory recursively (`.mobi` / `.azw` / `.azw3`)
- **OPF spine ordering** — extract images in OPF spine order to preserve the real reading order; falls back to natural filename sorting when no OPF exists
- **Cover fallback** — automatically scans for images whose filenames contain cover/front; if the cover is already in the spine list, the list order wins, and it is only inserted at the front when missing
- **Directory alignment fallback** — when the image count in the directory differs from the collected count, extra images are appended to the end of the cbz in natural order by default; `--drop-extra` switches to dropping them instead, and the outcome is printed
- **Dual-directory deduplication** — automatically detects mobi7/mobi8 dual directories and keeps the copy that has content (default `auto`: prefers mobi8, falls back to mobi7 when mobi8 has no images; explicitly specifying `mobi7`/`mobi8` also falls back to the other when the chosen directory has no images)
- **Lightweight i18n** — `--language auto|zh-CN|zh-TW|ja|en` switches the UI language (default `auto` follows the system locale: Simplified Chinese → zh-CN, Traditional Chinese → zh-TW, Japanese → ja, otherwise → en).
- Runtime messages and `--help` follow the selected language; CLI flag names, enums, and technical terms (OPF, DRM, spine, etc.) stay in English.
- **Same-name extension deduplication** — when files in the same directory differ only by extension (e.g. `Vol1.mobi` + `Vol1.azw3`), only one is kept; `--ext-priority` controls the keep priority (default azw3)
- **Natural sorting** — sorts by page number naturally, avoiding `10.jpg` being placed before `2.jpg`
- **Integrity verification** — automatically verifies the CBZ file after conversion; corrupt output is deleted and reported
- **ComicInfo.xml metadata** — generates ComicInfo.xml in the CBZ root by default (UTF-8, with XML declaration), writing Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary metadata; Series/Number are inferred with high confidence from the filename (supporting `001` / `01` / `1` / `Vol.01` / `Vol 01` / `Volume 01` / `第 01 卷` forms); volume markers without a series name (e.g. `Vol.01` / `01巻`) are not inferred, and fields are omitted when confidence is insufficient (better missing than wrong); fields without a reliable source are omitted (no empty tags); `--no-comicinfo` disables generation
- **No-compression packing** — images are already compressed; ZIP defaults to store-only for speed and small output
- **Optional compression** — `--compress LEVEL` enables deflate compression (1-9), which can significantly shrink PNG-source manga; higher levels are smaller but slower; JPEG sources benefit little, not recommended (default `0` = no compression)
- **Inspect mode** — `--inspect` randomly samples one ebook (`--inspect-all` for every file). It unpacks only to read internal information and does not create a CBZ; temporary files are removed afterwards.
- Reports include basic checks (magic bytes, size, DRM), EXTH metadata when present, mobi7/mobi8 markers, OPF/spine counts (first five filenames), NCX preview, image totals, cover detection, format distribution, dominant resolution, and compression advice.
- DRM handling: header flag set → treated as DRM and skip unpacking; no flag and zero images → suspected DRM; no flag and images found → not DRM.
- **Optional source deletion** — `--delete` automatically deletes the original ebook after successful conversion
- **Force overwrite** — `--overwrite` forcibly regenerates existing cbz files, so you don't need to delete old files manually after updating manga
- **Per-file timeout protection** — `--timeout` limits conversion time per file; when a corrupt/encrypted/oversized ebook blocks the underlying unpacking indefinitely, it is skipped automatically and counted as failed instead of stalling the whole batch (default 600 seconds, `0` means no limit)
- **Quiet mode** — `--quiet` shows only errors and the summary during batch conversion instead of flooding the screen; `--log FILE` appends all output to a log file
- **Compact summary** — `--short-summary` shows only counts (not paths) for succeeded/skipped/precheck-skipped files (failed files always list full paths), complementary to `--quiet`, ideal for large directories
- **DRM encryption detection** — clearly reports when it encounters DRM-encrypted Kindle manga instead of failing silently
- **Path case compatibility** — cover comparison and directory alignment use normalized lowercase paths, so case-only naming differences are not misjudged as duplicates/missing on case-insensitive Windows filesystems
- **Output timestamps** — every output line is prefixed with `[YYYY-MM-DD HH:MM:SS]`, consistent across console and log files, making it easy to pinpoint when each conversion ran
- **Custom output directory** — `--output-dir DIR` outputs CBZ to a specified directory (auto-created); by default it preserves the relative subdirectory structure of the input (e.g. `One Piece/001.mobi` → `DIR/One Piece/001.cbz`); add `--flatten` to flatten everything into the directory root; same-name files are skipped (SKIP) unless `--overwrite` is given
- **Precheck filtering** — 0-byte files and ebooks with a corrupt header (no `BOOKMOBI` magic at offset 60) are skipped directly at the precheck stage, with the full path and reason logged
- **Minimum-size filtering** — `--min-size BYTES` filters out ebooks smaller than the given byte count (default 1000 when no number is given, `0` disables, not passing it disables size filtering), catching edge-corrupt samples whose header is intact but content is truncated
- **Dry-run mode** — `--dry-run` only scans and prints the conversion flow without actually unpacking/packing, handy for previewing results first
- **Resume support** — if the target CBZ already exists and passes integrity verification, it is skipped (SKIP); corrupt/invalid output is automatically reconverted; when the source file is newer than the target CBZ it is automatically reconverted too; `--overwrite` unconditionally overwrites
- **Failure classification** — conversion failures are counted by reason (`timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other`), with per-category counts shown in the summary
- **Inspect supports CBZ** — `--inspect` can inspect `.cbz` files directly (pure zipfile reading, no unpacking); cover line gains resolution+size, format stats gain total file count, and each of the first 5 Spine entries gains width/height
- **ComicInfo field override** — `--setinfo FIELD=VALUE` overrides/adds ComicInfo fields (highest priority); VALUE supports fixed values / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN` placeholders, repeatable; FIELD must be in the ComicInfo standard-field whitelist (39 simple fields, complex `Pages` excluded; out-of-whitelist fields emit a warning and are ignored); when the input is an existing `.cbz`, its ComicInfo.xml is modified in place (unspecified fields keep their original values, written via temp file + atomic replace)
- **Auto-named log** — `--log` without a filename auto-generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory)
- **Unpack mode** — `--unpack` only extracts without converting, outputting to a same-name subdirectory next to each source file (auto-numbered `(2)(3)` if it already exists); mobi uses extract preserving the full structure, cbz uses extractall (with zip-slip path-traversal protection); `.cbz` inputs are also collected when `--unpack` or `--setinfo` is given
- **Elapsed-time stats** — per-file conversion time is printed in real time, and the total elapsed time is shown at the bottom of the summary

## Supported image formats

The following image formats are recognized and packed during conversion: `.jpg` / `.jpeg` / `.png` / `.gif` / `.webp` / `.bmp` / `.tiff` / `.tif`

## Requirements

- Python 3.10+
- Dependency: `mobi`

## Installation

```bash
pip install mobi
```

## Usage

### Convert a single file

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi"
```

### Batch-convert an entire directory (recursively searches all .mobi / .azw / .azw3)

```bash
python manga-mobi2cbz.py "D:\Manga"
```

### Delete the original ebook after successful conversion

```bash
python manga-mobi2cbz.py "D:\Manga" --delete
```

### Keep the mobi7 version when a dual-directory mobi is present

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --prefer mobi7
```

### Drop extra images in the directory instead of appending them

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --drop-extra
```

### Force regeneration when a cbz already exists

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --overwrite
```

### Limit per-file conversion timeout (prevents corrupt files from stalling batch jobs)

```bash
python manga-mobi2cbz.py "D:\Manga" --timeout 300
```

### Output to a custom directory (preserves relative subdirectory structure by default)

```bash
python manga-mobi2cbz.py "D:\Manga" --output-dir "E:\CBZ"
```

### Flatten output (all CBZ files go directly to the output directory root)

```bash
python manga-mobi2cbz.py "D:\Manga" --output-dir "E:\CBZ" --flatten
```

### Dry run: only scan and print the conversion flow, without actually converting

```bash
python manga-mobi2cbz.py "D:\Manga" --dry-run
```

### Quiet mode + write output to a log

```bash
python manga-mobi2cbz.py "D:\Manga" --quiet --log convert.log
```

### Compact summary (large directories, success/skip shown as counts only)

```bash
python manga-mobi2cbz.py "D:\Manga" --quiet --short-summary --log convert.log
```

### Enable zip compression (can significantly shrink PNG-source manga)

```bash
python manga-mobi2cbz.py "D:\Manga" --compress 9
```

### Inspect mode: randomly sample 1 ebook's internal info (metadata/structure/images/resolution/DRM/NCX TOC)

```bash
python manga-mobi2cbz.py "D:\Manga" --inspect
```

### Inspect all ebooks' internal info

```bash
python manga-mobi2cbz.py "D:\Manga" --inspect --inspect-all
```

### Override/add ComicInfo fields (repeatable, highest priority)

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --setinfo "Title=天是紅河岸" --setinfo "Number=%number" --setinfo "Summary=hello, world"
```

### Unpack to view (extract only, no conversion; output to a same-name subdirectory)

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --unpack
```

### Show version

```bash
python manga-mobi2cbz.py --version
```

## Parameter reference

| Parameter               | Description                                                                                                                      |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `target`                | Path to an ebook file or a directory containing ebooks (.mobi/.azw/.azw3) (required)                                              |
| `--language LANG`       | Output language: `auto` selects by system locale (zh prefix → Chinese, zh-TW/zh-Hant → Traditional Chinese, ja/Japanese → Japanese, otherwise → English), or specify `zh-CN`/`zh-TW`/`ja`/`en` (default `auto`); tolerant of common spellings: `zh`/`cn`→zh-CN, `zhtw`/`tw`→zh-TW, `jp`→ja, `eng`→en |
| `--delete`              | Delete the original ebook file after successful conversion (default: keep)                                                        |
| `--prefer`              | Which copy to keep for dual-directory mobi: `auto` / `mobi7` / `mobi8` (default `auto`); `auto` prefers mobi8 and falls back to mobi7 when mobi8 has no images; explicitly specifying `mobi7`/`mobi8` falls back to the other when the chosen directory has no images |
| `--drop-extra`          | Drop uncollected extra images in the directory (default: append to the end of the cbz)                                            |
| `--overwrite`           | Force regeneration when the target cbz already exists (default: skip)                                                            |
| `--ext-priority EXTS`   | Which format to keep when files share the same name in the same directory (differing only by extension): comma-separated, order = priority high→low, accepts only mobi/azw/azw3, default azw3; groups not covered fall back to azw3→mobi→azw; unrelated to `--prefer` (dual-directory selection) |
| `--timeout`             | Per-file conversion timeout in seconds; timeout files are skipped and counted as failed (default 600, `0` = no limit)              |
| `--min-size BYTES`      | Filter out ebooks smaller than the given bytes; default 1000 without a number, `0` disables, not passing it disables size filtering |
| `--output-dir DIR`      | Output CBZ to the specified directory (auto-created); preserves the relative subdirectory structure of the input by default (e.g. `One Piece/001.mobi` → `DIR/One Piece/001.cbz`); add `--flatten` to flatten into the directory root |
| `--flatten`              | Only used together with `--output-dir`: flattens all CBZ files into the output directory root; same-name files are skipped (SKIP) unless `--overwrite` is given, which overwrites the preferred name; using it alone (without `--output-dir`) exits with an error |
| `--progress`            | Force the per-file progress bar (auto-shown by default when stderr is TTY and file count ≥ 2; when passed with `--no-progress`, the last one wins; kept by default under `--quiet`; writes to stderr, not into `--log`) |
| `--no-progress`         | Force-disable the progress bar (even when TTY and file count ≥ 2)                                                                 |
| `--dry-run`             | Dry run: only scan files and print the conversion flow, without unpacking/packing or creating output directories                   |
| `--quiet`               | Quiet mode: only show errors and the final summary                                                                                |
| `--short-summary`       | Compact summary: succeeded/skipped files show counts only (failed files always list full paths)                                    |
| `--compress LEVEL`      | zip compression level 0-9: `0` = no compression (default, images are already compressed), `1-9` = deflate (benefits PNG sources; higher = smaller but slower) |
| `--inspect`             | Inspect mode: inspect the file directly when the positional argument is a single file, or randomly sample 1 ebook for a directory; unpack only to read internal info (metadata/structure/images/resolution/dual DRM judgment/NCX TOC), no CBZ produced, temp directory cleaned up automatically |
| `--inspect-all`         | Inspect all ebooks (requires `--inspect`; using it alone will auto-enable `--inspect`)                                                                |
| `--no-comicinfo`        | Do not generate ComicInfo.xml (default: generates it into the CBZ root with Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary metadata)                                                          |
| `--setinfo FIELD=VALUE` | Override/add ComicInfo fields (repeatable, highest priority): `FIELD` is a ComicInfo field name and must be in the standard-field whitelist (39 simple fields; out-of-whitelist fields emit a warning and are ignored); `VALUE` supports fixed values / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN` placeholders (field omitted when the placeholder value is missing); smart splitting: only splits when a comma is followed by `fieldname=`, otherwise the comma is part of the value (e.g. `Summary=hello, world` is not split); when the input is an existing `.cbz`, its ComicInfo.xml is modified in place (unspecified fields keep their original values) |
| `--unpack`              | Unpack to view: extract only, no conversion; outputs to a same-name subdirectory next to each source file (auto-numbered `(2)(3)` if it already exists); mobi uses extract preserving the full structure, cbz uses extractall (with zip-slip path-traversal protection); `.cbz` inputs are also collected |
| `--log FILE`            | Append all output to the specified log file; without a filename, auto-generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory)                                                                                       |
| `--version`             | Show version number                                                                                                               |

## Output

- By default, the converted `.cbz` file is placed in the same directory as the original ebook; with `--output-dir`, it goes to that directory (auto-created), preserving the relative subdirectory structure of the input, or flattened into the directory root with `--flatten` (same-name files are skipped unless `--overwrite` is given)
- Existing `.cbz` files are skipped by default and never overwritten; use `--overwrite` to force regeneration
- 0-byte / corrupt-header ebooks are skipped at the precheck stage, with the full path and reason logged
- Per-file conversion time is printed in real time; total elapsed time is shown at the bottom of the summary
- Failed files print an error message and do not block conversion of other files

## Known limitations

- **DRM-encrypted mobi is not supported** — the underlying mobi library cannot decrypt DRM-encrypted manga purchased from the Kindle store; such files are clearly reported as "possibly DRM-encrypted" and skipped rather than silently producing an empty cbz. Remove DRM before converting
- **Threads cannot be force-terminated after timeout** — when a single file exceeds `--timeout`, the main flow skips it and continues, but Python cannot kill a blocked unpacking thread; the stuck thread lingers until the process exits, continuously consuming memory/IO; batch-processing many corrupt files may accumulate zombie threads in the background. To fully isolate stuck jobs, `multiprocessing` could be used for terminable child processes, but that adds cross-platform complexity and has not been adopted yet

## FAQ

**Q: The image order in the converted CBZ is messed up?**
A: Images are extracted in OPF spine order (the EPUB standard reading order) first, which is correct in the vast majority of cases; if the source has no OPF or the spine extraction is empty, it falls back to natural filename sorting. If the issue persists, the original mobi's internal image naming may be inconsistent — please check the source file.

**Q: Why is the cover missing from the CBZ?**
A: Some mobi covers are only referenced by the OPF metadata cover meta and are not referenced by the spine, so spine-based extraction misses them. The script automatically scans for images whose filenames contain cover/front and inserts one at the front when missing; if the cover is already in the spine list, the original order is kept. If the cover filename contains none of those keywords, it may still be missed — rename it and reconvert.

**Q: Why are some mobi files very small after conversion?**
A: Dual-directory mobi (mobi7+mobi8) keeps only one copy by default (`--prefer auto`): it prefers mobi8 and falls back to mobi7 when mobi8 has no images, avoiding duplicated content doubling the size. Add `--prefer mobi7` to force keeping mobi7.

**Q: Batch conversion stalls on a corrupt/encrypted mobi?**
A: Per-file conversion has a 600-second timeout by default (`--timeout` adjustable); on timeout the file is skipped automatically and counted as failed, and the main flow continues with the remaining files. If you notice a file stalling earlier, use a smaller value like `--timeout 30` to skip it faster, or `--quiet` to reduce output.

**Q: Why does --output-dir keep the subdirectories now?**
A: Since v1.9.0, `--output-dir` preserves the relative subdirectory structure of the input by default (a breaking change from the old flat behavior). Add `--flatten` to flatten instead; change the old command `python manga-mobi2cbz.py Manga --output-dir CBZ` to `python manga-mobi2cbz.py Manga --output-dir CBZ --flatten` to restore the old flat behavior.

**Q: Are .azw / .azw3 supported?**
A: Yes. Since v1.8.0 the accepted input extensions are `.mobi` / `.azw` / `.azw3`, all three going through the same conversion pipeline; for same-name files with different extensions in the same directory, azw3 is kept by default, adjustable via `--ext-priority`.

## Changelog

### [2.2.0] - 2026-08-18

#### Added

- **CBZ modification mode** — when the input is an existing `.cbz` and `--setinfo` is given, its ComicInfo.xml is modified directly: read the original XML → overwrite the specified fields, keep unspecified fields at their original values → write via temp file + atomic replace (`os.replace`); covered by `--dry-run` preview / summary stats / `--log`
- **setinfo whitelist** — `--setinfo` field names must be within the ComicInfo standard-field whitelist (39 simple fields, complex `Pages` excluded); out-of-whitelist fields emit a warning and are ignored
- **Source-newer auto-reconvert** — resume support now compares the source file's mtime with the target CBZ's; when the source is newer, it is automatically reconverted
- **`--unpack` / `--setinfo` accept CBZ input** — the collection stage also gathers `.cbz` files when `--unpack` or `--setinfo` is given
- **`--prefer auto` (default)** — dual-directory mobi now defaults to auto: prefers mobi8, falls back to mobi7 when mobi8 has no images; explicitly specifying `mobi7`/`mobi8` falls back to the other when the chosen directory has no images
- **Summary HTML cleanup** — the ComicInfo Summary field strips HTML tags (plain text written to disk)
- **Cover-source annotation** — the ComicInfo Notes field appends `CoverSource` (OPF guide / filename match)
- **CBZ precheck** — `.cbz` inputs now also go through 0-byte / `--min-size` checks
- **`--inspect` PageCount consistency check** — compares the ComicInfo PageCount inside a CBZ with the actual image count and reports a mismatch

#### Changed

- **`--unpack` path safety** — cbz unpacking gains zip-slip path-traversal protection (rejects `..` / absolute-path entries) and prints an unpack summary
- **Multiple OPF warning** — when a directory contains more than one `.opf`, a warning is emitted and the first one is used
- **Corrupt-CBZ reconvert reason** — the resume path now prints the specific `validate_cbz` failure reason when reconverting a corrupt CBZ
- **HTML image path compatibility** — `<img>` src extraction strips query / fragment (`?` / `#`) before resolving the local path
- **Directory creation timing** — no longer creates the output directory early when the target CBZ already exists and will be SKIPped
- **Code hygiene** — `ebook_to_cbz` return-type annotation completed to the triple; `_auto_language` tail made explicit

### [2.1.0] - 2026-08-17

#### Added

- **Resume support (default behavior)** — if the target CBZ already exists and passes `validate_cbz`, it is skipped (SKIP); corrupt/invalid output is automatically reconverted; `--overwrite` unconditionally overwrites
- **Failure classification** — `ebook_to_cbz` now returns a triple `(result, status, reason)`; failure reasons are categorized as `timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other`; the main flow adds a `failed_reasons` counter shown in the summary
- **`--inspect` supports CBZ** — merged into `inspect_ebook`; the CBZ branch reads purely via zipfile without unpacking; extracted `image_dimensions_bytes(bytes)` for reuse
- **`--inspect` output enhancement** — cover line gains resolution+size, format stats gain total file count, and each of the first 5 Spine entries gains width/height
- **`--setinfo FIELD=VALUE`** — override/add ComicInfo fields (repeatable, highest priority); VALUE supports fixed values / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN`; smart splitting (only splits when a comma is followed by `fieldname=`); CBZ modification mode rewrites the zip directly; the `--inspect` preview block applies it too
- **ComicInfo written in the same zip pass** — removed the `write_comicinfo` function; `zf.writestr` inside the Step4 `with` block
- **`--log` auto-naming** — `nargs="?"` + `const="auto"`; auto generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory)
- **`--unpack` unpack-to-view** — extract only, no conversion; mobi uses extract preserving the full structure, cbz uses extractall; defaults to a same-name directory, auto-numbered `(2)(3)` if it already exists

### [2.0.2] - 2026-08-17

#### Changed

- `infer_series_number` now supports parenthesized suffixes: a `(author)` suffix no longer blocks volume inference (e.g. `天是紅河岸 - 第23卷 (筱原千繪)` correctly infers Series=天是紅河岸 / Number=23)
- Pure volume markers (`Vol.01` / `第 01 卷` / `01巻` etc.) now return only the volume number `(None, number)` instead of `(None, None)`, so ComicInfo can write Number
- `--flatten` same-name handling changed to SKIP/`--overwrite`: same-name files in the flat output root are no longer auto-renamed and re-converted as `(2).cbz`; without `--overwrite` they are skipped (SKIP), with it the preferred name is overwritten; dry-run stays consistent with the real run
- Removed the now-unused `unique_path` function

#### Fixed

- Fixed PageCount consistency: physical dedup now happens before ComicInfo generation; both PageCount and packaging use the deduplicated actual written count
- Fixed `run_with_timeout` cross-version: except now catches both built-in `TimeoutError` and `concurrent.futures.TimeoutError` (Python 3.10 compatible)
- Fixed `infer_series_number` dot failure: now uses `path.name` with manual extension removal, so dotted volume numbers like `One Piece Vol.01` infer correctly
- LanguageISO whitelist + alias: full ISO 639-1 whitelist (184 codes) plus common aliases `jp→ja` / `cn→zh` / `zhtw→zh`
- Year strict date parsing: prefers full date fields; ranges/multi-values (`2001-2005`) return None
- `emit` warning now visible under `--quiet`
- EXTH loop variable `t` renamed to `type_id` to avoid shadowing the global `t()`
- Regex img src extraction now applies `unquote`, consistent with the HtmlImgParser fallback path
- `--language` tolerance: accepts common spellings like `zh`/`cn`/`zhtw`/`jp` via new `_normalize_lang` (argparse `choices` restriction removed)

### [2.0.1] - 2026-08-17

#### Fixed

- Fixed `infer_series_number` incorrectly inferring a series name from volume-marker-only filenames (`Vol.01` / `Volume 01` / `01巻` etc.); added the `_is_volume_marker` volume-marker filter

### [2.0.0] - 2026-08-14

#### Added

- Generates ComicInfo.xml by default (written into the CBZ ZIP root, UTF-8 with XML declaration); new `--no-comicinfo` flag disables it
- New functions: `build_comicinfo` (built with `xml.etree.ElementTree`, no manual string concatenation), `write_comicinfo`, `normalize_language` (normalizes language codes to ISO 639-1), `infer_series_number` (high-confidence Series/Number inference from the filename, supporting `001`/`01`/`1`/`Vol.01`/`Vol 01`/`Volume 01`/`第 01 卷` forms; returns None when confidence is insufficient — better missing than wrong)
- Field mapping: Title=OPF title→EXTH title→filename stem, Writer=OPF creator→EXTH author, Publisher=OPF publisher→EXTH publisher, Year=PublicationDate year, LanguageISO=the ebook's own language (not guessed from the filename), PageCount=the actual image count written into the CBZ (always written), Series/Number=high-confidence filename inference, Summary=OPF description (written only when present); fields without a reliable source are omitted (no empty tags)
- Flow insertion: ComicInfo is built after the final image set is determined, then written into the CBZ together with the images; integrity verification adds 3 checks (ComicInfo.xml exists, parseable by a standard XML parser, root node is ComicInfo); ComicInfo generation or verification failure = the whole conversion fails, and `--delete` must not delete the source file
- `--dry-run` does not create ComicInfo.xml but prints one line indicating whether ComicInfo is enabled
- `--inspect` output gains a ComicInfo preview block (Title/Series/Number/Writer/Publisher/Year/LanguageISO/PageCount/Summary shown only when present), with inferred fields clearly marked `[inferred]`
- i18n: 6 new keys across all four languages: `comicinfo.generating` / `comicinfo.created` / `comicinfo.disabled` / `comicinfo.invalid` / `comicinfo.inferred` / `help.no_comicinfo`

### [1.9.1] - 2026-08-14

#### Added

- `--inspect-all` used alone (without `--inspect`) now auto-enables `--inspect` and prints a warning (new key `warn.inspect_all_auto_enable` in all four languages)
- `--inspect` help updated: a single-file positional argument inspects that file directly; a directory samples 1 ebook randomly
- `--inspect-all` help updated: requires `--inspect`; using it alone will auto-enable `--inspect`

### [1.9.0] - 2026-08-14

#### Breaking Change

- `--output-dir DIR` changed from "flatten everything into DIR" to "**preserve the relative subdirectory structure of the input by default**" (e.g. `One Piece/001.mobi` → `DIR/One Piece/001.cbz`)
- Migration: the old command `python manga-mobi2cbz.py Manga --output-dir CBZ` must be changed to `python manga-mobi2cbz.py Manga --output-dir CBZ --flatten` to restore the "flatten" behavior

#### Added

- `--flatten`: only used together with `--output-dir`; flattens all CBZ files into the output directory root; flat naming rules: file directly under the input root → `stem`, in a subdirectory → `parent dir name - stem`; illegal filename characters (`<>:"/\|?*`) are replaced with `_`
- Automatic conflict uniquification in flat mode: `base.cbz` → `base (2).cbz` → `base (3).cbz` …, never silently overwrites or skips; an info message is printed when numbering occurs
- Using `--flatten` without `--output-dir` exits with an error (exit 2); the message is i18n-ized
- Prints one output-mode line per run (preserve structure / flatten); four language tables gain keys `output.mode_preserve` / `output.mode_flatten` / `output.renamed_due_to_conflict` / `output.flatten_requires_dir` / `error.flatten_without_output_dir` / `rel_fallback`
- If computing the relative subdirectory path fails (e.g. across drives), falls back to `DIR/stem.cbz` with a warning
- Single-file input + `--output-dir` outputs `DIR/stem.cbz` (no subdirectory wrapping)
- `--overwrite` semantics unchanged in preserve mode; in flat mode uniquification is preferred, and `--overwrite` still applies to the final chosen path

#### Refactored

- `target_cbz_path` gains `flatten` / `input_root` / `used_names` parameters; new standalone helpers `sanitize_filename_component` / `flat_base_name` / `unique_path`
- dry-run flat uniquification maintains a used-name set in processing order, consistent with real runs

#### Fixes & Enhancements (folded into v1.9.0, no version bump)

- `run_with_timeout` now returns a `(timed_out, result)` tuple: timeout → `(True, None)`, normal → `(False, function return value)`, removing the ambiguity between "timeout" and a normal `None` return
- `--inspect` timeout branch adds a hint that the extracted temp directory may be left behind and should be cleaned up manually (new key `inspect_mode.timeout_residue` in all four languages)
- Packing-stage `seen` now also uses normalized paths to detect physically duplicate files: the same physical file appearing more than once is skipped (same-name different files still get numeric prefixes), and a dedup count is printed (new key `convert.dedup_physical`)
- New `HtmlImgParser` (an `HTMLParser` subclass) fallback for extracting `<img src>`: HTML entities are auto-decoded by HTMLParser plus `unquote` for `%XX`; wired into OPF/spine HTML image extraction, enabled only when the regex misses; the ElementTree main flow is untouched
- `--dry-run` now checks whether the output directory (`--output-dir` or each source file's directory) is writable and warns when it is not (new key `dryrun.output_not_writable`)

### [1.8.0] - 2026-08-14

#### Added

- Lightweight i18n: `--language auto|zh-CN|zh-TW|ja|en` (default `auto` detects by system locale: Simplified → zh-CN, Traditional zh-TW/zh-Hant → zh-TW, Japanese ja/Japanese → ja, non-zh/ja → en); all output text and `--help` are translated with the language (`--help` is implemented by pre-parsing `--language` before building the parser); missing keys fall back en → key name without raising; business code never writes `if lang` branches; parameter names/enums/book metadata/OPF/DRM/spine and other technical terms are not translated; all `TAG_*` constants are removed and replaced with `t()` keys
- `.azw` / `.azw3` input support: accepted input extensions expanded to `.mobi` / `.azw` / `.azw3` (case-insensitive), all three reusing the same `extract → OPF/spine → cover → align → pack → verify` pipeline, no parallel implementations
- `--ext-priority EXTS`: which format to keep when files share the same name in the same directory (differing only by extension) — comma-separated, order = priority high→low, accepts only `mobi`/`azw`/`azw3`, default `azw3`; groups not covered by the priority fall back to azw3→mobi→azw with a warning; completely unrelated to `--prefer` (dual-directory mobi7/mobi8 selection)
- Same-name extension deduplication: only one file kept per same directory + same stem (group key `parent.resolve() + stem.lower()`); same-name files in different directories are not deduplicated; dedup happens before path computation and progress counting, skip reason is logged
- Magic-bytes precheck extended to all three formats: unified `BOOKMOBI` magic check at offset 60; files with the right extension but wrong magic (or anomalous `.azw/.azw3` magic) are no longer directly judged corrupt and skipped — a warning is printed and extraction is still attempted (`mobi.extract` has its own secondary validation; unpack failures are counted as failures normally)
- `--delete` and `--inspect` / `--inspect-all` support `.mobi` / `.azw` / `.azw3` uniformly
- Per-file progress bar: `--progress` forces it on, `--no-progress` forces it off; automatic by default (shown when stderr is TTY and file count ≥ 2, off when not TTY); when both are passed, the last one wins; kept by default under `--quiet`, closed by `--no-progress`; covers convert / inspect / dry-run modes; total strictly equals the final post-dedup list length, showing current/total, percentage, ETA, average time, and current filename (truncated to 40 chars); writes to stderr, not into emit/`--log`; tqdm is optional, degrading to a simple text progress without crashing when missing

#### Refactored

- `collect_mobi_files` renamed to `collect_ebook_files` (old alias `collect_mobi_files` kept for compatibility); `precheck_mobi` → `precheck_ebook`, `mobi_to_cbz` → `ebook_to_cbz`, `inspect_mobi` → `inspect_ebook`
- Input extension set constantized as `SUPPORTED_INPUT_EXTENSIONS`; `PREFER_EXT_ORDER` renamed to `KEEP_EXT_ORDER`
- docstring, CLI help, and runtime log wording unified to "ebook" (mobi file → ebook); help description changed to `mobi/azw/azw3 manga batch to cbz`

#### Code hygiene & UX polish (bundled into [1.8.0])

- Removed the duplicate `from concurrent.futures import ThreadPoolExecutor` import
- `LANGUAGES` dict gets functional-section Chinese comments (【预处理】【转换】【检查】【汇总】, including help/progress/tag sections)
- `--language auto` prints an INFO-level "detected language: X" message (suppressed under `--quiet`, via `emit` + `t()`)
- Magic-bytes check downgrade: `precheck_ebook` magic failure changed from "judge corrupt and skip" to a warning + still attempting extraction (`extract` has its own secondary validation; unpack failures count as failed)
- `--ext-priority` invalid-value error message i18n-ized (new `error.ext_priority_empty` / `error.ext_priority_invalid` keys in all four language tables)
- Chinese comments added to argparse parameter definitions and main function input parameters (describing input and output)

### [1.7.0] - 2026-08-13

#### Added

- `--compress LEVEL`: zip compression level 0-9, `0` = no compression (default, images already compressed), `1-9` = deflate; PNG sources can shrink significantly, higher = smaller but slower; JPEG sources benefit little, not recommended
- `--inspect` inspect mode: randomly samples 1 mobi (`--inspect-all` for all), unpacking only to read internal info without producing CBZ, temp directory cleaned up automatically afterwards; outputs basic checks (magic/size/DRM marker), EXTH metadata (title/author/language/publish date/publisher/ISBN, shown only when found), dual-directory markers, OPF and spine extraction counts, total image count, cover, image format distribution, dominant resolution (dominant height/width + range of the other dimension), compression advice; suspected DRM (no images) and unpack timeouts counted separately
- `--inspect` enhancements: cover detection prefers the OPF guide `type="cover"` official reference (falls back to filename matching); vertical preview of first 5 spine-extracted filenames; NCX (toc.ncx) entry count + preview of first 3 titles; EXTH metadata adds ASIN(type113) and copyright(type109); dual DRM judgment (header marker present → judged DRM and skips unpacking; no marker + 0 unpacked images → suspected; no marker + images → none), summary line adds DRM-marker count

#### Refactored

- Packing branch refactored: `compress>0` uses `ZIP_DEFLATED`+`compresslevel`, otherwise `ZIP_STORED`, eliminating the deprecation warning from old Python passing `compresslevel=None` under STORED
- `--inspect` dual-directory selection unified through the shared `select_mobi_dir` function (new prefer parameter controlled by `--prefer`) instead of hand-written logic; output indentation unified to 2 spaces, fixed inconsistent OPF line indentation

### [1.6.0] - 2026-08-13

#### Added

- `--output-dir DIR`: CBZ output to a specified directory (auto-created), no longer forced into the source mobi's directory; `--overwrite` existence check also based on the output directory
- Precheck filtering: 0-byte files and files failing header validation (no `BOOKMOBI` magic at offset 60, suspected corrupt or not mobi) are skipped directly, with full path and reason logged
- `--dry-run` dry-run mode: only scans and prechecks, prints each file's conversion flow and target output path, without unpacking/packing, creating output directories, or any disk writes, and prints the precheck filter list too (consistent with real runs)
- `--min-size BYTES`: filters out mobi smaller than the given bytes (default 1000 without a number, `0` disables, not passing it disables size filtering), catching edge-corrupt samples whose header is intact but content is truncated; precheck also adds an "unable to read file (OSError)" skip-reason branch
- Elapsed-time stats: per-file conversion time printed in real time, total elapsed time at the bottom of the summary (success/fail/skip all counted)
- Summary adds a one-line conversion stats row (success/skip/fail counts, including 0): when a category is 0, its detail lines are not printed, but the stats row always shows all three counts

#### Refactored

- Magic-string statuses refactored into the `ConvStatus` enum (`OK`/`SKIP`/`FAIL`); `mobi_to_cbz` return type changed to `tuple[Path | None, ConvStatus]`; main-loop branches and return sites use enum members uniformly to avoid typos
- Output labels extracted into constants (`TAG_INFO`/`TAG_FAIL`/`TAG_ERROR`/`TAG_SKIP`/`TAG_OVERWRITE`/`TAG_CLEAN`/`TAG_SORT`/`TAG_DEDUP`/`TAG_DONE`/`TAG_VERIFY`/`TAG_VERIFY_FAIL`/`TAG_TIMEOUT`/`TAG_ELAPSED`/`TAG_FILE`/`TAG_PENDING`/`TAG_WILL_SKIP`/`TAG_DRYRUN`) for centralized output styling
- Added comments to `run_with_timeout` on thread limits: after timeout, `mobi.extract` worker threads linger in the background consuming memory/IO; batch-processing many corrupt files may accumulate zombie threads; `multiprocessing` could be adopted later for terminable child processes but adds cross-platform complexity and has not been used yet
- Top-level global exception capture: `main()` wraps everything in `try/except`; uncaught exceptions and Ctrl+C outside the main loop (argument parsing/file collection) are printed with stack trace via `emit` to console and log (with timestamp) instead of a bare stack trace exit
- `--short-summary` compact summary: succeeded/skipped/precheck-skipped files show counts only (failed files always list full paths), unaffected by dry-run, complementary to `--quiet`

### [1.5.0] - 2026-08-13

#### Added

- `--timeout` per-file timeout protection: default 600 seconds; when a corrupt/encrypted/oversized mobi blocks the underlying `mobi.extract()` indefinitely, the file is skipped automatically and counted as failed instead of stalling the whole batch; `0` means no limit
- Path case compatibility: cover comparison and directory alignment use normalized lowercase paths, so case-only naming differences are not misjudged as duplicates/missing on case-insensitive Windows filesystems
- Output timestamps: every output line (console and `--log` file) is prefixed with `[YYYY-MM-DD HH:MM:SS]`, making it easy to pinpoint when each conversion ran

#### Changed

- Log write tolerance: `--log` write failures (invalid chars/overlong paths, disk full, read-only partition, file locked) no longer swallow exceptions silently; all `Exception`s are caught and a single warning is printed so users don't mistakenly believe the log was saved
- Ctrl+C interruption fallback: pressing Ctrl+C mid-batch no longer exits with a raw exception; the main loop catches `KeyboardInterrupt` and force-prints the progress summary of completed/failed files
- Summary completes the skip list: files skipped because the target cbz already exists (when `--overwrite` is off) are counted in "skipped files" and listed with full paths
- `--overwrite` regeneration marker keeps only the per-file `[overwrite]` log line, not in the final summary (written to the `--log` file)
- Removed the ineffective outer `TemporaryDirectory` fallback: extraction temp dirs are still cleaned uniformly by `extract_temp_paths` + `finally`

### [1.4.0] - 2026-08-13

#### Added

- Dependency check moved to the top of the module, validated at startup
- DRM encryption detection: when unpacking fails or no images are extracted, clearly reports the file may be DRM-encrypted Kindle manga that the mobi library cannot decrypt, avoiding silent failure
- `--overwrite` parameter: force regeneration when the target cbz already exists, no need to manually delete old cbz after updating manga
- `--quiet` quiet mode: only errors and the final summary, no screen flooding during batch conversion
- `--log FILE`: append all output to the specified log file
- Lists full paths of pending mobi files before conversion starts, and full paths of output cbz files after conversion completes
- Lists failed file count and full paths after conversion (files skipped because they already exist are not counted as failures)

#### Fixed

- Fixed temp-directory residue: `mobi.extract` does not support the `output_dir` parameter, changed to pass only the input file and record the extraction path it generates, cleaned uniformly in `finally` — no residue on normal/Ctrl+C/exception paths

### [1.3.0] - 2026-08-13

#### Added

- Cover fallback: after spine extraction, automatically scans for images whose filenames contain cover/front; if the cover is already in the list, the list order wins; only inserted at the front when missing
- Fixed page loss when the cover is only defined by the OPF metadata meta and not referenced by the spine (e.g. `cover00198.jpeg`)
- Directory alignment fallback: when the image count differs from the collected count, extra images are appended to the end of the cbz in natural order by default; `--drop-extra` switches to dropping them, and the outcome is printed

### [1.2.0] - 2026-08-13

#### Added

- OPF spine order image extraction: parses manifest and spine itemref, ordering by the real reading order
- `--version` parameter, `python manga-mobi2cbz.py --version` shows the version
- `select_mobi_dir` directory selection logic, preferring mobi7/mobi8 directory before extracting images
- Tiered sort fallback: falls back to natural filename sorting automatically when spine extraction is empty / OPF not found

#### Changed

- Duplicate image names get a sequence prefix (`{idx:04d}_`) to guarantee order and avoid collisions
- Script renamed to `manga-mobi2cbz.py`

### [1.1.0] - 2026-08-13

#### Added

- Version mechanism: `__version__` and `SCRIPT_NAME` constants

### [1.0.0] - 2026-08-12

#### Added

- First usable version: recursive mobi collection, batch cbz conversion, dual-directory deduplication, EOCD + testzip integrity verification, cleanup of failed half-products

## License

[MIT](./LICENSE)
