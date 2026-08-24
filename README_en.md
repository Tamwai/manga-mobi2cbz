**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md)

# manga-mobi2cbz

A batch-conversion CLI tool built for Kindle manga: convert DRM-free MOBI / AZW / AZW3 / EPUB ebooks into standard CBZ comic packages with one command.
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

- **Batch conversion** — convert a single file or an entire directory recursively (`.mobi` / `.azw` / `.azw3` / `.epub`)
- **OPF spine ordering** — extract images in OPF spine order to preserve the real reading order; falls back to natural filename sorting when no OPF exists
- **Cover fallback** — automatically scans for images whose filenames contain cover/front; if the cover is already in the spine list, the list order wins, and it is only inserted at the front when missing
- **Directory alignment fallback** — when the image count in the directory differs from the collected count, extra images are appended to the end of the cbz in natural order by default; `--drop-extra` switches to dropping them instead, and the extra image file names are listed one by one (only counts under `--short-summary`)
- **Dual-directory deduplication** — automatically detects mobi7/mobi8 dual directories and keeps the copy that has content (default `auto`: prefers mobi8, falls back to mobi7 when mobi8 has no images; explicitly specifying `mobi7`/`mobi8` also falls back to the other when the chosen directory has no images)
- **Lightweight i18n** — `--language auto|zh-CN|zh-TW|ja|en` switches the UI language (default `auto` follows the system locale: Simplified Chinese → zh-CN, Traditional Chinese → zh-TW, Japanese → ja, otherwise → en).
- Runtime messages and `--help` follow the selected language; CLI flag names, enums, and technical terms (OPF, DRM, spine, etc.) stay in English.
- **Same-name extension deduplication** — when files in the same directory differ only by extension (e.g. `Vol.01.mobi` + `Vol.01.azw3`), only one is kept; `--ext-priority` controls the keep priority (default azw3)
- **Natural sorting** — sorts by page number naturally, avoiding `10.jpg` being placed before `2.jpg`
- **Integrity verification** — automatically verifies the CBZ file after conversion; corrupt output is deleted and reported
- **ComicInfo.xml metadata** — generates ComicInfo.xml in the CBZ root by default (UTF-8, with XML declaration), writing Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary metadata; Series/Number are inferred with high confidence from the filename (supporting `001` / `01` / `1` / `Vol.01` / `Vol 01` / `Volume 01` / `第 01 卷` forms); volume markers without a series name (e.g. `Vol.01` / `01巻`) are not inferred, and fields are omitted when confidence is insufficient (better missing than wrong); fields without a reliable source are omitted (no empty tags); `--no-comicinfo` disables generation
- **No-compression packing** — images are already compressed; ZIP defaults to store-only for speed and small output
- **Optional compression** — `--compress LEVEL` enables deflate compression (1-9), which can significantly shrink PNG-source manga; higher levels are smaller but slower; JPEG sources benefit little, not recommended (default `0` = no compression)
- **Inspect mode** — `--inspect` samples one ebook by default (`sample`); `--inspect all` inspects every file (equivalent to the old `--inspect-all`). It unpacks only to read internal information and does not create a CBZ; temporary files are removed afterwards.
- Reports include basic checks (magic bytes, size, DRM), EXTH metadata when present, mobi7/mobi8 markers, OPF/spine counts (first five filenames), NCX preview, image totals, cover detection, format distribution, dominant resolution, a resolution summary (dominant count/percentage + abnormal small-image count), and compression advice.
- DRM handling: a DRM marker is treated as an informational flag only and never blocks inspection — unpacking is still attempted; if images are extracted the ebook is reported as readable with a `drm` marker; it is classified as DRM only when unpacking fails and the image count is 0.
- **Optional source deletion** — `--delete` automatically deletes the original ebook after successful conversion
- **Force overwrite** — `--overwrite` forcibly regenerates existing cbz files, so you don't need to delete old files manually after updating manga
- **Per-file timeout protection** — `--timeout` limits conversion time per file; when a corrupt/encrypted/oversized ebook blocks the underlying unpacking indefinitely, it is skipped automatically and counted as failed instead of stalling the whole batch (default 600 seconds, `0` means no limit)
- **Quiet mode** — `--quiet` shows only errors and the summary during batch conversion instead of flooding the screen; `--log FILE` appends all output to a log file
- **Compact summary** — `--short-summary` shows only counts (not paths) for succeeded/skipped/precheck-skipped files (failed files always list full paths), complementary to `--quiet`, ideal for large directories
- **DRM encryption detection** — clearly reports when it encounters DRM-encrypted Kindle manga instead of failing silently
- **Path case compatibility** — cover comparison and directory alignment use normalized lowercase paths, so case-only naming differences are not misjudged as duplicates/missing on case-insensitive Windows filesystems
- **Output timestamps** — every output line is prefixed with `[YYYY-MM-DD HH:MM:SS]`, consistent across console and log files, making it easy to pinpoint when each conversion ran
- **Custom output directory** — `--output-dir DIR` outputs CBZ to a specified directory (auto-created); by default it preserves the relative subdirectory structure of the input (e.g. `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`); add `--flatten` to flatten everything into the directory root; same-name files are skipped (SKIP) unless `--overwrite` is given
- **Precheck filtering** — 0-byte files and ebooks with a corrupt header (no `BOOKMOBI` magic at offset 60) are skipped directly at the precheck stage, with the full path and reason logged
- **Minimum-size filtering** — `--min-size BYTES` filters out ebooks smaller than the given byte count (default 1000 when no number is given, `0` disables, not passing it disables size filtering), catching edge-corrupt samples whose header is intact but content is truncated
- **Dry-run mode** — `--dry-run` only scans and prints the conversion flow without actually unpacking/packing, handy for previewing results first
- **Output renaming** — `--rename[=TEMPLATE]` renames the output CBZ filename (optional template, off by default): no value = default template (series name + auto-chosen marker prefix by type `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`, connected chapters `話005-006` → `[Ch.5-6]`); the template supports `%series` / `%number` / `%volume` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` and `%03number` zero-padding placeholders; source priority: filename inference > built-in metadata (OPF / ComicInfo.xml) fallback, `--setinfo` not involved; when the input is an existing `.cbz` it enters a standalone rename mode (renames only, no conversion, combinable with other modes); `%description` is not recommended for filenames (content may be too long) — pair it with `%subN_M` to truncate; pair with `--dry-run` to preview first
- **Color control** — `--no-color` disables ANSI color output (even when the terminal supports it); logs / JSON / pipes are never colored anyway
- **Classified rename-skip hints** — when `--rename` skips a file, two hint kinds are distinguished: target already exists on disk (suggest `--overwrite`) vs. collision within the current batch (suggest adjusting the naming template); both dry-run and non-dry-run paths apply, and the JSON `reason` field records `existing` / `conflict` respectively; the dry-run preview colors `[Will Skip]` by collision class (on-disk existing = yellow, in-batch conflict = magenta; TTY + not `--no-color` only), and the non-dry-run summary splits the skip total into "on-disk existing N / in-batch conflict M" with the skipped file list grouped by class
- **Resume support** — if the target CBZ already exists and passes integrity verification, it is skipped (SKIP); corrupt/invalid output is automatically reconverted; when the source file is newer than the target CBZ it is automatically reconverted too; `--overwrite` unconditionally overwrites
- **Failure classification** — conversion failures are counted by reason (`timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other`), with per-category counts shown in the summary
- **Inspect supports CBZ** — `--inspect` can inspect `.cbz` files directly (pure zipfile reading, no unpacking); cover line gains resolution+size, format stats gain total file count, and each of the first 5 Spine entries gains width/height
- **Read-only image listing** — `--list-images [FILTER]` lists every image of the target ebook (No. / filename / resolution / size / mode·depth / orientation / TOC / tag) plus a full statistics block (format / mode·depth / size distribution / double-page banners / animated GIF / small images / anomaly details), without converting, writing a CBZ, or generating ComicInfo; FILTER is optional and supports conditional expressions (format / `res` / `size` / orientation / mode / depth / tag, comma = OR, `+` = AND, `-` prefix = exclude)
- **Double-page detection** — `--double-page` identifies full-width spread images (width/height ≥ ratio, default 2.0); when enabled it writes per-page DoublePage marks (without a Manga declaration); no value / `auto` enables, a number sets the ratio, `off` / `no` / `0` disables
- **Drop small images** — `--drop-small` removes images whose width and height are both below median × ratio (default 0.5), such as cover thumbnails; PageCount is recalculated from the actual image count after dropping; no value / `auto` = 0.5, a 0~1 number sets the ratio, `off` / `no` / `0` disables
- **ComicInfo field override** — `--setinfo FIELD=VALUE` overrides/adds ComicInfo fields (highest priority); VALUE supports fixed values / `%series` / `%number` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` placeholders, repeatable; FIELD must be in the ComicInfo standard-field whitelist (39 simple fields, complex `Pages` excluded; out-of-whitelist fields emit a warning and are ignored); for existing `.cbz` inputs, `%series`/`%number`/`%volume` read the explicit Series/Number/Volume from ComicInfo first, falling back to filename inference only when absent; when the input is an existing `.cbz`, its ComicInfo.xml is modified in place (unspecified fields keep their original values, written via temp file + atomic replace)
- **Auto-named log** — `--log` without a filename auto-generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory)
- **Unpack mode** — `--unpack` only extracts without converting, outputting to a same-name subdirectory next to each source file (auto-numbered `(2)(3)` if it already exists); mobi uses extract preserving the full structure, cbz uses extractall (with zip-slip path-traversal protection); `.cbz` inputs are also collected when `--unpack` or `--setinfo` is given
- **Elapsed-time stats** — per-file conversion time is printed in real time, and the total elapsed time is shown at the bottom of the summary
- **JSON structured output** — `--json` prints JSON to stdout (a single-line compact JSON in conversion/modify mode, or one slim JSON per file in inspect mode; for AI / pipelines / scripts, suppresses human-readable text); `--json-out [FILE]` writes the structured result to a JSON file (indented format; omitting the filename auto-generates a timestamped file, behaving exactly like `--log`); supported in the conversion mode, the `--setinfo` modification mode, and the `--inspect` inspection mode, and can be used together

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
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi"
```

### Batch-convert an entire directory (recursively searches all .mobi / .azw / .azw3 / .epub)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary"
```

### Delete the original ebook after successful conversion

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --delete
```

### Keep the mobi7 version when a dual-directory mobi is present

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --prefer mobi7
```

### Drop extra images in the directory instead of appending them

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --drop-extra
```

### Force regeneration when a cbz already exists

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --overwrite
```

### Limit per-file conversion timeout (prevents corrupt files from stalling batch jobs)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --timeout 300
```

### Output to a custom directory (preserves relative subdirectory structure by default)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --output-dir "E:\CBZ_Output"
```

### Flatten output (all CBZ files go directly to the output directory root)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --output-dir "E:\CBZ_Output" --flatten
```

### Dry run: only scan and print the conversion flow, without actually converting

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --dry-run
```

> When run against existing CBZ files together with `--setinfo`, it lists the ComicInfo fields that would change per file (`~ field: old -> new`); fields that would only be added are marked with `+`, and unchanged fields are omitted.

### Quiet mode + write output to a log

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --quiet --log convert.log
```

### Compact summary (large directories, success/skip shown as counts only)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --quiet --short-summary --log convert.log
```

### Enable zip compression (can significantly shrink PNG-source manga)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --compress 9
```

### Inspect mode: sample 1 ebook's internal info by default (metadata/structure/images/resolution/DRM/NCX TOC)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --inspect
```

### Inspect all ebooks' internal info

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --inspect all
```

### Override/add ComicInfo fields (repeatable, highest priority)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --setinfo "Title=Sample Series" --setinfo "Number=%number" --setinfo "Summary=Vol. 1, First Edition"
```

> Note: `--setinfo` only splits when a comma is immediately followed by a `fieldname=`. If a value itself contains a `Key=...` structure, pass multiple `--setinfo` options to avoid accidental splitting. When the input directory mixes existing `.cbz` and `.mobi`, enabling `--setinfo` modifies the `.cbz` files' ComicInfo.xml in place (unspecified fields keep their original values), while other files are converted as usual.

### Unpack to view (extract only, no conversion; output to a same-name subdirectory)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --unpack
```

### JSON structured output

```bash
# Print a single-line JSON result to stdout
python manga-mobi2cbz.py "D:\ComicsLibrary" --json

# Write the structured result to a file (indented); omitting the filename auto-generates a timestamped one
python manga-mobi2cbz.py "D:\ComicsLibrary" --json-out inspect_result.json
python manga-mobi2cbz.py "D:\ComicsLibrary" --json-out
```

> Note: `--json` / `--json-out` emit structured results in the conversion, CBZ-modification, inspection, and dry-run modes; they output nothing in `--unpack`. In conversion/modify mode `--json` prints one whole compact JSON; in inspect mode it prints one slim JSON per file (status/series/number/source/page_count/drm; status is one of ok/drm/invalid/noimg/timeout/fail), while `--json-out` writes the full record including spine/toc and a summary; in dry-run mode every record carries the `dry_run: true` flag with status `will_skip` / `pending`. Progress bar and human-readable hints go to stderr, JSON goes to stdout so they are naturally separated; if you merge with `2>&1` the progress bar will pollute the JSON stream, so add `--no-progress` too.

### Show version

```bash
python manga-mobi2cbz.py --version
```

## Parameter reference

| Parameter               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `target`                | Path to an ebook file, a directory containing ebooks (.mobi/.azw/.azw3/.epub), or a glob pattern with `*` / `?` (e.g. `*.epub`, `卷*/001.mobi`); use `.` for the current directory (required)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `--language LANG`       | Output language: `auto` selects by system locale (zh prefix → Chinese, zh-TW/zh-Hant → Traditional Chinese, ja/Japanese → Japanese, otherwise → English), or specify `zh-CN`/`zh-TW`/`ja`/`en` (default `auto`); tolerant of common spellings: `zh`/`cn`→zh-CN, `zhtw`/`tw`→zh-TW, `jp`→ja, `eng`→en                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `--top-only`             | Only process ebook files directly in the target directory (do not recurse into subdirectories) |
| `--delete`              | Delete the original ebook file after successful conversion (default: keep)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `--prefer`              | Which copy to keep for dual-directory mobi: `auto` / `mobi7` / `mobi8` (default `auto`); `auto` prefers mobi8 and falls back to mobi7 when mobi8 has no images; explicitly specifying `mobi7`/`mobi8` falls back to the other when the chosen directory has no images                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `--drop-extra FILTER`   | Generic drop filter (`nargs='?'`): no value = `extra`, dropping all uncollected extra images (equivalent to the old behavior, extra images are appended to the end of the cbz by default); with a value, drops by conditions — format / `res` / `size` / orientation / mode / bit depth / tag (`double` / `thumbnail` / `animated` / `small` / `cover`; `cover` is detected via OPF guide cover + filename keywords) (same expression engine as `--list-images`, comma = OR, `+` = AND, e.g. `--drop-extra gif`, `--drop-extra gif,extra`, `--drop-extra cover`); `off` / `no` / `0` disables; execution order: drop extra images → dedupe → filter → drop small images, combinable with `--drop-small`; dropped file names are listed, only counts under `--short-summary`                                                                                                                                                                                                                                                                                                                                                                                                |
| `--overwrite`           | Force regeneration when the target cbz already exists (default: skip)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `--ext-priority EXTS`   | Which format to keep when files share the same name in the same directory (differing only by extension): comma-separated, order = priority high→low, accepts only mobi/azw/azw3/epub, default azw3; groups not covered fall back to azw3→epub→mobi→azw; unrelated to `--prefer` (dual-directory selection)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `--timeout`             | Per-file conversion timeout in seconds; timeout files are skipped and counted as failed (default 600, `0` = no limit)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `--min-size BYTES`      | Filter out ebooks smaller than the given bytes; default 1000 without a number, `0` disables, not passing it disables size filtering                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `--output-dir DIR`      | Output CBZ to the specified directory (auto-created); preserves the relative subdirectory structure of the input by default (e.g. `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`); add `--flatten` to flatten into the directory root                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `--flatten`             | Only used together with `--output-dir`: flattens all CBZ files into the output directory root; same-name files are skipped (SKIP) unless `--overwrite` is given, which overwrites the preferred name; using it alone (without `--output-dir`) exits with an error                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `--progress`            | Progress bar policy: `auto` shows when stderr is TTY and file count ≥ 2 and `--json`/`--json-out` is not used; `on` forces display; `off` disables (default `off`, not shown); writes to stderr, not into `--log`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `--no-progress`         | Force-disable the progress bar (equivalent to `--progress off`; kept for old-command compatibility)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `--dry-run`             | Dry run: only scan files and print the conversion flow, without unpacking/packing or creating output directories                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `--rename[=TEMPLATE]`   | Rename the output CBZ filename (optional template, off by default): no value = default template (series name + auto-chosen marker prefix by type `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`, connected chapters `話005-006` → `[Ch.5-6]`); the template supports `%series` / `%number` / `%volume` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` and `%03number` zero-padding placeholders; source priority: filename inference > built-in metadata (OPF / ComicInfo.xml) fallback, `--setinfo` not involved; when the input is an existing `.cbz` it enters a standalone rename mode (renames only, no conversion, combinable with other modes); on skip, two hint kinds are distinguished (target exists → suggest `--overwrite`; in-batch collision → suggest adjusting the template), JSON `reason` records `existing` / `conflict`; the dry-run preview colors `[Will Skip]` by collision class (on-disk existing = yellow, in-batch conflict = magenta, TTY + not `--no-color` only), and the summary splits the skip total into "on-disk existing N / in-batch conflict M" with the skipped file list grouped by class; `%description` is not recommended for filenames (content may be too long) — pair it with `%subN_M` to truncate; pair with `--dry-run` to preview first                                                                                                                                                                                                                                                                                                                                                                                                       |
| `--no-color`            | Disable ANSI color output (even when the terminal supports it); logs / JSON / pipes are never colored anyway                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `--quiet`               | Quiet mode: only show errors and the final summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `--debug`               | Debug mode: print debug-level logs to stderr (silent by default, only printed when specified; still printed even when combined with `--quiet`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `--short-summary`       | Compact summary: succeeded/skipped files show counts only (failed files always list full paths)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `--compress LEVEL`      | zip compression level 0-9: `0` = no compression (default, images are already compressed), `1-9` = deflate (benefits PNG sources; higher = smaller but slower)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `--inspect`             | Inspect mode: `sample` randomly inspects 1 ebook (default), `all` inspects every file; a single-file positional argument inspects that file directly; unpack only to read internal info (metadata/structure/images/resolution/dual DRM judgment/NCX TOC), no CBZ produced, temp directory cleaned up automatically; the image preview lists the first 5 files and, when there are more, appends an English ellipsis line `...` (e.g. `... (188 images)`); TOC (NCX) / nav preview truncation is also unified to English `...`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `--inspect-all`         | Inspect all ebooks (equivalent to `--inspect all`; kept for old-command compatibility)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `--no-comicinfo`        | Do not generate ComicInfo.xml (default: generates it into the CBZ root with Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary metadata)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `--setinfo FIELD=VALUE` | Override/add ComicInfo fields (repeatable, highest priority): `FIELD` is a ComicInfo field name and must be in the standard-field whitelist (out-of-whitelist fields emit a warning and are ignored); `VALUE` supports fixed values / `%series` / `%number` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` placeholders (`%subN_M` = M chars from the Nth char, 1-based; field omitted only when the whole value is exactly one known placeholder and its value is missing); placeholders may be mixed with fixed text (e.g. `%writer·重制`, `第%number话`), in which case a missing value renders as an empty string; smart splitting: only splits when a comma is followed by `fieldname=`, otherwise the comma is part of the value (e.g. `Summary=Vol. 1, First Edition` is not split); for existing `.cbz` inputs, `%series`/`%number`/`%volume` read the explicit Series/Number/Volume from ComicInfo first, falling back to filename inference only when absent; when the input is an existing `.cbz`, its ComicInfo.xml is modified in place (unspecified fields keep their original values); use multiple `--setinfo` when a value contains `Key=`; when enabled, `.cbz` files mixed into the input are modified in place while other files convert as usual; `Manga` is not written by default — specify it explicitly with `--setinfo Manga=Unknown\|No\|Yes\|YesAndRightToLeft` (official v2.0 enum only); `CommunityRating` (0-5) / `MainCharacterOrTeam` / `Review` are also supported |
| `--unpack`              | Unpack to view: extract only, no conversion; outputs to a same-name subdirectory next to each source file (auto-numbered `(2)(3)` if it already exists); mobi uses extract preserving the full structure, cbz uses extractall (with zip-slip path-traversal protection); `.cbz` inputs are also collected                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `--double-page VALUE`   | Double-page spread detection: omitted or `auto` enables it (threshold 2.0; detects wide banner spread images with width/height ≥ threshold, writing per-page `Type="DoublePage"` to ComicInfo; `Manga` is no longer declared automatically); a numeric value (e.g. `2.5`) enables it and adjusts the threshold; `off` / `no` / `0` disables it; invalid values error out                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `--drop-small [VALUE]`  | Drop small images: exclude images clearly smaller than the rest during conversion (cover thumbnails / copyright pages, etc.) — an image is dropped when both its width and height are < median × ratio; omitted or `auto` uses the default ratio 0.5, a `0~1` number (e.g. `0.4`) adjusts it, `off` / `no` / `0` disables (disabled by default, existing behavior unchanged); ComicInfo `PageCount` is recomputed from the remaining images; summary / `--log` / `--json` report a "dropped small" count (`--json` emits a `dropped_small` field) and list the dropped file names one by one (only counts under `--short-summary`); `--inspect` preview shows "N image(s) will be dropped when --drop-small is enabled"; wide double-page banners (width not small) are never mis-dropped; conversion mode only                                                                                                                                                                                                                                                                   |
| `--list-images [FILTER]` | Read-only image listing: no value = list all images of the target ebook; with a value = FILTER expression (format / `res` / `size` / orientation / mode / bit depth / tag; comma = OR, `+` = AND, `-` prefix excludes, e.g. `jpeg,size>1MB`, `-webp`); read-only scan — no conversion, no CBZ, no ComicInfo, no files written; CBZ read directly from zip (no TOC column / no conversion-state tags); per-file block (No. / filename / resolution / size / mode·depth / orientation / TOC / tag) + full statistics block (always full-set, unaffected by the filter); works with `--json` (one slim JSON per file) and `--quiet` (detail suppressed, count only); independent from `--inspect` |
| `--log FILE`            | Append all output to the specified log file; without a filename, auto-generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `--json`                | Print JSON of the run result to stdout (for AI / pipelines / scripts); suppresses human-readable text output when enabled; one whole compact JSON in conversion/modify mode, or one slim JSON per file in inspect mode (status/series/number/source/page_count/drm); in dry-run mode it emits records carrying the `dry_run` flag (status `will_skip` / `pending`), nothing in unpack mode; can be combined with `--json-out`; progress bar goes to stderr and stays separate, but 2>&1 combined redirection mixes it in                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `--json-out [FILE]`     | Write the structured run result to a JSON file (indented format); without a filename, auto-generates a timestamped file (current directory, behaves exactly like `--log`); can be combined with `--json`; file-level results in conversion/modify mode, full record (incl. spine/toc and summary) in inspect mode                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `--version`             | Show version number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

## Output

- By default, the converted `.cbz` file is placed in the same directory as the original ebook; with `--output-dir`, it goes to that directory (auto-created), preserving the relative subdirectory structure of the input, or flattened into the directory root with `--flatten` (same-name files are skipped unless `--overwrite` is given)
- Existing `.cbz` files are skipped by default and never overwritten; use `--overwrite` to force regeneration
- 0-byte / corrupt-header ebooks are skipped at the precheck stage, with the full path and reason logged
- Per-file conversion time is printed in real time; total elapsed time is shown at the bottom of the summary
- Failed files print an error message and do not block conversion of other files

## JSON output contract

In the structured output of `--json` / `--json-out`, the `status` field is the machine-consumed contract. Values per mode:

| Mode | `status` values | Failure detail |
|---|---|---|
| Conversion (default) | `ok` / `skip` / `fail` / `timeout` | failure reason in the `reason` field: `drm` / `corrupt` / `verify` / `comicinfo` / `other` |
| Inspection (`--inspect`) | `ok` / `drm` / `invalid` / `noimg` / `timeout` / `fail` | `--json` prints one slim JSON per file; `--json-out` writes the full record (incl. spine/toc and summary) |
| Modification (`--setinfo`) | `modified` / `nochange` / `fail` | failure reason in the `reason` field |
| Dry-run (`--dry-run`) | `will_skip` / `pending` | every record carries `dry_run: true` so machines can distinguish it from a real run |

Every record has the fixed fields `source` / `status` / `target` / `reason` / `elapsed_sec`; conversion mode additionally carries `series_source` / `number_source` / `cover_source` / `dropped_small`.

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
A: Since v1.9.0, `--output-dir` preserves the relative subdirectory structure of the input by default (a breaking change from the old flat behavior). Add `--flatten` to flatten instead; change the old command `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output` to `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output --flatten` to restore the old flat behavior.

**Q: Are .azw / .azw3 supported?**
A: Yes. Since v1.8.0 the accepted input extensions are `.mobi` / `.azw` / `.azw3`, all three going through the same conversion pipeline; for same-name files with different extensions in the same directory, azw3 is kept by default, adjustable via `--ext-priority`.

**Q: Are EPUB files supported?**
A: Yes. Since v2.4.0 the accepted input extensions are `.mobi` / `.azw` / `.azw3` / `.epub`. EPUB is a ZIP container, so it is safely unpacked via zipfile and reuses the OPF spine extraction pipeline; cover detection supports both EPUB2 (`<meta name="cover">`) and EPUB3 (`properties="cover-image"`); without an EXTH header, metadata is read from OPF `dc:` fields; `--prefer` is silently ignored for EPUB. Encrypted EPUBs (e.g. Adobe DRM) cannot be parsed — they are reported as no images / no usable metadata and skipped; remove the DRM before converting.

## Changelog

### [3.0.0] - 2026-08-24
#### Breaking changes

- **License switched to GPL-3.0-only** — because this tool depends at runtime on the mobi library (GPL-3.0-only), public distribution of this project constitutes distribution, so the license changed from MIT to GPL-3.0-only; LICENSE is replaced with GNU GPL v3 and the License section of this README was updated accordingly
- **Progress bar off by default** — no longer auto-shown; enable explicitly with `--progress on` / `--progress auto`; unified to `--progress auto|on|off` (omitted or `off` = hidden; `auto` = shown on TTY with ≥ 2 files and when `--json`/`--json-out` are not used); legacy `--no-progress` kept as a hidden alias
- **`--inspect` argument collapsed** — `--inspect [sample|all]` (default `sample` = old random check of 1, `all` = old `--inspect-all`); the old black-box behavior where `--inspect-all` alone auto-enabled `--inspect` is removed, you must pass `--inspect all` explicitly; `--inspect-all` kept as a hidden alias

#### New features

- **Glob patterns for `target`** — `target` accepts patterns containing `*` / `?` (e.g. `*.epub`, `卷*/001.mobi`); when multiple files match they are filtered by extension and processed as a flat file list; use `.` to process the current directory
- **`--top-only`** — Only process ebook files directly in the target directory (do not recurse into subdirectories)
- **New `%subN_M` placeholder for `--setinfo`** — take M chars starting from the Nth char (1-based) of the filename, e.g. `[Anon][Demo Series]話005-006` with `--setinfo "Series=%sub8_11"` yields `Demo Series`; the field is omitted when out of range
- **JSON output for `--inspect`** — `--json` prints one slim JSON per file (`status` / `series` / `number` / `source` / `page_count` / `drm`; `status` ∈ `ok` / `drm` / `invalid` / `noimg` / `timeout` / `fail`); `--json-out` writes the full record (incl. `spine` / `toc` and summary); `inspect_ebook` refactored to return a structured `(InspectStatus, info dict)` tuple
- **Field-level dry-run preview with `--setinfo`** — lists the ComicInfo fields that would change per file (`~ field: old → new`; new-only fields marked `+`; unchanged fields omitted), without writing
- **Resolution summary for `--inspect`** — a resolution distribution summary is printed at the end of the sample/full scan: dominant `WxH` with count & percentage, plus the number of abnormal small images (same threshold as `--drop-small`: both width and height < median × 0.5)
- **`--debug` debug logging** — new `--debug` flag + emit debug level: debug-level logs are printed to stderr only when `--debug` is given (silent by default); they are still printed even when combined with `--quiet`; help.debug in all four languages
- **`--inspect` spam reduction** — per-file progress lines in inspect mode demoted to info level, so `--quiet` can suppress the flood; zero new flags
- **Disk space precheck** — new `estimate_expanded_size` + `check_disk_space`: the main loop prechecks each file's expanded-size requirement; when space is insufficient a `warn.disk_space` hint is printed but processing continues (batch not blocked; all four languages)
- **Temp-dir cleanup failure hint** — three `rmtree(ignore_errors=True)` calls changed to try/except with `warn.cleanup_tmp_fail`; cleanup failures are no longer silently swallowed (all four languages)
- **Symmetric output for `--drop-extra` / `--drop-small`** — both now list the affected file names one by one (`--drop-extra` lists the extra images dropped, `--drop-small` lists the dropped small images); with `--short-summary` only the counts are shown without paths, consistent with the succeeded/skipped summary
- **`--rename` output renaming** — renames the output CBZ filename (optional template, off by default): no value = default template (series name + auto-chosen marker prefix by type `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`, connected chapters `話005-006` → `[Ch.5-6]`); the template supports `%series` / `%number` / `%volume` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` and `%03number` zero-padding placeholders; source priority: filename inference > built-in metadata (OPF / ComicInfo.xml) fallback, `--setinfo` not involved; when the input is an existing `.cbz` it enters a standalone rename mode (renames only, no conversion, combinable with other modes); `%description` is not recommended for filenames (content may be too long) — pair it with `%subN_M` to truncate; pair with `--dry-run` to preview first
- **`--no-color` color control** — disables ANSI color output (even when the terminal supports it); logs / JSON / pipes are never colored anyway
- **Classified rename-skip hints** — when `--rename` skips a file, two hint kinds are distinguished: target already exists on disk (`skip_existing`, suggest `--overwrite`) vs. collision within the current batch (`skip_conflict`, suggest adjusting the naming template); both dry-run and non-dry-run paths apply, and the JSON `reason` field records `existing` / `conflict` respectively
- **New `--list-images [FILTER]` read-only image listing** — lists every image of the target ebook (No. / filename / resolution / size / mode·depth / orientation / TOC / tag) plus a full statistics block (format / mode·depth / size distribution / double-page banners / animated GIFs / small images / abnormal-image detail); no conversion, no CBZ, no ComicInfo, no files written; fully independent of `--inspect`. No value = list everything; with a value = FILTER expression (format / `res` / `size` / orientation / mode / bit depth / tag keywords; comma = OR, `+` = AND, `-` prefix excludes, e.g. `jpeg,size>1MB`, `-webp`); the filter affects only the listing rows while statistics stay full-set; CBZ is read directly from the zip without unpacking (no TOC column / no conversion-state tags); works with `--json` (one slim JSON per file) and `--quiet` (detail suppressed, count only)
- **`--drop-extra` upgraded to a generic drop filter** — changed from a boolean to `nargs='?'`: no value = `extra` (drop all uncollected extra images, same as the old behavior); with a value, drop by conditions (format / `res` / `size` / orientation / mode / bit depth / tag keywords, same expression engine as `--list-images`, comma = OR, `+` = AND, e.g. `--drop-extra gif`, `--drop-extra gif,extra`); `off` / `no` / `0` disables; execution order: drop extra images → dedupe → condition filter → drop small images, combinable with `--drop-small`
- **`--inspect` ellipsis unified to English `...`** — the image preview lists the first 5 files and appends an ellipsis line when there are more (e.g. `... (N images)`); TOC (NCX) / nav preview truncation unified to English `...` (replacing the previous Unicode `…`)
- **Classified skip preview coloring & grouped summary** — in `--rename` dry-run preview, `[Will Skip]` is colored by collision class (on-disk existing target = yellow, in-batch collision = magenta; TTY + not `--no-color` only); the non-dry-run summary splits the skip total into "on-disk existing N / in-batch conflict M" and lists the skipped files grouped by class (each with its own header); JSON `reason` stays `existing` / `conflict`, `skipped` count semantics unchanged (sum of both groups + nochange)

#### Fixes

- **NCX lookup miss** — Added unified `find_ncx` lookup (first by OPF manifest `media-type=application/x-dtbncx+xml`, then by the id referenced by the spine `toc` attribute, finally falling back to `*.ncx`), compatible with packages that name the NCX `xml/vol.nav` instead of using a `.ncx` extension; `parse_ncx_toc` / `parse_ncx_entries` now use it
- **`--inspect` TOC (NCX) count scope** — Count only `<navLabel><text>` entries (previously docTitle/docAuthor were counted too, inflating the entry count by 1-2)
- **`--rename` `%title%` placeholder now falls back to OPF `dc:title`** — previously `%title%` only read ComicInfo.xml `<Title>`, so an epub without a ComicInfo always yielded an empty value; now OPF `dc:title` is read as a fallback; source priority: OPF `dc:title` → ComicInfo.xml `<Title>` (consistent with the series/number OPF fallback)
- **New `%writer` / `%publisher` / `%date` / `%language` / `%description` placeholders for `--rename` / `--setinfo`** — OPF reads `dc:creator` / `dc:publisher` / `dc:date` / `dc:language` (normalized) / `dc:description`, ComicInfo reads `<Writer>` / `<Publisher>` / `<LanguageISO>` / `<Summary>`; `%date` keeps the raw date string (e.g. `2024-01-15`; ComicInfo has no counterpart); OPF takes priority over ComicInfo
- **DRM false-positive fix** — `get_drm_flag` previously read 2 bytes at PalmDB header offset 12 (which landed in the name field, so ebooks whose filenames contain `-`/`_`, e.g. the [Anon] series, were misjudged as encrypted); it now reads the copy-protection bit at attributes offset 32 plus the PalmDOC header encryption type (offset 78 + 8×nrec + 0x0E) as the authoritative criterion
- **`--inspect` no longer skips unpacking on a DRM marker** — the DRM marker is demoted to an informational flag; unpacking is still attempted: images extracted → `status=ok` with a `drm` marker; it is classified as DRM only when unpacking fails and the image count is 0
- **`--drop-extra cover` atomic no-op fix** — covers are now tagged via OPF guide + COVER_KEYWORDS on both the list and conversion paths, so `--drop-extra cover` reliably drops the cover
- **Mixed `--setinfo` placeholders with fixed text** — a value may mix placeholders and literal text (e.g. `%writer·remaster`, `第%number话`), with the same global replacement as `--rename`: missing values render as empty, unknown placeholders are kept verbatim; when the whole value is exactly a single known placeholder, the original semantics are preserved (the field is not written when missing)
- **NCX / NAV TOC parse order and entity decoding** — `parse_ncx_entries` now builds the tree with a stack and walks it in document order (parents always precede children; siblings keep document order), stripping nested tags from titles and decoding HTML entities (`&amp;` → `&`); `parse_nav_entries` gains the same entity decoding

#### Security

- **XXE injection protection (P0)** — all `ET.parse` calls replaced with `safe_et_parse` (7 call sites); only `<!ENTITY` entity declarations are blocked (bare DOCTYPE is allowed through); string paths only reject `..` traversal (a `./` prefix and plain relative paths are allowed, so unpacked OPF/NCX references keep working)

#### Fixed / Maintenance

- **Timeout residue hint on conversion path** — `run.timeout_residue` added (previously only on the inspect path)
- **Volume inference fix** — 4-digit years (`19xx` / `20xx`) no longer mis-detected as volume numbers (e.g. `Series 2024`)
- **Volume/chapter inference enhancement (Kavita-aligned)** — new chapter-family keyword list (話 / 话 / 話数 / 话数 / Chapter / Ch. / ch / chp / c / Episode / 화 / 회 / 回 / 集 / บทที่ / ตอนที่ / Глава); supports run-together forms (`c001` / `ch001` / `v01` / `T3` / `S01`), volume+chapter co-occurrence (`Vol.0001 Ch.0001`, `Том 1 Глава 3`), volume/chapter ranges (`v16-17`, `c001-006` → first value), decimals (`025.5`), trailing-b half chapters (`153b` → 153.5), extra multi-language volume forms (`冊N` / `1권` / `장N` / `季N` / `第N季`), and parentheses/bracket annotation stripping; fixes the old defects of English markers being swallowed into the series name and ranges taking the last value
- **Magic numbers promoted to named constants** — `HEAD_READ_BYTES = 65536`, `DEFAULT_TIMEOUT = 600`
- **Error status strings consolidated into enums** — `ConvStatus` / `InspectStatus`
- **Dead code cleanup** — `used_names` dead parameter on the real run path, `target_cbz_path` dead formal parameter, `sys.argv` scanning removed
- **Maintenance** — matching-semantics comments for `_VOLUME_PATTERNS`; stray comment relocated
- **ComicInfo error differentiation** — build and write failures now use separate messages (`comicinfo.build_fail` / `comicinfo.write_fail`), making the cause clearer
- **`validate_cbz` doc hygiene** — EOCD read strategy, ComicInfo triple-check and return semantics documented (no behavior change)
- **Type annotation completion** — return-type annotations such as `_main() -> None` added
- **`natural_key` fallback for very long numbers** — overlong all-digit strings (beyond the Python int digit limit) no longer break sorting; they fall back to string comparison
- **`extract_epub_to_temp` self-healing on failure** — if unpacking fails midway, the just-created `mkdtemp` directory is cleaned up before the exception is re-raised, avoiding directory leaks
- **`ZIP_EOCD_READ_TAIL` named constant** — the tail byte count `validate_cbz` reads for the EOCD is promoted to a named constant (70000, far larger than the maximum size of a single EOCD record)
- **Per-directory disk-precheck cache** — `check_disk_space` caches free disk space per directory (`_disk_free`), avoiding repeated syscalls when batching many files
- **PageCount removed from the ComicInfo `--setinfo` whitelist** — `PageCount` can no longer be overridden via `--setinfo`; it is always derived from the actual number of images written (whitelist 42 → 41)
- **HTML entity decoding (P1-3)** — `extract_images_from_html` now applies `html.unescape` to src values on the regex path (previously only the HtmlImgParser fallback path decoded entities, so entity-encoded srcs like `&amp;` in malformed HTML leaked through)
- **Startup warning for leftover `.cbz.tmp`** — on startup the script scans output-side directories for half-finished `*.cbz.tmp` from a previous interrupted/killed/power-loss run and emits a warning if found (warn only, never auto-deletes — data-safe); complements the atomic-write `finally` cleanup into a complete safety chain
- **JSON status contract documented** — see the "JSON output contract" section below; the `status` enum for all three modes is now explicit so machine consumers do not have to guess
- **Docs & comment fixes** — the outdated `--double-page` comment ("writes Manga>Yes") now reads "DoublePage only; Manga via --setinfo"; the top usage line gains `--json` / `--json-out` / `--double-page` / `--drop-small` / `--debug`; the `dedupe_ebook_files` docstring fallback order now includes epub; a misplaced outdated signature comment was removed
- **ComicInfo source label localization** — the `--inspect` preview block now renders the Series/Number source annotation (`setinfo` / `opf` / `inferred`) through i18n so it follows the UI language (e.g. `[filename inferred]` under zh-CN); the `series_source` / `number_source` fields in `--json` stay machine-readable English as before; the single `comicinfo.inferred` key is refactored into `comicinfo.src.setinfo` / `comicinfo.src.opf` / `comicinfo.src.inferred` across all four languages
- **dry-run JSON output fixed** — `--dry-run` combined with `--json` / `--json-out` now emits structured JSON (the contract was previously missing and docs claimed no output): each record carries a `dry_run` boolean flag to distinguish a trial run from a real one, with dry-run status values `will_skip` / `pending`; the "JSON output contract" section and the argument descriptions that said "dry-run does not output" are updated accordingly
- **SPDX header added** — `SPDX-License-Identifier: GPL-3.0-only` added to the script header

#### Review fixes (follow-up batch)

- **GIF frame-count false positive fixed (P0)** — `gif_frame_count` no longer scans LZW compressed data with `head.count(b"\x2c")`; it now parses GIF structure blocks (counting only image descriptors `0x2C` and skipping LZW data by sub-block boundaries without reading contents), so stray `0x2C` bytes inside a static GIF's compressed data no longer mis-flag it as `animated`; a truncated header exits safely
- **zip-slip drive / UNC escape protection (P0)** — `_safe_zip_extract` now also checks `Path.is_absolute()`, rejecting drive-letter (`C:/...`) and UNC (`//server/share`) absolute-path entries that could write outside `out_dir` (previously only `/`-prefixed and `..` segments were blocked)
- **`validate_cbz` tail seek (P1)** — files > 70KB are now seeked to read only the trailing `ZIP_EOCD_READ_TAIL` (70000) bytes instead of reading the whole file then slicing; peak memory for validating large CBZs drops from O(file size) to O(70KB)
- **`build_cbz_image_attrs` streaming header read (P1)** — switched to `zf.open().read(HEAD_READ_BYTES)` (lazy decompression) instead of `zf.read(name)` (whole-image decompress then slice), reducing decompression work and memory for large image entries
- **`_fill_small_mark` magic-number cleanup (P2)** — the hard-coded `0.5` is replaced with the constant `DEFAULT_DROP_SMALL_RATIO`; semantics and behavior are unchanged

### [2.5.1] - 2026-08-20

#### Fixed

- **Deduplication no longer drops same-name `.cbz`** — in `--setinfo` / `--inspect` / `--unpack` modes, converted `.cbz` files no longer join same-name deduplication with mobi/azw/azw3/epub, so existing CBZ can be modified / checked normally
- **Dedicated hint for flatten name conflicts** — when a second same-name source is skipped under flatten mode, it now clearly flags a flatten conflict instead of the generic "target already exists", and suggests `--overwrite`

### [2.5.0] - 2026-08-20

#### Changed

- **`Manga` no longer written automatically** — double-page detection (`--double-page`) only emits `<Pages>` per-page `Type="DoublePage"` markers and no longer appends a `<Manga>Yes</Manga>` declaration (readers like Mihon do not read that field, and it avoids declaring Manga even without spreads); `Manga` is now set explicitly via `--setinfo Manga=Unknown|No|Yes|YesAndRightToLeft`, limited to the official v2.0 enum; invalid values emit a warning and are ignored
- **`--ext-priority` supports EPUB** — accepts `mobi` / `azw` / `azw3` / `epub`; the fallback order when priority does not cover a group is now `azw3 → epub → mobi → azw` (EPUB is kept over the mobi family)
- **No-image hint split by extension** — EPUB with no images now gets a neutral hint (confirm it contains comic images and is not encrypted) instead of a false Kindle DRM warning; mobi/azw/azw3 still hint at possible DRM

#### Added

- **`--setinfo` whitelist extended (39 → 42)** — three more official ComicInfo v2.0 fields: `CommunityRating` (0-5 rating) / `MainCharacterOrTeam` / `Review`
- **`--drop-small` drops small images** — disabled by default; when enabled, images clearly smaller than the rest are excluded during conversion (cover thumbnails / copyright pages, etc.): an image is dropped when both its width and height are < median × ratio (default ratio 0.5, adjustable with a `0~1` value, `off`/`no`/`0` disables); reads PNG/JPEG header dimensions per image with no new dependencies; ComicInfo `PageCount` is recomputed from the remaining images; the summary / `--log` / `--json` report a "dropped small" count (`--json` emits `dropped_small`); `--inspect` preview warns "N image(s) will be dropped when --drop-small is enabled"; wide double-page banners (width not small) are never mis-dropped

#### Docs

- **`--help` synced in four languages** — `help.description` / `help.target` / `help.ext_priority` now mention `.epub`; `help.setinfo` documents the Manga enum and explicit specification
- **Encrypted EPUB note** — the FAQ clarifies that encrypted EPUBs (e.g. Adobe DRM) cannot be converted; remove DRM first

### [2.4.0] - 2026-08-20

#### Added

- **EPUB input support** — accepted input extensions expanded to `.mobi` / `.azw` / `.azw3` / `.epub`; `ebook_to_cbz` / `--inspect` / `--unpack` branch by extension: EPUB (a ZIP container) is safely unpacked via zipfile (with zip-slip path-traversal protection), while mobi/azw/azw3 still go through `mobi.extract`; the existing OPF spine extraction and ComicInfo metadata pipeline is reused, with no parallel implementations
- **EPUB cover fallback enhanced** — `get_opf_guide_cover_href` now checks three sources in order: ① guide `type="cover"` ② manifest `properties="cover-image"` (EPUB3) ③ the item referenced by `<meta name="cover">` (EPUB2); cover href resolution corrected to be relative to the OPF directory (EPUB OPFs usually live in OEBPS/)
- **EPUB metadata supplement** — without an EXTH header, `--inspect` reads title/author/language/date/publisher from OPF `dc:` fields instead; `get_drm_flag` passes EPUB through directly (a ZIP container has no PalmDB DRM field, avoiding false positives)
- **`--prefer` silently ignored for EPUB** — EPUB has no mobi7/mobi8 dual directories and is naturally single-directory
- **EPUB3 nav TOC recognition** — `--inspect` locates the nav document via OPF manifest `properties="nav"` (fallback: `*nav*.xhtml`), parses `<a>` titles inside `<nav epub:type="toc">` (nested levels included); shown alongside the EPUB2 `toc.ncx`, so a pure EPUB3 without .ncx still gets a TOC
- **ComicInfo series/number read from metadata first** — when generating ComicInfo, Series/Number are now taken from OPF metadata first (`dc:series` / `dc:number`, EPUB3 `belongs-to-collection` / `group-position`, calibre's `meta[name=calibre:series/series_index]`); `dc:number` is auto-stripped of volume markers (`卷12` → `12`), and only falls back to filename inference when no OPF metadata exists
- **Double-page detection (`--double-page`)** — on by default (threshold 2.0): detects wide banner spread images whose width/height ≥ threshold, and writes `<Manga>Yes</Manga>` top-level tag + per-page `Type="DoublePage"` into ComicInfo; `--double-page auto` equals the default, `--double-page 2.5` adjusts the threshold, `--double-page off` (or `no` / `0`) disables it, and invalid values error out
- **ComicInfo field source annotation** — the `--inspect` preview annotates Series/Number with their source (`[setinfo]` / `[opf]` / `[inferred]`), so you can tell at a glance whether a field came from user specification, OPF metadata, or filename inference; `--json` also gains `series_source` / `number_source` / `cover_source` fields (values such as `setinfo` / `opf` / `inferred` / `filename`) for AI/pipeline trust assessment

#### Changed

- **Unified safe extraction for `--unpack`** — CBZ and EPUB share `_safe_zip_extract` (zip-slip protection), simplifying the logic
- **Streaming rewrite for `--setinfo` CBZ modification** — `modify_cbz_comicinfo` no longer loads the whole archive into memory; it copies entries with dual handles (1MB chunks) and only reads `ComicInfo.xml` into memory; per-entry compression method / timestamps / attributes are preserved, and atomic replacement with exception cleanup is unchanged (memory for large archives drops from O(whole archive) to O(single entry))
- **ComicInfo priority reordered (setinfo > OPF metadata > filename inference)** — previously Series/Number came straight from filename inference (`infer_series_number`); now user-specified `--setinfo` wins, then OPF metadata, and filename inference is only the last resort; files with a bare volume marker and no series name (e.g. `Vol.01.mobi`) now return the number only, not a fake series name
- **Volume-inference regex expanded** — `infer_series_number` now covers: `卷N` prefix style, `vN`, `第N册`/`N册`, `巻N` prefix style, French `tome N`, Korean `권N`, Thai `เล่ม N`, Russian `Том N`, Chinese-numeral volumes (`第一卷`/`卷二`), and fractional volumes (`Vol 7.5`)
- **CoverSource removed from Notes** — cover source is no longer written into the `Notes` field of ComicInfo (avoiding non-standard notes leaking into the cross-software shared ComicInfo.xml); it is now surfaced via the `--inspect` cover line and the `--json` `cover_source` field, and Notes keeps content fields only

### [2.3.1] - 2026-08-19

#### Fixed

- **Hardened atomic replacement in the conversion branch** — the temp file is validated with validate_cbz before `os.replace` overwrites the target; on failure only the tmp is cleaned and the old CBZ is kept; a ComicInfo generation failure no longer deletes an existing target CBZ; Ctrl+C (KeyboardInterrupt) leftover `.tmp` files are cleaned up by a finally block
- **Unknown `--setinfo` placeholder warning** — out-of-whitelist placeholders emit a warning and are written as-is (new i18n keys in all four languages)
- **sanitize extended** — ASCII control characters stripped, trailing dots/spaces removed
- **find_opf naming priority** — `content.opf` / `package.opf` preferred when multiple OPFs exist
- **Maintenance** — stale docstrings cleaned; `_strip_html` switched to HTMLParser (dead `import html` removed)

#### Docs

- **`--help` wording extended (zh-CN/zh-TW/en/ja)** — `--setinfo`: use multiple options when a value contains `Key=`, existing `.cbz` inputs are modified in place when enabled; `--json`/`--json-out`: only emitted in conversion/modify mode (nothing in dry-run/inspect/unpack), progress bar goes to stderr and stays separate, but 2>&1 combined redirection mixes it in
- **README usage notes synchronized** — setinfo / JSON sections and the parameter table updated accordingly

### [2.3.0] - 2026-08-19

#### Added

- **JSON structured output** — `--json` prints a single-line compact JSON to stdout (for AI / pipelines / scripts; suppresses human-readable text output when enabled); `--json-out [FILE]` writes the structured result to a JSON file (indented format; omitting the filename auto-generates a timestamped file, behaving exactly like `--log`); the two can be combined; supported by both the conversion mode and the `--setinfo` modification mode

#### Fixed (merged from the v2.2.1 interim fixes)

- **Atomic replacement in the conversion path** — CBZ packaging now writes to a `xxx.cbz.tmp` temp file first and only `os.replace`s it over the target after everything succeeds; removed the unlink of the old CBZ before packaging and the deletion in failure branches, so only the half-written tmp is cleaned on exception. Eliminates the risk of a truncated CBZ left behind by Ctrl+C / mid-run crash, and the data-loss risk of losing the old file when overwrite fails (consistent with the existing atomic replacement in CBZ modification mode)
- **`--inspect` non-numeric PageCount warning** — a non-numeric PageCount in ComicInfo now emits a warning instead of being silently ignored (new i18n key `inspect.pagecount_non_numeric`, synced across all four languages)
- **`--timeout` help text** — now notes that the underlying unpack thread may linger in the background after a timeout; the `--overwrite` message now reads "old file will be replaced", matching the actual atomic-replacement behavior

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
- **`--setinfo FIELD=VALUE`** — override/add ComicInfo fields (repeatable, highest priority); VALUE supports fixed values / `%series` / `%number` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M`; smart splitting (only splits when a comma is followed by `fieldname=`); CBZ modification mode rewrites the zip directly; the `--inspect` preview block applies it too
- **ComicInfo written in the same zip pass** — removed the `write_comicinfo` function; `zf.writestr` inside the Step4 `with` block
- **`--log` auto-naming** — `nargs="?"` + `const="auto"`; auto generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory)
- **`--unpack` unpack-to-view** — extract only, no conversion; mobi uses extract preserving the full structure, cbz uses extractall; defaults to a same-name directory, auto-numbered `(2)(3)` if it already exists

### [2.0.2] - 2026-08-17

#### Changed

- `infer_series_number` now supports parenthesized suffixes: a `(author)` suffix no longer blocks volume inference (e.g. `Sample Series - Vol. 23 (Sample Author)` correctly infers Series=Sample Series / Number=23)
- Pure volume markers (`Vol.01` / `第 01 卷` / `01巻` etc.) now return only the volume number `(None, number)` instead of `(None, None)`, so ComicInfo can write Number
- `--flatten` same-name handling changed to SKIP/`--overwrite`: same-name files in the flat output root are no longer auto-renamed and re-converted as `(2).cbz`; without `--overwrite` they are skipped (SKIP), with it the preferred name is overwritten; dry-run stays consistent with the real run
- Removed the now-unused `unique_path` function

#### Fixed

- Fixed PageCount consistency: physical dedup now happens before ComicInfo generation; both PageCount and packaging use the deduplicated actual written count
- Fixed `run_with_timeout` cross-version: except now catches both built-in `TimeoutError` and `concurrent.futures.TimeoutError` (Python 3.10 compatible)
- Fixed `infer_series_number` dot failure: now uses `path.name` with manual extension removal, so dotted volume numbers like `Sample Series Vol.01` infer correctly
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

- `--output-dir DIR` changed from "flatten everything into DIR" to "**preserve the relative subdirectory structure of the input by default**" (e.g. `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`)
- Migration: the old command `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output` must be changed to `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output --flatten` to restore the "flatten" behavior

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

This project is licensed under the [GPL-3.0](./LICENSE).

### Third-party dependency license

This tool depends at runtime on the mobi library (v0.4.1, maintained by Titusz Pan), which is licensed under GPL-3.0-only. Please comply with GPL-3.0 requirements when distributing.
