**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md)

# manga-mobi2cbz

A batch-conversion CLI tool built for Kindle manga: convert DRM-free MOBI / AZW / AZW3 / EPUB ebooks into standard CBZ comic packages with one command.
It natively follows the OPF spine reading order to extract images, and comes with a full set of practical capabilities: automatic cover repair, same-volume multi-format deduplication, batch timeout protection, file integrity verification, and multi-language auto output. It also includes an `--inspect` exploration mode that lets you inspect comic metadata, resolution, NCX table of contents, and DRM status without packing. Cross-platform, efficient and stable for batch organizing your manga library.

> ⚠️ Only supports DRM-free Kindle comics. Store-purchased DRM-protected eBooks cannot be parsed.
> 
> **Project Origin**: Created to handle manga formats — each conversion was handled with AI-generated scripts, and the project was uploaded to GitHub for easy reuse and to avoid losing the scripts.
> Later, issues such as page-order errors, missing covers, and batch interruptions were encountered; through repeated iteration the project gradually evolved into its current form. The code is entirely AI-generated — feel free to use it, and feedback is welcome if you find any problems.

## Features

- **Batch conversion** — convert a single file or an entire directory recursively (`.mobi` / `.azw` / `.azw3` / `.epub`)
- **OPF spine ordering** — extract images in OPF spine order to preserve the real reading order; falls back to natural filename sorting when no OPF exists
- **Cover fallback** — automatically scans for images whose filenames contain cover/front; if the cover is already in the spine list, the list order wins, and it is only inserted at the front when missing
- **Directory alignment fallback** — when the image count in the directory differs from the collected count, extra images are appended to the end of the cbz in natural order by default; `--drop` switches to dropping them instead, and the extra image file names are listed one by one (only counts under `--short-summary`)
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
- **Output renaming** — `--rename[=TEMPLATE]` renames the output CBZ filename (optional template, off by default): no value = default template (series name + auto-chosen marker prefix by type `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`, connected chapters `話005-006` → `[Ch.5-6]`); the template supports `%series` / `%number` / `%volume` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` and `%03number` zero-padding placeholders; source priority: filename inference > built-in metadata (OPF / ComicInfo.xml) fallback, `--setinfo` not involved; when the input is an existing `.cbz` it enters a standalone rename mode (renames only, no conversion, combinable with other modes); `%description` is not recommended for filenames (content may be too long) — pair it with `%subN_M` to truncate; pair with `--dry-run` to preview first
- **Color control** — `--no-color` disables ANSI color output (even when the terminal supports it); logs / JSON / pipes are never colored anyway
- **Classified rename-skip hints** — when `--rename` skips a file, two hint kinds are distinguished: target already exists on disk (suggest `--overwrite`) vs. collision within the current batch (suggest adjusting the naming template); both dry-run and non-dry-run paths apply, and the JSON `reason` field records `existing` / `conflict` respectively; the dry-run preview colors `[Will Skip]` by collision class (on-disk existing = yellow, in-batch conflict = magenta; TTY + not `--no-color` only), and the non-dry-run summary splits the skip total into "on-disk existing N / in-batch conflict M" with the skipped file list grouped by class
- **Resume support** — if the target CBZ already exists and passes integrity verification, it is skipped (SKIP); corrupt/invalid output is automatically reconverted; when the source file is newer than the target CBZ it is automatically reconverted too; `--overwrite` unconditionally overwrites
- **Failure classification** — conversion failures are counted by reason (`timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other`), with per-category counts shown in the summary
- **Inspect supports CBZ** — `--inspect` can inspect `.cbz` files directly (pure zipfile reading, no unpacking); cover line gains resolution+size, format stats gain total file count, and each of the first 5 Spine entries gains width/height
- **Read-only image listing** — `--list-images [FILTER]` lists every image of the target ebook (No. / filename / resolution / size / mode·depth / orientation / TOC / tag) plus a full statistics block (format / mode·depth / size distribution / double-page banners / animated GIF / small images / anomaly details), without converting, writing a CBZ, or generating ComicInfo; FILTER is optional and supports conditional expressions (format / `res` / `size` / orientation / mode / depth / tag, comma = OR, `+` = AND, `-` prefix = exclude); images with EXIF Orientation≠1 carry a `[rotateN]` mark (N=2–8, normal=1 not marked) also counted in the `[anomaly]` summary; orientation filter words: no value = select all orientation-anomalous images (rotate=auto will rotate), a value = exact EXIF Orientation match (e.g. `orientation=6`); `--json-out` adds an `orientation` field (v3.6.0)
- **Filename glob filter** — `name=` matches the filename with glob when its value contains `*` / `?` (case-insensitive; only `*` and `?` are special, `[]` is treated literally), and keeps substring matching otherwise; enabled in all three entry points `--list-images` / `--drop` / `--pages`, e.g. `name=*_cover*`, `name=p00?`
- **Image processing pipeline** — `--img-edit` applies rotation / mirror flipping / grayscale conversion / format conversion / re-encode quality control / scaling / whitespace trimming / EXIF stripping to output images (repeatable; split ops with '+' inside a value): `rotate[=auto|90|180|270]` burns EXIF Orientation into pixels and removes the orientation field before re-encoding (no value = auto, only images with Orientation≠1 are processed), `flip=x|y|both` mirrors the image (x = horizontal, y = vertical, both = both), `grayscale` converts to grayscale (always inserted right after flip, output stays RGB with equal channels), `format=jpeg|png|webp` (alias jpg; target format, entry suffix inside the cbz is renamed to match after re-encode; transparent-to-JPEG backfills with white by default, override with `format=jpeg,black` or a `#RRGGBB` color; JPEG/WebP saved with quality, PNG lossless), `quality=1-100` overrides the re-encode quality (default 95, out-of-range errors), `scale=NNN%` scales relative by percent keeping aspect ratios across pages (e.g. `200%` = double size, 1~1000) or `scale=NNNw` unifies target width in px with height scaled to the original ratio (e.g. `1200w`, 1~100000; the two syntaxes are mutually exclusive), `trim[=tolerance]` auto-trims uniform border whitespace (no value / auto = 0.05, detects the uniform edge background, safe margin avoids over-trimming), `strip` clears all EXIF metadata from images; fixed pipeline order `rotate→flip→grayscale→format→quality→scale→trim→strip` regardless of writing order; three entry points: before mobi→cbz conversion output / before `--repack` packing / in-place fixing of an existing `.cbz` (CBZ orientation-fix mode); works with `--dry-run` / `--json` / `--json-out` / `--log`
- **Double-page detection** — `--double-page` identifies full-width spread images (width/height ≥ ratio, default 2.0); when enabled it writes per-page DoublePage marks (without a Manga declaration); no value / `auto` enables, a number sets the ratio, `off` / `no` / `0` disables
- **Drop small images** — `--drop small[=ratio]` removes images whose area is clearly small (width × height < area median × ratio, default 0.5), such as cover thumbnails; PageCount is recalculated from the actual image count after dropping; no value / `auto` = 0.5, a 0~1 number sets the ratio, `off` / `no` / `0` disables; the old `--drop-small` remains a hidden alias (≡ `--drop small`)
- **ComicInfo field override** — `--setinfo FIELD=VALUE` overrides/adds ComicInfo fields (highest priority); VALUE supports fixed values / `%series` / `%number` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` placeholders, repeatable; FIELD must be in the ComicInfo standard-field whitelist (39 simple fields, complex `Pages` excluded; out-of-whitelist fields emit a warning and are ignored); for existing `.cbz` inputs, `%series`/`%number`/`%volume` read the explicit Series/Number/Volume from ComicInfo first, falling back to filename inference only when absent; when the input is an existing `.cbz`, its ComicInfo.xml is modified in place (unspecified fields keep their original values, written via temp file + atomic replace)
- **Auto-named log** — `--log` without a filename auto-generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory)
- **Unpack mode** — `--unpack` only extracts without converting, outputting to a `<source>_<ext>` subdirectory next to each source file (e.g. vol.cbz → vol_cbz/, never clashing with the source name; auto-numbered `(2)(3)` if it already exists); mobi uses extract preserving the full structure, cbz uses extractall (with zip-slip path-traversal protection); `.cbz` inputs are also collected when `--unpack` or `--setinfo` is given
- **Elapsed-time stats** — per-file conversion time is printed in real time, and the total elapsed time is shown at the bottom of the summary
- **JSON structured output** — `--json` prints JSON to stdout (a single-line compact JSON in conversion/modify mode, or one slim JSON per file in inspect mode; for AI / pipelines / scripts, suppresses human-readable text); `--json-out [FILE]` writes the structured result to a JSON file (indented format; omitting the filename auto-generates a timestamped file, behaving exactly like `--log`); supported in the conversion mode, the `--setinfo` modification mode, and the `--inspect` inspection mode, and can be used together
- **Debug mode** — `--debug` prints debug-level logs to stderr (silent by default, only printed when specified; debug output still appears even when combined with `--quiet`), for troubleshooting

## Supported image formats

The following image formats are recognized and packed during conversion: `.jpg` / `.jpeg` / `.png` / `.gif` / `.webp` / `.bmp` / `.tiff` / `.tif`

## Requirements

- Python 3.10+
- Runtime dependency: `mobi` (required)
- Optional: `pillow` (only needed for the `--img-edit` pipeline), `tqdm` (progress bars; falls back to plain-text progress if missing)

## Installation

```bash
pip install mobi          # required
pip install pillow tqdm   # optional: --img-edit pipeline / progress bars (falls back to text)
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
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --drop
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

> When run against existing CBZ files together with `--setinfo`, both real runs and dry-runs list the ComicInfo fields that would change per file before running (`~ field: old -> new`); fields that would only be added are marked with `+`, and unchanged fields are omitted.

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

### In-place orientation fix (auto-rotate orientation-anomalous pages by EXIF; CBZ in-place fix mode)

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.cbz" --img-edit rotate
```

The `--img-edit` image processing pipeline also applies before mobi→cbz conversion output and before `--repack` packing; `rotate` with no value (auto) auto-rotates orientation-anomalous images by EXIF Orientation (v3.6.0).

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

| Parameter | Description |
| --- | --- |
| `target` | Path to an ebook file, a directory containing ebooks (.mobi/.azw/.azw3/.epub), or a glob pattern with `*` / `?` (e.g. `*.epub`, `卷*/001.mobi`); use `.` for the current directory (required) |
| `--language LANG` | Output language: `auto` selects by system locale (zh prefix → Chinese, zh-TW/zh-Hant → Traditional Chinese, ja/Japanese → Japanese, otherwise → English), or specify `zh-CN`/`zh-TW`/`ja`/`en` (default `auto`); tolerant of common spellings: `zh`/`cn`→zh-CN, `zhtw`/`tw`→zh-TW, `jp`→ja, `eng`→en |
| `--top-only` | Only process ebook files directly in the target directory (do not recurse into subdirectories) |
| `--delete` | Delete the original ebook file after successful conversion (default: keep) |
| `--prefer` | Which copy to keep for dual-directory mobi: `auto` / `mobi7` / `mobi8` (default `auto`); `auto` prefers mobi8 and falls back to mobi7 when mobi8 has no images; explicitly specifying `mobi7`/`mobi8` falls back to the other when the chosen directory has no images |
| `--drop [EXPR]` | Unified drop entry (`nargs='?'`, repeatable = OR union): no value = `extra`, dropping all uncollected extra images (appended to the end of the cbz by default); with a value, drops by conditions — format words / condition words (`res` / `size` / orientation / mode / bit depth / tag: `double` / `thumbnail` / `animated` / `cover` etc., plus orientation-class `landscape`/`portrait`/`square` horizontal/vertical/square) / `small[=ratio]` small images; multi-condition comma = OR, `+` = AND, `-` prefix excludes, e.g. `--drop gif,extra`, `--drop small=0.4`, `--drop cover+overscale`; `off` / `no` / `0` disables; execution order: drop extra images → dedupe → filter → drop small images; dropped file names are listed, only counts under `--short-summary`; the old `--drop-extra` / `--drop-small` are merged into this option (hidden aliases, still usable) |
| `--overwrite` | Force regeneration when the target cbz already exists (default: skip) |
| `--ext-priority EXTS` | Which format to keep when files share the same name in the same directory (differing only by extension): comma-separated, order = priority high→low, accepts only mobi/azw/azw3/epub, default azw3; groups not covered fall back to azw3→epub→mobi→azw; unrelated to `--prefer` (dual-directory selection) |
| `--timeout` | Per-file conversion timeout in seconds; timeout files are skipped and counted as failed (default 600, `0` = no limit) |
| `--min-size BYTES` | Filter out ebooks smaller than the given bytes; default 1000 without a number, `0` disables, not passing it disables size filtering |
| `--output-dir DIR` | Output CBZ to the specified directory (auto-created); preserves the relative subdirectory structure of the input by default (e.g. `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`); add `--flatten` to flatten into the directory root |
| `--flatten` | Only used together with `--output-dir`: flattens all CBZ files into the output directory root; same-name files are skipped (SKIP) unless `--overwrite` is given, which overwrites the preferred name; using it alone (without `--output-dir`) exits with an error |
| `--progress` | Progress bar policy: `auto` shows when stderr is TTY and file count ≥ 2 and `--json`/`--json-out` is not used; `on` forces display; `off` disables (default `off`, not shown); writes to stderr, not into `--log` |
| `--no-progress` | Force-disable the progress bar (equivalent to `--progress off`; kept for old-command compatibility) |
| `--dry-run` | Dry run: only scan files and print the conversion flow, without unpacking/packing or creating output directories |
| `--rename[=TEMPLATE]` | Rename the output CBZ filename (optional template, off by default): no value = default template (series name + auto-chosen marker prefix by type `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`, connected chapters `話005-006` → `[Ch.5-6]`); the template supports `%series` / `%number` / `%volume` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` and `%03number` zero-padding placeholders; source priority: filename inference > built-in metadata (OPF / ComicInfo.xml) fallback, `--setinfo` not involved; when the input is an existing `.cbz` it enters a standalone rename mode (renames only, no conversion, combinable with other modes); on skip, two hint kinds are distinguished (target exists → suggest `--overwrite`; in-batch collision → suggest adjusting the template), JSON `reason` records `existing` / `conflict`; the dry-run preview colors `[Will Skip]` by collision class (on-disk existing = yellow, in-batch conflict = magenta, TTY + not `--no-color` only), and the summary splits the skip total into "on-disk existing N / in-batch conflict M" with the skipped file list grouped by class; `%description` is not recommended for filenames (content may be too long) — pair it with `%subN_M` to truncate; pair with `--dry-run` to preview first |
| `--no-color` | Disable ANSI color output (even when the terminal supports it); logs / JSON / pipes are never colored anyway |
| `--quiet` | Quiet mode: only show errors and the final summary |
| `--debug` | Debug mode: print debug-level logs to stderr (silent by default, only printed when specified; still printed even when combined with `--quiet`) |
| `--short-summary` | Compact summary: succeeded/skipped files show counts only (failed files always list full paths) |
| `--compress LEVEL` | zip compression level 0-9: `0` = no compression (default, images are already compressed), `1-9` = deflate (benefits PNG sources; higher = smaller but slower) |
| `--inspect [MODE][,FILTER]` | Inspect mode: `sample` randomly inspects 1 ebook (default), `all` inspects every file; a filter may be attached (e.g. `all,small=0.6`) and matched images print a count + filename list (with dimensions); a single-file positional argument inspects that file directly; unpack only to read internal info (metadata/structure/images/resolution/dual DRM judgment/NCX TOC), no CBZ produced, temp directory cleaned up automatically; the image preview lists the first 5 files and, when there are more, appends an English ellipsis line `...` (e.g. `... (188 images)`); TOC (NCX) / nav preview truncation is also unified to English `...`; the book-level summary adds a “N rotated image(s) (rotate=auto will rotate)” line with a `rotate_count` field carried out via `--json-out`, and orientation filter words are supported (e.g. `all,orientation`) (v3.6.0) |
| `--inspect-all` | Inspect all ebooks (equivalent to `--inspect all`; kept for old-command compatibility) |
| `--no-comicinfo` | Do not generate ComicInfo.xml (default: generates it into the CBZ root with Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary metadata) |
| `--setinfo FIELD=VALUE` | Override/add ComicInfo fields (repeatable, highest priority): `FIELD` is a ComicInfo field name and must be in the standard-field whitelist — 39 simple fields, the complex `Pages` excluded — (out-of-whitelist fields emit a warning and are ignored); `VALUE` supports fixed values / `%series` / `%number` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` placeholders (`%subN_M` = M chars from the Nth char, 1-based; field omitted only when the whole value is exactly one known placeholder and its value is missing); placeholders may be mixed with fixed text (e.g. `%writer·重制`, `第%number话`), in which case a missing value renders as an empty string; smart splitting: only splits when a comma is followed by `fieldname=`, otherwise the comma is part of the value (e.g. `Summary=Vol. 1, First Edition` is not split); for existing `.cbz` inputs, `%series`/`%number`/`%volume` read the explicit Series/Number/Volume from ComicInfo first, falling back to filename inference only when absent; when the input is an existing `.cbz`, its ComicInfo.xml is modified in place (unspecified fields keep their original values); use multiple `--setinfo` when a value contains `Key=`; when enabled, `.cbz` files mixed into the input are modified in place while other files convert as usual; `Manga` is not written by default — specify it explicitly with `--setinfo Manga=Unknown\\|No\\|Yes\\|YesAndRightToLeft` (official v2.0 enum only); `CommunityRating` (0-5) / `MainCharacterOrTeam` / `Review` are also supported |
| `--unpack` | Unpack to view: extract only, no conversion; outputs to a `<source>_<ext>` subdirectory next to each source file (e.g. vol.cbz → vol_cbz/, never clashing with the source name; auto-numbered `(2)(3)` if it already exists; `--output-dir DIR` sets the unpack output directory, defaulting to each source file's directory when omitted, v3.6.0); mobi uses extract preserving the full structure, cbz uses extractall (with zip-slip path-traversal protection); `.cbz` inputs are also collected when `--unpack` or `--setinfo` is given |
| `--repack` | Repack mode: packs an already-unpacked `_cbz` directory (directory name ends with `_cbz`, e.g. `vol_cbz/`) back into a CBZ; the output name restores the source file name (`vol_cbz` → `vol.cbz`); accepts a single directory or a parent directory for batch processing, prints the pending list before running (each line `unpack-dir → output.cbz`); an existing ComicInfo.xml inside the directory is carried over as-is, otherwise a basic one is generated — `--setinfo` can override it, `--no-comicinfo` disables it; existing output is skipped by default, `--overwrite` replaces it; `--rename` does not apply to this mode |
| `--double-page VALUE` | Double-page spread detection: omitted or `auto` enables it (threshold 2.0; detects wide banner spread images with width/height ≥ threshold, writing per-page `Type="DoublePage"` to ComicInfo; `Manga` is no longer declared automatically); a numeric value (e.g. `2.5`) enables it and adjusts the threshold; `off` / `no` / `0` disables it; invalid values error out |
| `--drop small[=ratio]` | Drop small images: exclude images whose area is clearly small during conversion (cover thumbnails / copyright pages, etc.) — an image is dropped when width × height < area median × ratio; `small` omitted or `auto` uses the default ratio 0.5, a `0~1` number (e.g. `--drop small=0.4`) adjusts it, `off` / `no` / `0` disables (disabled by default, existing behavior unchanged); ComicInfo `PageCount` is recomputed from the remaining images; summary / `--log` / `--json` report a "dropped small" count (`--json` emits a `dropped_small` field) and list the dropped file names one by one (only counts under `--short-summary`); `--inspect` preview shows "N image(s) will be dropped when --drop small is enabled"; wide double-page banners (width not small) are never mis-dropped; conversion mode only; the old `--drop-small` ≡ `--drop small` (hidden alias, still usable) |
| `--img-edit [EDIT]` | Image processing pipeline (repeatable; split ops with '+' inside a value): `rotate[=auto\|90\|180\|270]` burns the EXIF Orientation into pixels and re-encodes (no value = auto, only Orientation≠1 images), `flip=x\|y\|both` mirror flip, `grayscale` grayscale (always right after flip), `format=jpeg\|png\|webp` format conversion (transparent-to-JPEG backfills white by default; override with `format=jpeg,black` or `#RRGGBB`), `quality=1-100` re-encode quality (default 95), `scale=NNN%` or `scale=NNNw` scaling, `trim[=tolerance]` border trim (no value / auto = 0.05), `strip` removes EXIF; fixed order `rotate→flip→grayscale→format→quality→scale→trim→strip` regardless of writing order; three entry points: before mobi→cbz conversion output / before `--repack` packing / in-place fixing of an existing `.cbz`; works with `--dry-run` / `--json` / `--json-out` / `--log` |
| `--pages PAGES` | Page selection (repeatable; comma-separated inside one value, no quoting needed): process only the selected pages, page numbers start at 1 (page 1 = the 1st image in the volume). Supports single `5`｜closed range `1-3`｜open-ended `7-*` (* = last page), comma-mixed (e.g. `1-3,5,7-*`); out-of-range pages are ignored with per-page warnings; all-out-of-range / empty hits error out; with `--img-edit` only selected pages run the pipeline, with `--drop` AND-combined (pages locked first, then filtered), with `--unpack` / `--repack` only the selected pages are extracted/packed (v3.6.0); pages can also be selected by filter words — `name=` with `*` / `?` matches file names via glob (e.g. `name=*_cover*`, `name=p00?`), other words share the `--drop` vocabulary |
| `--list-images [FILTER]` | Read-only image listing: no value = list all images of the target ebook; with a value = FILTER expression (shared filtering engine with `--drop`: format / `extra` (images not in the OPF spine) / `res` / `size` / orientation / mode / bit depth / tag / `small[=ratio]`, plus orientation-class `landscape`/`portrait`/`square` horizontal/vertical/square; comma = OR, `+` = AND, `-` prefix excludes, e.g. `jpeg,size>1MB`, `-webp`); read-only scan — no conversion, no CBZ, no ComicInfo, no files written; CBZ read directly from zip (no TOC column / no conversion-state tags); per-file block (No. / filename / resolution / size / mode·depth / orientation / TOC / tag) + full statistics block (always full-set, unaffected by the filter); images with EXIF Orientation≠1 carry a `[rotateN]` mark (N=2–8, normal=1 not marked) also counted into the `[anomaly]` summary, and orientation filter words are available (`orient` / `orientation` / `direction` / `方向` / `方向異常`): no value = select all orientation-anomalous images (rotate=auto will rotate), a value = exact EXIF Orientation match (e.g. `orientation=6`); `--json-out` image records add an `orientation` field (v3.6.0); works with `--json` (one slim JSON per file) and `--quiet` (detail suppressed, count only); independent from `--inspect` |
| `--log FILE` | Append all output to the specified log file; without a filename, auto-generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory) |
| `--json` | Print JSON of the run result to stdout (for AI / pipelines / scripts); suppresses human-readable text output when enabled; one whole compact JSON in conversion/modify mode, or one slim JSON per file in inspect mode (status/series/number/source/page_count/drm); in dry-run mode it emits records carrying the `dry_run` flag (status `will_skip` / `pending`), nothing in unpack mode; can be combined with `--json-out`; progress bar goes to stderr and stays separate, but 2>&1 combined redirection mixes it in |
| `--json-out [FILE]` | Write the structured run result to a JSON file (indented format); without a filename, auto-generates a timestamped file (current directory, behaves exactly like `--log`); can be combined with `--json`; file-level results in conversion/modify mode, full record (incl. spine/toc and summary) in inspect mode |
| `--version` | Show version number |

## Parameter and Mode Effectiveness Matrix

Some parameters do not apply to every mode; inapplicable ones are silently ignored (no error, no warning). Use this matrix as the source of truth:

| Parameter | mobi→cbz conversion | `--unpack` | `--list-images` | `--repack` | CBZ in-place fix |
| --- | --- | --- | --- | --- | --- |
| `--img-edit` | ✅ pipeline before output | ⏭ ignored | ⏭ ignored | ✅ pipeline before writing images | ✅ in-place re-encode |
| `--drop` | ✅ drop/filter | ⏭ ignored | ⏭ ignored (use FILTER words for read-only filtering) | ⏭ ignored | ⏭ ignored |
| `--pages` | ✅ selected pages only | ✅ keeps selected pages only | ⏭ ignored | ✅ packs selected pages only | ✅ selected pages only |
| `--double-page` | ✅ writes DoublePage marks | ⏭ ignored | ⏭ ignored | ✅ keeps existing marks when ComicInfo is carried back | ⏭ ignored |
| `--rename` | ✅ renames output | ⏭ ignored | ⏭ ignored | ⏭ not applicable | ✅ in-place rename |
| `--setinfo` | ✅ ComicInfo override | ⏭ ignored | ⏭ ignored | ✅ overrides/generates ComicInfo | ✅ in-place ComicInfo edit |
| `--no-comicinfo` | ✅ no ComicInfo generated | ⏭ ignored | ⏭ ignored | ✅ no ComicInfo carried back | ⏭ ignored |
| `--delete` | ✅ deletes source after success | ⏭ ignored | ⏭ ignored | ⏭ not applicable | ⏭ not applicable |

> Note: rows for `--double-page` / `--rename` / `--setinfo` / `--no-comicinfo` / `--delete` follow the actual code behavior; `--unpack` also handles existing `.cbz` / `.epub` inputs (plain zip extraction), and `--pages` keeps only the selected page images after unpacking, numbered by natural sort order.

## Output

- By default, the converted `.cbz` file is placed in the same directory as the original ebook; with `--output-dir`, it goes to that directory (auto-created), preserving the relative subdirectory structure of the input, or flattened into the directory root with `--flatten` (same-name files are skipped unless `--overwrite` is given)
- Existing `.cbz` files are skipped by default and never overwritten; use `--overwrite` to force regeneration
- 0-byte / corrupt-header ebooks are skipped at the precheck stage, with the full path and reason logged
- Per-file conversion time is printed in real time; total elapsed time is shown at the bottom of the summary
- Failed files print an error message and do not block conversion of other files

## JSON output contract

In the structured output of `--json` / `--json-out`, the `status` field is the machine-consumed contract. Values per mode:

| Mode | `status` values | Failure detail |
| --- | --- | --- |
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

See [CHANGELOG_en.md](CHANGELOG_en.md).

## License

This project is licensed under the [GPL-3.0](./LICENSE).

### Third-party dependency license

This tool depends at runtime on the mobi library (v0.4.1, maintained by Titusz Pan), which is licensed under GPL-3.0-only. Please comply with GPL-3.0 requirements when distributing.