## [3.6.4] - 2026-10-24

### Fixes

- **OPF/HTML resource path traversal** — added `_path_inside` boundary check and applied it to `extract_images_from_html` / `extract_images_by_spine` / `find_ncx` / `parse_nav_toc` / cover href / `_resolve_toc_href_to_image`, rejecting `..` traversal, absolute paths and Windows drive-relative escapes
- **`--unpack` leaves a half-baked directory on failure** — switched to unpack-into-temp-dir + commit-on-success; failures / exceptions / empty `--pages` hits clean up the temp dir, never leaving the final output directory and never touching existing user directories
- **`--unpack --dry-run` inconsistent preview for same-named inputs** — `_unpack_target_dir` gained a `reserved` batch set; dry-run and real run share the same naming plan

### Internal

- Added `TestPathInside` / `TestUnpackSafety` / `TestExtractPathEscape` regression guards

## [3.6.3] - 2026-09-24

### Fixes

- **`--unpack --pages small` still ineffective** — when v3.6.2 unified the small-ratio extraction, only the `repack` path passed `pages_expr`; the `unpack` path still called `_dir_attrs_roll` without it, leaving the small mark empty. Now the argument is forwarded.
  
### Internal
  
- Extracted `_render_rename_preview` to merge the three rename-preview coloring sites (DRY)
- Added a set-consistency self-check between `_IMAGEDIT_PIPELINE_ORDER` and `_IMAGEDIT_IMPLEMENTED` to prevent regressions where docs/constants promise unimplemented operations

## [3.6.2] - 2026-09-15

### Fixes

- **`--pages small` was ineffective in unpack/repack paths** — `_dir_attrs_roll` hardcoded `None`, dropping the small ratio; now uniformly extracted from the `--pages` expression (default ratio without a value, the given value with one), symmetric with `_cbz_attrs_roll`
- **`--unpack` did not select the mobi7/mobi8 directory before numbering** — pages were numbered across the whole tree and could delete/mis-select across both directories; now `select_mobi_dir` runs right after `mobi.extract` before any page logic
- **`--repack` failed when the output directory did not exist** — the output directory is now auto-created before packing
- **Extremely small images crashed `--img-edit` whitespace trimming** — corner sampling raised IndexError when width or height was below 3px; now falls back to the center pixel
- **Mixed input (mobi conversion + CBZ modification) discarded CBZ-modification failures** — the final exit code now includes `cbz_failed`; any failure returns non-zero
- **Top-level hard `mobi` dependency check broke `--help` / `--version`** — replaced with lazy loading (`_require_mobi`); only modes that actually unpack mobi fail without the library
- **Preview stats reused the `run.error` message** — added a dedicated `img_edit.preview_fail` key in all four languages
  
### Docs
  
- **Removed unimplemented `denoise` / `whitebalance` pipeline promises** — the fixed pipeline order in all four help texts and README is now the actually implemented `rotate→flip→grayscale→format→quality→scale→trim→strip` (denoise/whitebalance remain as reserved words in comments only)
- **zh-TW `help.output_dir` synced with the other three languages** — `--unpack` outputs to the given directory
- **Added a parameter × mode matrix** — documents which modes honor `--img-edit` / `--drop` / `--pages` etc. (see "Parameter and Mode Effectiveness Matrix")
  
### Internal
  
- Removed the unused `delete_original` parameter of `ebook_to_cbz`

## [3.6.1] - 2026-09-07

### Fixed

- **`--pages` filter word `small` was ineffective** — the small-image mark was not filled in the mobi conversion and CBZ in-place fix paths (`_fill_small_mark` was passed `None`); now the small ratio is uniformly extracted from the `--pages` expression
- **`--delete` could delete the source file on a concurrent conversion timeout** — deletion is now confined to the main thread and only runs after a confirmed successful conversion; orphaned `mobi.extract` threads from a timeout no longer delete the source
- **`--setinfo` / `--img-edit` / `--rename` pure-CBZ modifications always exited 0 on failure** — now return a non-zero exit code based on the number of failed files (success/skip = 0)
- **Missing CBZ in-place fix error wording (`run.error` completed in all four languages)** — no more KeyError
- **Preview statistics exceptions were silently swallowed** — `_preview_img_edit_count` now prints an error hint before returning
  
### Internal
  
- Removed the dead `drop_extra_hit` variable

## [3.6.0] - 2026-09-05

### Added

- **`--pages` page selection** — process only the selected pages (page numbers start at 1, page 1 = the 1st image in the volume); repeatable (union semantics), comma-separated in one value without quoting: supports single `5`, closed range `1-3`, open range `7-*` (* = last page), mixed with commas (`1-3,5,7-*`); out-of-range pages are ignored with per-page warnings, all-out-of-range / empty hit errors out; combined with `--img-edit` only selected pages go through the pipeline, coexists with `--drop` (AND), and with `--unpack` / `--repack` only selected pages are processed
- **`--img-edit` image processing pipeline** — applies rotation / mirror flipping / grayscale / format conversion / re-encode quality control / scaling / whitespace trimming / EXIF stripping to output images, with three entry points: before mobi→cbz conversion output, before `--repack` packing, and in-place fixing of an existing `.cbz` (CBZ orientation-fix mode). `rotate[=auto|90|180|270]` handles orientation as described above; `flip=x|y|both` mirrors; `grayscale` converts to grayscale (always inserted right after flip, output stays RGB with equal channels); `format=jpeg|png|webp` (alias jpg; target format, entry suffix inside the cbz is renamed to match after re-encode; transparent-to-JPEG backfills with white by default, override with `format=jpeg,black` or a `#RRGGBB` color; JPEG/WebP saved with quality, PNG lossless); `quality=1-100` overrides the re-encode quality; `scale=NNN%` scales relative by percent keeping aspect ratios across pages (e.g. `200%` = double size, 1~1000) or `scale=NNNw` unifies target width in px with height scaled to the original ratio (e.g. `1200w`, 1~100000; the two syntaxes are mutually exclusive); `trim[=tolerance]` auto-trims uniform border whitespace; `strip` clears all EXIF metadata (always the last pipeline stage); fixed pipeline order `rotate→flip→grayscale→format→quality→scale→trim→strip` regardless of writing order
- **`name=` filename glob filter** — when the `name=` value contains `*` / `?`, filenames are matched with glob (case-insensitive; only `*` and `?` are special, `[]` is treated literally), otherwise substring matching is kept; enabled in all three entry points `--list-images` / `--drop` / `--pages`, e.g. `name=*_cover*`, `name=p00?`
- **`--drop` repeatable and takes an OR union** — repeated flags accumulate (`--drop a --drop b` = OR of both conditions); the hidden alias `--drop-extra` is retained
- **`--unpack` supports `--output-dir`** — optional output directory; if omitted, the folder containing the source file is used
- **`--list-images` `[rotateN]` mark, orientation filter words, and `orientation` field** — images with EXIF Orientation≠1 show a `[rotateN]` mark and are counted in the `[anomaly]` summary; orientation filter words: no value = select all orientation-anomalous images (rotate=auto will rotate), a value = exact EXIF Orientation match (e.g. `orientation=6`); `--json-out` adds an `orientation` field
- **`--inspect` book-level rotation total summary** — adds a "N rotated image(s) (rotate=auto will rotate)" line and an `info.rotate_count` field carried out via `--json-out`; orientation filter words supported (e.g. `all,orientation`)
  
### Fixes
  
- **Big-endian TIFF EXIF Orientation parsing** — fixed the bug that misread SHORT values as 4 bytes with a mask; now decodes 2 bytes according to byte order

## [3.5.4] - 2026-09-04

### Fixes

- **`--dry-run` now respected in `--unpack` / `--repack` modes** — both modes previously ignored `--dry-run` and performed real extraction/repacking to disk; both now short-circuit at the entry, printing the extraction/repack plan only without writing anything (including the `--json` / `--json-out` output), matching the help contract "no extraction, packing or output directories"
  
### Maintenance
  
- **Unpack target-directory naming extracted to `_unpack_target_dir`** — shared by real unpacking and the `--dry-run` preview so the preview matches real runs

## [3.5.3] - 2026-09-02

### Fixes

- **`--list-images` exit code fix for invalid filter expressions** — the invalid-expression branch returned a bare `return`; changed to `return 1` so `_main` no longer calls `max(mode_codes)` on an empty list (TypeError)
- **`get_drm_flag` EXTH offset correction** — the in-item offset used to read the DRM flag is corrected from `+14` to `+12` (`0x0E` → `0x0C`)

## [3.5.2] - 2026-09-01

### Maintenance

- **`_list_ebook` reuses `ensure_cover_first`** — removes duplicated cover fallback scanning (the filename-keyword cover completion is now a single implementation)
- **`parse_inspect_arg` local `t` renamed to `tok`** — no longer shadows the i18n translation function `t()`
- **`emit` log now uses a persistent handle** — no longer opens/closes the log file on every write

## [3.5.1] - 2026-08-31

### Fixes

- **P0: `%%` placeholders restored in help texts across all four languages** — `help.setinfo` / `help.rename` help texts had been changed to single `%`, causing argparse to expand help as a `%` format string and raise TypeError; restored to `%%` (module docstring keeps single `%`)
- **P1: three modes now return their exit code** — `--unpack` / `--inspect` / `--list-images` no longer call `sys.exit` directly; they return the exit code instead, and `_main` runs a single `sys.exit(max(mode_codes))`, so chained modes are no longer interrupted
- **P2: `--repack` examples/comments end with `_cbz`** — the "directory name ends with .cbz" wording in examples and code comments changed to `_cbz`; the docstring example `Vol_cbz --repack` updated accordingly
- File-header usage line `[--inspect sample|all]` → `[--inspect [sample|all][,FILTER]]`
- `help.output_dir` in all four languages now notes "ignored in `--unpack` mode"
  
### Changes
  
- **Generic exception fallback in the main loop** — the `_convert_one` nested function is extracted with an added `except Exception`, so unexpected errors are counted as failed files instead of aborting; a new `run.unexpected_error` message key is added in all four languages

## [3.5.0] - 2026-08-28

### New features

- **`-` prefix exclusion** — `--drop` / `--inspect` filters now support negative conditions (e.g. `all,small=0.6,-gif`), parsed by the same expression engine as comma OR / plus AND
- **`--repack` ignores `--rename` with a hint** — in repack mode the output name is inferred from the unpack directory name; when `--rename` is ignored a hint is printed
- **`--repack` processing list annotates the inferred output name** — each line of the pre-execution processing list shows `unpack dir → output.cbz`, making the inference source obvious (this is the internal list display of `--repack` mode, not a separate parameter)
  
### Changes
  
- **Refined exit-code semantics** — target path does not exist → exit `2`; `--repack` with no usable unpack directory / no `_cbz` directory → exit `2` and counted as 1 failure; `--unpack` extraction failure → exit `1`; `--inspect` exception → exit `1`; Ctrl+C during conversion → exit `130` (128+SIGINT)
  
### Fixes
  
- `--drop-small` invalid-value message was self-contradictory (also suggesting off/no/0); now "use auto or a number (0~1)"
- `--setinfo` help and the file-header example used a double `%%` placeholder; corrected to single `%`
- `--unpack` collision-avoidance wording (default 源名_扩展名, falls back to `(N)` suffix when the name is taken)
- `--inspect` help now documents FILTER syntax (same as `--drop`: comma=OR, plus=AND, `-` prefix excludes)
- `help.setinfo` / `help.rename` help texts in all four languages had a double `%%` placeholder typo → unified to single `%`
  
### Maintenance
  
- Regression-test exit-code expectation updated (missing target `1` → `2`)

## [3.4.0] - 2026-08-26

### New features

- **Exit code semantics** — `0` = all succeeded (including all-skipped with no failures); `1` = at least one file failed conversion (conversion failure / DRM / validation failure); `2` = command-line usage error (built-in argparse), for scriptable success/failure detection
  
### Changes
  
- `--inspect --json` compact stdout now includes a `formats` summary field (per-format image count distribution)
  
### Maintenance
  
- Regression tests increased to 56 cases (new: exit-code semantics / inspect formats / version guard)

## [3.3.0] - 2026-08-25

### New features

- **`--drop [EXPR]` unified drop entry** — no value drops extra images outside the collection (same semantics as the old `--drop-extra` with no value); format words / condition words / `small[=ratio]` all accepted; multi-condition comma = OR, plus = AND, `-` prefix excludes, `off` disables; the old `--drop-extra` / `--drop-small` are demoted to hidden aliases and merged in
- **`--inspect [MODE][,FILTER]`** — on top of sample/all, a filter may be attached (e.g. `all,small=0.6`); matched images print count + filename list (with dimensions); `--json` gains a matching `filter_hits` structure
- **`small` standalone parameterized condition word** — no value / auto = default ratio 0.5, a 0~1 number sets the ratio; the four-language aliases (异常小图 / 異常小圖 / 異常小画像 / 極小画像) all accept a ratio
  
### Changes
  
- The three pipelines (conversion drop / inspect preview / list) are all driven by the `--drop` expression; the small-image area criterion has a single source
- `--drop-extra` / `--drop-small` are hidden from `--help` (still usable for compatibility)
  
### Maintenance
  
- Regression tests increased to 46 cases

## [3.2.0] - 2026-08-24

### New features

- **[abnormal] always-on inline marker** — shown in the first column as a rollup of any anomaly in that row, visible at a glance
- **[inferred] dedicated inference marker, replacing "疑似"** — inference-based annotations (rotated double-pages / thumbnails / cover fallback) drop the "疑似" tag: entries inferred only from size / filename and not explicitly declared by the OPF are marked `[inferred]` (OPF guide covers / animated images / extras are not marked); new four-language filter aliases `inferred` / `推断` / `推斷` / `推測` / `推定`
  
### Changes
  
- **Mode column unified to canonical English names** — `index` / `gray` / `rgb` / `graya` / `rgba`; the four-language localization keys are removed to reduce maintenance
- **Small-image detection switched to an area-based criterion** — width × height < area median × ratio, unified with the `--drop-small` ratio — what is marked gets dropped; the `--list-images` / `--inspect` preview / conversion-drop pipelines now share one criterion
- **`[small]` is no longer marked when `--drop-small` is off** — consistent with "what is marked gets dropped"
  
### Maintenance
  
- Regression tests synchronized (34 cases, all passing)

## [3.1.1] - 2026-08-24

### Fixes

- `--unpack` help text still carried the old "auto numbered-avoidance" wording, contradicting the unified `source_ext` naming since v3.1.0; corrected in all four languages
  
### Maintenance
  
- `--repack` help now notes that `--rename` does not apply to this mode; `--list-images` help now explains the [append] / [drop] / [filter] disposition markers
- Regression tests expanded to 34 cases (three new groups: repack restore + ComicInfo overlay, `_safe_zip_extract` `C:foo` escape, `name` atom on WindowsPath)

## [3.1.0] - 2026-08-24

### New features

- **Multilingual filter expressions** — the FILTER of `--list-images` / `--drop-extra` now accepts aliases in four languages (e.g. `封面` / `cover` / `表紙`); display tags can be pasted directly (square brackets are stripped automatically)
- **New statistics tag keywords** — `overscale` / `rotated_double` / `anom` (超大页 / 疑似旋转跨页 / 异常); also supported by `--drop-extra` for dropping matching images during conversion; abnormal and extra are independent dimensions and never cascade into each other
- **Filename filter `name=keyword`** — case-insensitive substring match on the filename (incl. extension); combinable with tag and attribute conditions
- **Disposition filter keywords** — `append` / `drop` / `filter` (追加 / 舍弃 / 筛选) to select images that will be appended, dropped, or matched by the drop filter
- **`--repack` mode** — repack an unpacked `_cbz` directory (name ending in `_cbz`, e.g. `vol_cbz/`) back into a CBZ, restoring the source filename (`vol_cbz` → `vol.cbz`); accepts a single directory or a parent directory for batch processing, and lists the todo list before running. A `ComicInfo.xml` inside is carried back as-is, or a basic one is generated if missing; combine with `--setinfo` to override fields or `--no-comicinfo` to disable. Skips existing output by default, `--overwrite` to force
- **Uniform unpack directory naming `source_ext`** — `--unpack` output directories are renamed from `vol.cbz/` to `vol_cbz/` (`vol.mobi` → `vol_mobi/`), so they never collide with the source file and no numbered fallback appears; any `_cbz`-suffixed directory can be repacked with `--repack`
- **`--setinfo` prints a change plan before running** — the non-dry-run branch also lists the ComicInfo fields to add/modify per file before executing (`~ field: old -> new`, new-only fields marked with `+`), consistent with the "todo list + done summary" convention of `--unpack` / `--repack`
  
### Fixes
  
- `cover` / `extra` filter keywords did not cover the cover-fallback image (cover_extra), so the cover filter used to match 0 rows
- `_parse_atom` crash on `8bit`; `name` atom crashed on Windows due to `WindowsPath`
- Cover-fallback image was wrongly counted in the "abnormal" detail
- `_safe_zip_extract` now guards against drive-relative path escape (`C:foo`), closing the zip-slip defense chain
  
### Maintenance
  
- New regression tests `tests/test_mobi2cbz.py` (30 cases: multilingual aliases / bracket pasting / `name` / anomaly tags / disposition filters / cover_extra fix)

## [3.0.0] - 2026-08-24

### Breaking changes

- **License switched to GPL-3.0-only** — because this tool depends at runtime on the mobi library (GPL-3.0-only), public distribution of this project constitutes distribution, so the license changed from MIT to GPL-3.0-only; LICENSE is replaced with GNU GPL v3 and the License section of this README was updated accordingly
- **Progress bar off by default** — no longer auto-shown; enable explicitly with `--progress on` / `--progress auto`; unified to `--progress auto|on|off` (omitted or `off` = hidden; `auto` = shown on TTY with ≥ 2 files and when `--json`/`--json-out` are not used); legacy `--no-progress` kept as a hidden alias
- **`--inspect` argument collapsed** — `--inspect [sample|all]` (default `sample` = old random check of 1, `all` = old `--inspect-all`); the old black-box behavior where `--inspect-all` alone auto-enabled `--inspect` is removed, you must pass `--inspect all` explicitly; `--inspect-all` kept as a hidden alias

### New features

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

### Fixes

- **NCX lookup miss** — Added unified `find_ncx` lookup (first by OPF manifest `media-type=application/x-dtbncx+xml`, then by the id referenced by the spine `toc` attribute, finally falling back to `*.ncx`), compatible with packages that name the NCX `xml/vol.nav` instead of using a `.ncx` extension; `parse_ncx_toc` / `parse_ncx_entries` now use it
- **`--inspect` TOC (NCX) count scope** — Count only `<navLabel><text>` entries (previously docTitle/docAuthor were counted too, inflating the entry count by 1-2)
- **`--rename` `%title%` placeholder now falls back to OPF `dc:title`** — previously `%title%` only read ComicInfo.xml `<Title>`, so an epub without a ComicInfo always yielded an empty value; now OPF `dc:title` is read as a fallback; source priority: OPF `dc:title` → ComicInfo.xml `<Title>` (consistent with the series/number OPF fallback)
- **New `%writer` / `%publisher` / `%date` / `%language` / `%description` placeholders for `--rename` / `--setinfo`** — OPF reads `dc:creator` / `dc:publisher` / `dc:date` / `dc:language` (normalized) / `dc:description`, ComicInfo reads `<Writer>` / `<Publisher>` / `<LanguageISO>` / `<Summary>`; `%date` keeps the raw date string (e.g. `2024-01-15`; ComicInfo has no counterpart); OPF takes priority over ComicInfo
- **DRM false-positive fix** — `get_drm_flag` previously read 2 bytes at PalmDB header offset 12 (which landed in the name field, so ebooks whose filenames contain `-`/`_`, e.g. the [Anon] series, were misjudged as encrypted); it now reads the copy-protection bit at attributes offset 32 plus the PalmDOC header encryption type (offset 78 + 8×nrec + 0x0E) as the authoritative criterion
- **`--inspect` no longer skips unpacking on a DRM marker** — the DRM marker is demoted to an informational flag; unpacking is still attempted: images extracted → `status=ok` with a `drm` marker; it is classified as DRM only when unpacking fails and the image count is 0
- **`--drop-extra cover` atomic no-op fix** — covers are now tagged via OPF guide + COVER_KEYWORDS on both the list and conversion paths, so `--drop-extra cover` reliably drops the cover
- **Mixed `--setinfo` placeholders with fixed text** — a value may mix placeholders and literal text (e.g. `%writer·remaster`, `第%number话`), with the same global replacement as `--rename`: missing values render as empty, unknown placeholders are kept verbatim; when the whole value is exactly a single known placeholder, the original semantics are preserved (the field is not written when missing)
- **NCX / NAV TOC parse order and entity decoding** — `parse_ncx_entries` now builds the tree with a stack and walks it in document order (parents always precede children; siblings keep document order), stripping nested tags from titles and decoding HTML entities (`&amp;` → `&`); `parse_nav_entries` gains the same entity decoding

### Security

- **XXE injection protection (P0)** — all `ET.parse` calls replaced with `safe_et_parse` (7 call sites); only `<!ENTITY` entity declarations are blocked (bare DOCTYPE is allowed through); string paths only reject `..` traversal (a `./` prefix and plain relative paths are allowed, so unpacked OPF/NCX references keep working)

### Fixed / Maintenance

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

### Review fixes (follow-up batch)

- **GIF frame-count false positive fixed (P0)** — `gif_frame_count` no longer scans LZW compressed data with `head.count(b"\x2c")`; it now parses GIF structure blocks (counting only image descriptors `0x2C` and skipping LZW data by sub-block boundaries without reading contents), so stray `0x2C` bytes inside a static GIF's compressed data no longer mis-flag it as `animated`; a truncated header exits safely
- **zip-slip drive / UNC escape protection (P0)** — `_safe_zip_extract` now also checks `Path.is_absolute()`, rejecting drive-letter (`C:/...`) and UNC (`//server/share`) absolute-path entries that could write outside `out_dir` (previously only `/`-prefixed and `..` segments were blocked)
- **`validate_cbz` tail seek (P1)** — files > 70KB are now seeked to read only the trailing `ZIP_EOCD_READ_TAIL` (70000) bytes instead of reading the whole file then slicing; peak memory for validating large CBZs drops from O(file size) to O(70KB)
- **`build_cbz_image_attrs` streaming header read (P1)** — switched to `zf.open().read(HEAD_READ_BYTES)` (lazy decompression) instead of `zf.read(name)` (whole-image decompress then slice), reducing decompression work and memory for large image entries
- **`_fill_small_mark` magic-number cleanup (P2)** — the hard-coded `0.5` is replaced with the constant `DEFAULT_DROP_SMALL_RATIO`; semantics and behavior are unchanged

## [2.5.1] - 2026-08-20

### Fixed

- **Deduplication no longer drops same-name `.cbz`** — in `--setinfo` / `--inspect` / `--unpack` modes, converted `.cbz` files no longer join same-name deduplication with mobi/azw/azw3/epub, so existing CBZ can be modified / checked normally
- **Dedicated hint for flatten name conflicts** — when a second same-name source is skipped under flatten mode, it now clearly flags a flatten conflict instead of the generic "target already exists", and suggests `--overwrite`

## [2.5.0] - 2026-08-20

### Changed

- **`Manga` no longer written automatically** — double-page detection (`--double-page`) only emits `<Pages>` per-page `Type="DoublePage"` markers and no longer appends a `<Manga>Yes</Manga>` declaration (readers like Mihon do not read that field, and it avoids declaring Manga even without spreads); `Manga` is now set explicitly via `--setinfo Manga=Unknown|No|Yes|YesAndRightToLeft`, limited to the official v2.0 enum; invalid values emit a warning and are ignored
- **`--ext-priority` supports EPUB** — accepts `mobi` / `azw` / `azw3` / `epub`; the fallback order when priority does not cover a group is now `azw3 → epub → mobi → azw` (EPUB is kept over the mobi family)
- **No-image hint split by extension** — EPUB with no images now gets a neutral hint (confirm it contains comic images and is not encrypted) instead of a false Kindle DRM warning; mobi/azw/azw3 still hint at possible DRM

### Added

- **`--setinfo` whitelist extended (39 → 42)** — three more official ComicInfo v2.0 fields: `CommunityRating` (0-5 rating) / `MainCharacterOrTeam` / `Review`
- **`--drop-small` drops small images** — disabled by default; when enabled, images clearly smaller than the rest are excluded during conversion (cover thumbnails / copyright pages, etc.): an image is dropped when both its width and height are < median × ratio (default ratio 0.5, adjustable with a `0~1` value, `off`/`no`/`0` disables); reads PNG/JPEG header dimensions per image with no new dependencies; ComicInfo `PageCount` is recomputed from the remaining images; the summary / `--log` / `--json` report a "dropped small" count (`--json` emits `dropped_small`); `--inspect` preview warns "N image(s) will be dropped when --drop-small is enabled"; wide double-page banners (width not small) are never mis-dropped

### Docs

- **`--help` synced in four languages** — `help.description` / `help.target` / `help.ext_priority` now mention `.epub`; `help.setinfo` documents the Manga enum and explicit specification
- **Encrypted EPUB note** — the FAQ clarifies that encrypted EPUBs (e.g. Adobe DRM) cannot be converted; remove DRM first

## [2.4.0] - 2026-08-20

### Added

- **EPUB input support** — accepted input extensions expanded to `.mobi` / `.azw` / `.azw3` / `.epub`; `ebook_to_cbz` / `--inspect` / `--unpack` branch by extension: EPUB (a ZIP container) is safely unpacked via zipfile (with zip-slip path-traversal protection), while mobi/azw/azw3 still go through `mobi.extract`; the existing OPF spine extraction and ComicInfo metadata pipeline is reused, with no parallel implementations
- **EPUB cover fallback enhanced** — `get_opf_guide_cover_href` now checks three sources in order: ① guide `type="cover"` ② manifest `properties="cover-image"` (EPUB3) ③ the item referenced by `<meta name="cover">` (EPUB2); cover href resolution corrected to be relative to the OPF directory (EPUB OPFs usually live in OEBPS/)
- **EPUB metadata supplement** — without an EXTH header, `--inspect` reads title/author/language/date/publisher from OPF `dc:` fields instead; `get_drm_flag` passes EPUB through directly (a ZIP container has no PalmDB DRM field, avoiding false positives)
- **`--prefer` silently ignored for EPUB** — EPUB has no mobi7/mobi8 dual directories and is naturally single-directory
- **EPUB3 nav TOC recognition** — `--inspect` locates the nav document via OPF manifest `properties="nav"` (fallback: `*nav*.xhtml`), parses `<a>` titles inside `<nav epub:type="toc">` (nested levels included); shown alongside the EPUB2 `toc.ncx`, so a pure EPUB3 without .ncx still gets a TOC
- **ComicInfo series/number read from metadata first** — when generating ComicInfo, Series/Number are now taken from OPF metadata first (`dc:series` / `dc:number`, EPUB3 `belongs-to-collection` / `group-position`, calibre's `meta[name=calibre:series/series_index]`); `dc:number` is auto-stripped of volume markers (`卷12` → `12`), and only falls back to filename inference when no OPF metadata exists
- **Double-page detection (`--double-page`)** — on by default (threshold 2.0): detects wide banner spread images whose width/height ≥ threshold, and writes `<Manga>Yes</Manga>` top-level tag + per-page `Type="DoublePage"` into ComicInfo; `--double-page auto` equals the default, `--double-page 2.5` adjusts the threshold, `--double-page off` (or `no` / `0`) disables it, and invalid values error out
- **ComicInfo field source annotation** — the `--inspect` preview annotates Series/Number with their source (`[setinfo]` / `[opf]` / `[inferred]`), so you can tell at a glance whether a field came from user specification, OPF metadata, or filename inference; `--json` also gains `series_source` / `number_source` / `cover_source` fields (values such as `setinfo` / `opf` / `inferred` / `filename`) for AI/pipeline trust assessment

### Changed

- **Unified safe extraction for `--unpack`** — CBZ and EPUB share `_safe_zip_extract` (zip-slip protection), simplifying the logic
- **Streaming rewrite for `--setinfo` CBZ modification** — `modify_cbz_comicinfo` no longer loads the whole archive into memory; it copies entries with dual handles (1MB chunks) and only reads `ComicInfo.xml` into memory; per-entry compression method / timestamps / attributes are preserved, and atomic replacement with exception cleanup is unchanged (memory for large archives drops from O(whole archive) to O(single entry))
- **ComicInfo priority reordered (setinfo > OPF metadata > filename inference)** — previously Series/Number came straight from filename inference (`infer_series_number`); now user-specified `--setinfo` wins, then OPF metadata, and filename inference is only the last resort; files with a bare volume marker and no series name (e.g. `Vol.01.mobi`) now return the number only, not a fake series name
- **Volume-inference regex expanded** — `infer_series_number` now covers: `卷N` prefix style, `vN`, `第N册`/`N册`, `巻N` prefix style, French `tome N`, Korean `권N`, Thai `เล่ม N`, Russian `Том N`, Chinese-numeral volumes (`第一卷`/`卷二`), and fractional volumes (`Vol 7.5`)
- **CoverSource removed from Notes** — cover source is no longer written into the `Notes` field of ComicInfo (avoiding non-standard notes leaking into the cross-software shared ComicInfo.xml); it is now surfaced via the `--inspect` cover line and the `--json` `cover_source` field, and Notes keeps content fields only

## [2.3.1] - 2026-08-19

### Fixed

- **Hardened atomic replacement in the conversion branch** — the temp file is validated with validate_cbz before `os.replace` overwrites the target; on failure only the tmp is cleaned and the old CBZ is kept; a ComicInfo generation failure no longer deletes an existing target CBZ; Ctrl+C (KeyboardInterrupt) leftover `.tmp` files are cleaned up by a finally block
- **Unknown `--setinfo` placeholder warning** — out-of-whitelist placeholders emit a warning and are written as-is (new i18n keys in all four languages)
- **sanitize extended** — ASCII control characters stripped, trailing dots/spaces removed
- **find_opf naming priority** — `content.opf` / `package.opf` preferred when multiple OPFs exist
- **Maintenance** — stale docstrings cleaned; `_strip_html` switched to HTMLParser (dead `import html` removed)

### Docs

- **`--help` wording extended (zh-CN/zh-TW/en/ja)** — `--setinfo`: use multiple options when a value contains `Key=`, existing `.cbz` inputs are modified in place when enabled; `--json`/`--json-out`: only emitted in conversion/modify mode (nothing in dry-run/inspect/unpack), progress bar goes to stderr and stays separate, but 2>&1 combined redirection mixes it in
- **README usage notes synchronized** — setinfo / JSON sections and the parameter table updated accordingly

## [2.3.0] - 2026-08-19

### Added

- **JSON structured output** — `--json` prints a single-line compact JSON to stdout (for AI / pipelines / scripts; suppresses human-readable text output when enabled); `--json-out [FILE]` writes the structured result to a JSON file (indented format; omitting the filename auto-generates a timestamped file, behaving exactly like `--log`); the two can be combined; supported by both the conversion mode and the `--setinfo` modification mode

### Fixed (merged from the v2.2.1 interim fixes)

- **Atomic replacement in the conversion path** — CBZ packaging now writes to a `xxx.cbz.tmp` temp file first and only `os.replace`s it over the target after everything succeeds; removed the unlink of the old CBZ before packaging and the deletion in failure branches, so only the half-written tmp is cleaned on exception. Eliminates the risk of a truncated CBZ left behind by Ctrl+C / mid-run crash, and the data-loss risk of losing the old file when overwrite fails (consistent with the existing atomic replacement in CBZ modification mode)
- **`--inspect` non-numeric PageCount warning** — a non-numeric PageCount in ComicInfo now emits a warning instead of being silently ignored (new i18n key `inspect.pagecount_non_numeric`, synced across all four languages)
- **`--timeout` help text** — now notes that the underlying unpack thread may linger in the background after a timeout; the `--overwrite` message now reads "old file will be replaced", matching the actual atomic-replacement behavior

## [2.2.0] - 2026-08-18

### Added

- **CBZ modification mode** — when the input is an existing `.cbz` and `--setinfo` is given, its ComicInfo.xml is modified directly: read the original XML → overwrite the specified fields, keep unspecified fields at their original values → write via temp file + atomic replace (`os.replace`); covered by `--dry-run` preview / summary stats / `--log`
- **setinfo whitelist** — `--setinfo` field names must be within the ComicInfo standard-field whitelist (39 simple fields, complex `Pages` excluded); out-of-whitelist fields emit a warning and are ignored
- **Source-newer auto-reconvert** — resume support now compares the source file's mtime with the target CBZ's; when the source is newer, it is automatically reconverted
- **`--unpack` / `--setinfo` accept CBZ input** — the collection stage also gathers `.cbz` files when `--unpack` or `--setinfo` is given
- **`--prefer auto` (default)** — dual-directory mobi now defaults to auto: prefers mobi8, falls back to mobi7 when mobi8 has no images; explicitly specifying `mobi7`/`mobi8` falls back to the other when the chosen directory has no images
- **Summary HTML cleanup** — the ComicInfo Summary field strips HTML tags (plain text written to disk)
- **Cover-source annotation** — the ComicInfo Notes field appends `CoverSource` (OPF guide / filename match)
- **CBZ precheck** — `.cbz` inputs now also go through 0-byte / `--min-size` checks
- **`--inspect` PageCount consistency check** — compares the ComicInfo PageCount inside a CBZ with the actual image count and reports a mismatch

### Changed

- **`--unpack` path safety** — cbz unpacking gains zip-slip path-traversal protection (rejects `..` / absolute-path entries) and prints an unpack summary
- **Multiple OPF warning** — when a directory contains more than one `.opf`, a warning is emitted and the first one is used
- **Corrupt-CBZ reconvert reason** — the resume path now prints the specific `validate_cbz` failure reason when reconverting a corrupt CBZ
- **HTML image path compatibility** — `<img>` src extraction strips query / fragment (`?` / `#`) before resolving the local path
- **Directory creation timing** — no longer creates the output directory early when the target CBZ already exists and will be SKIPped
- **Code hygiene** — `ebook_to_cbz` return-type annotation completed to the triple; `_auto_language` tail made explicit

## [2.1.0] - 2026-08-17

### Added

- **Resume support (default behavior)** — if the target CBZ already exists and passes `validate_cbz`, it is skipped (SKIP); corrupt/invalid output is automatically reconverted; `--overwrite` unconditionally overwrites
- **Failure classification** — `ebook_to_cbz` now returns a triple `(result, status, reason)`; failure reasons are categorized as `timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other`; the main flow adds a `failed_reasons` counter shown in the summary
- **`--inspect` supports CBZ** — merged into `inspect_ebook`; the CBZ branch reads purely via zipfile without unpacking; extracted `image_dimensions_bytes(bytes)` for reuse
- **`--inspect` output enhancement** — cover line gains resolution+size, format stats gain total file count, and each of the first 5 Spine entries gains width/height
- **`--setinfo FIELD=VALUE`** — override/add ComicInfo fields (repeatable, highest priority); VALUE supports fixed values / `%series` / `%number` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M`; smart splitting (only splits when a comma is followed by `fieldname=`); CBZ modification mode rewrites the zip directly; the `--inspect` preview block applies it too
- **ComicInfo written in the same zip pass** — removed the `write_comicinfo` function; `zf.writestr` inside the Step4 `with` block
- **`--log` auto-naming** — `nargs="?"` + `const="auto"`; auto generates `manga-mobi2cbz_YYYYMMDD_HHMMSS.log` (current directory)
- **`--unpack` unpack-to-view** — extract only, no conversion; mobi uses extract preserving the full structure, cbz uses extractall; defaults to a same-name directory, auto-numbered `(2)(3)` if it already exists

## [2.0.2] - 2026-08-17

### Changed

- `infer_series_number` now supports parenthesized suffixes: a `(author)` suffix no longer blocks volume inference (e.g. `Sample Series - Vol. 23 (Sample Author)` correctly infers Series=Sample Series / Number=23)
- Pure volume markers (`Vol.01` / `第 01 卷` / `01巻` etc.) now return only the volume number `(None, number)` instead of `(None, None)`, so ComicInfo can write Number
- `--flatten` same-name handling changed to SKIP/`--overwrite`: same-name files in the flat output root are no longer auto-renamed and re-converted as `(2).cbz`; without `--overwrite` they are skipped (SKIP), with it the preferred name is overwritten; dry-run stays consistent with the real run
- Removed the now-unused `unique_path` function

### Fixed

- Fixed PageCount consistency: physical dedup now happens before ComicInfo generation; both PageCount and packaging use the deduplicated actual written count
- Fixed `run_with_timeout` cross-version: except now catches both built-in `TimeoutError` and `concurrent.futures.TimeoutError` (Python 3.10 compatible)
- Fixed `infer_series_number` dot failure: now uses `path.name` with manual extension removal, so dotted volume numbers like `Sample Series Vol.01` infer correctly
- LanguageISO whitelist + alias: full ISO 639-1 whitelist (184 codes) plus common aliases `jp→ja` / `cn→zh` / `zhtw→zh`
- Year strict date parsing: prefers full date fields; ranges/multi-values (`2001-2005`) return None
- `emit` warning now visible under `--quiet`
- EXTH loop variable `t` renamed to `type_id` to avoid shadowing the global `t()`
- Regex img src extraction now applies `unquote`, consistent with the HtmlImgParser fallback path
- `--language` tolerance: accepts common spellings like `zh`/`cn`/`zhtw`/`jp` via new `_normalize_lang` (argparse `choices` restriction removed)

## [2.0.1] - 2026-08-17

### Fixed

- Fixed `infer_series_number` incorrectly inferring a series name from volume-marker-only filenames (`Vol.01` / `Volume 01` / `01巻` etc.); added the `_is_volume_marker` volume-marker filter

## [2.0.0] - 2026-08-14

### Added

- Generates ComicInfo.xml by default (written into the CBZ ZIP root, UTF-8 with XML declaration); new `--no-comicinfo` flag disables it
- New functions: `build_comicinfo` (built with `xml.etree.ElementTree`, no manual string concatenation), `write_comicinfo`, `normalize_language` (normalizes language codes to ISO 639-1), `infer_series_number` (high-confidence Series/Number inference from the filename, supporting `001`/`01`/`1`/`Vol.01`/`Vol 01`/`Volume 01`/`第 01 卷` forms; returns None when confidence is insufficient — better missing than wrong)
- Field mapping: Title=OPF title→EXTH title→filename stem, Writer=OPF creator→EXTH author, Publisher=OPF publisher→EXTH publisher, Year=PublicationDate year, LanguageISO=the ebook's own language (not guessed from the filename), PageCount=the actual image count written into the CBZ (always written), Series/Number=high-confidence filename inference, Summary=OPF description (written only when present); fields without a reliable source are omitted (no empty tags)
- Flow insertion: ComicInfo is built after the final image set is determined, then written into the CBZ together with the images; integrity verification adds 3 checks (ComicInfo.xml exists, parseable by a standard XML parser, root node is ComicInfo); ComicInfo generation or verification failure = the whole conversion fails, and `--delete` must not delete the source file
- `--dry-run` does not create ComicInfo.xml but prints one line indicating whether ComicInfo is enabled
- `--inspect` output gains a ComicInfo preview block (Title/Series/Number/Writer/Publisher/Year/LanguageISO/PageCount/Summary shown only when present), with inferred fields clearly marked `[inferred]`
- i18n: 6 new keys across all four languages: `comicinfo.generating` / `comicinfo.created` / `comicinfo.disabled` / `comicinfo.invalid` / `comicinfo.inferred` / `help.no_comicinfo`

## [1.9.1] - 2026-08-14

### Added

- `--inspect-all` used alone (without `--inspect`) now auto-enables `--inspect` and prints a warning (new key `warn.inspect_all_auto_enable` in all four languages)
- `--inspect` help updated: a single-file positional argument inspects that file directly; a directory samples 1 ebook randomly
- `--inspect-all` help updated: requires `--inspect`; using it alone will auto-enable `--inspect`

## [1.9.0] - 2026-08-14

### Breaking Change

- `--output-dir DIR` changed from "flatten everything into DIR" to "**preserve the relative subdirectory structure of the input by default**" (e.g. `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`)
- Migration: the old command `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output` must be changed to `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output --flatten` to restore the "flatten" behavior

### Added

- `--flatten`: only used together with `--output-dir`; flattens all CBZ files into the output directory root; flat naming rules: file directly under the input root → `stem`, in a subdirectory → `parent dir name - stem`; illegal filename characters (`<>:"/\|?*`) are replaced with `_`
- Automatic conflict uniquification in flat mode: `base.cbz` → `base (2).cbz` → `base (3).cbz` …, never silently overwrites or skips; an info message is printed when numbering occurs
- Using `--flatten` without `--output-dir` exits with an error (exit 2); the message is i18n-ized
- Prints one output-mode line per run (preserve structure / flatten); four language tables gain keys `output.mode_preserve` / `output.mode_flatten` / `output.renamed_due_to_conflict` / `output.flatten_requires_dir` / `error.flatten_without_output_dir` / `rel_fallback`
- If computing the relative subdirectory path fails (e.g. across drives), falls back to `DIR/stem.cbz` with a warning
- Single-file input + `--output-dir` outputs `DIR/stem.cbz` (no subdirectory wrapping)
- `--overwrite` semantics unchanged in preserve mode; in flat mode uniquification is preferred, and `--overwrite` still applies to the final chosen path

### Refactored

- `target_cbz_path` gains `flatten` / `input_root` / `used_names` parameters; new standalone helpers `sanitize_filename_component` / `flat_base_name` / `unique_path`
- dry-run flat uniquification maintains a used-name set in processing order, consistent with real runs

### Fixes & Enhancements (folded into v1.9.0, no version bump)

- `run_with_timeout` now returns a `(timed_out, result)` tuple: timeout → `(True, None)`, normal → `(False, function return value)`, removing the ambiguity between "timeout" and a normal `None` return
- `--inspect` timeout branch adds a hint that the extracted temp directory may be left behind and should be cleaned up manually (new key `inspect_mode.timeout_residue` in all four languages)
- Packing-stage `seen` now also uses normalized paths to detect physically duplicate files: the same physical file appearing more than once is skipped (same-name different files still get numeric prefixes), and a dedup count is printed (new key `convert.dedup_physical`)
- New `HtmlImgParser` (an `HTMLParser` subclass) fallback for extracting `<img src>`: HTML entities are auto-decoded by HTMLParser plus `unquote` for `%XX`; wired into OPF/spine HTML image extraction, enabled only when the regex misses; the ElementTree main flow is untouched
- `--dry-run` now checks whether the output directory (`--output-dir` or each source file's directory) is writable and warns when it is not (new key `dryrun.output_not_writable`)

## [1.8.0] - 2026-08-14

### Added

- Lightweight i18n: `--language auto|zh-CN|zh-TW|ja|en` (default `auto` detects by system locale: Simplified → zh-CN, Traditional zh-TW/zh-Hant → zh-TW, Japanese ja/Japanese → ja, non-zh/ja → en); all output text and `--help` are translated with the language (`--help` is implemented by pre-parsing `--language` before building the parser); missing keys fall back en → key name without raising; business code never writes `if lang` branches; parameter names/enums/book metadata/OPF/DRM/spine and other technical terms are not translated; all `TAG_*` constants are removed and replaced with `t()` keys
- `.azw` / `.azw3` input support: accepted input extensions expanded to `.mobi` / `.azw` / `.azw3` (case-insensitive), all three reusing the same `extract → OPF/spine → cover → align → pack → verify` pipeline, no parallel implementations
- `--ext-priority EXTS`: which format to keep when files share the same name in the same directory (differing only by extension) — comma-separated, order = priority high→low, accepts only `mobi`/`azw`/`azw3`, default `azw3`; groups not covered by the priority fall back to azw3→mobi→azw with a warning; completely unrelated to `--prefer` (dual-directory mobi7/mobi8 selection)
- Same-name extension deduplication: only one file kept per same directory + same stem (group key `parent.resolve() + stem.lower()`); same-name files in different directories are not deduplicated; dedup happens before path computation and progress counting, skip reason is logged
- Magic-bytes precheck extended to all three formats: unified `BOOKMOBI` magic check at offset 60; files with the right extension but wrong magic (or anomalous `.azw/.azw3` magic) are no longer directly judged corrupt and skipped — a warning is printed and extraction is still attempted (`mobi.extract` has its own secondary validation; unpack failures are counted as failures normally)
- `--delete` and `--inspect` / `--inspect-all` support `.mobi` / `.azw` / `.azw3` uniformly
- Per-file progress bar: `--progress` forces it on, `--no-progress` forces it off; automatic by default (shown when stderr is TTY and file count ≥ 2, off when not TTY); when both are passed, the last one wins; kept by default under `--quiet`, closed by `--no-progress`; covers convert / inspect / dry-run modes; total strictly equals the final post-dedup list length, showing current/total, percentage, ETA, average time, and current filename (truncated to 40 chars); writes to stderr, not into emit/`--log`; tqdm is optional, degrading to a simple text progress without crashing when missing

### Refactored

- `collect_mobi_files` renamed to `collect_ebook_files` (old alias `collect_mobi_files` kept for compatibility); `precheck_mobi` → `precheck_ebook`, `mobi_to_cbz` → `ebook_to_cbz`, `inspect_mobi` → `inspect_ebook`
- Input extension set constantized as `SUPPORTED_INPUT_EXTENSIONS`; `PREFER_EXT_ORDER` renamed to `KEEP_EXT_ORDER`
- docstring, CLI help, and runtime log wording unified to "ebook" (mobi file → ebook); help description changed to `mobi/azw/azw3 manga batch to cbz`

### Code hygiene & UX polish (bundled into [1.8.0])

- Removed the duplicate `from concurrent.futures import ThreadPoolExecutor` import
- `LANGUAGES` dict gets functional-section Chinese comments (【预处理】【转换】【检查】【汇总】, including help/progress/tag sections)
- `--language auto` prints an INFO-level "detected language: X" message (suppressed under `--quiet`, via `emit` + `t()`)
- Magic-bytes check downgrade: `precheck_ebook` magic failure changed from "judge corrupt and skip" to a warning + still attempting extraction (`extract` has its own secondary validation; unpack failures count as failed)
- `--ext-priority` invalid-value error message i18n-ized (new `error.ext_priority_empty` / `error.ext_priority_invalid` keys in all four language tables)
- Chinese comments added to argparse parameter definitions and main function input parameters (describing input and output)

## [1.7.0] - 2026-08-13

### Added

- `--compress LEVEL`: zip compression level 0-9, `0` = no compression (default, images already compressed), `1-9` = deflate; PNG sources can shrink significantly, higher = smaller but slower; JPEG sources benefit little, not recommended
- `--inspect` inspect mode: randomly samples 1 mobi (`--inspect-all` for all), unpacking only to read internal info without producing CBZ, temp directory cleaned up automatically afterwards; outputs basic checks (magic/size/DRM marker), EXTH metadata (title/author/language/publish date/publisher/ISBN, shown only when found), dual-directory markers, OPF and spine extraction counts, total image count, cover, image format distribution, dominant resolution (dominant height/width + range of the other dimension), compression advice; suspected DRM (no images) and unpack timeouts counted separately
- `--inspect` enhancements: cover detection prefers the OPF guide `type="cover"` official reference (falls back to filename matching); vertical preview of first 5 spine-extracted filenames; NCX (toc.ncx) entry count + preview of first 3 titles; EXTH metadata adds ASIN(type113) and copyright(type109); dual DRM judgment (header marker present → judged DRM and skips unpacking; no marker + 0 unpacked images → suspected; no marker + images → none), summary line adds DRM-marker count

### Refactored

- Packing branch refactored: `compress>0` uses `ZIP_DEFLATED`+`compresslevel`, otherwise `ZIP_STORED`, eliminating the deprecation warning from old Python passing `compresslevel=None` under STORED
- `--inspect` dual-directory selection unified through the shared `select_mobi_dir` function (new prefer parameter controlled by `--prefer`) instead of hand-written logic; output indentation unified to 2 spaces, fixed inconsistent OPF line indentation

## [1.6.0] - 2026-08-13

### Added

- `--output-dir DIR`: CBZ output to a specified directory (auto-created), no longer forced into the source mobi's directory; `--overwrite` existence check also based on the output directory
- Precheck filtering: 0-byte files and files failing header validation (no `BOOKMOBI` magic at offset 60, suspected corrupt or not mobi) are skipped directly, with full path and reason logged
- `--dry-run` dry-run mode: only scans and prechecks, prints each file's conversion flow and target output path, without unpacking/packing, creating output directories, or any disk writes, and prints the precheck filter list too (consistent with real runs)
- `--min-size BYTES`: filters out mobi smaller than the given bytes (default 1000 without a number, `0` disables, not passing it disables size filtering), catching edge-corrupt samples whose header is intact but content is truncated; precheck also adds an "unable to read file (OSError)" skip-reason branch
- Elapsed-time stats: per-file conversion time printed in real time, total elapsed time at the bottom of the summary (success/fail/skip all counted)
- Summary adds a one-line conversion stats row (success/skip/fail counts, including 0): when a category is 0, its detail lines are not printed, but the stats row always shows all three counts

### Refactored

- Magic-string statuses refactored into the `ConvStatus` enum (`OK`/`SKIP`/`FAIL`); `mobi_to_cbz` return type changed to `tuple[Path | None, ConvStatus]`; main-loop branches and return sites use enum members uniformly to avoid typos
- Output labels extracted into constants (`TAG_INFO`/`TAG_FAIL`/`TAG_ERROR`/`TAG_SKIP`/`TAG_OVERWRITE`/`TAG_CLEAN`/`TAG_SORT`/`TAG_DEDUP`/`TAG_DONE`/`TAG_VERIFY`/`TAG_VERIFY_FAIL`/`TAG_TIMEOUT`/`TAG_ELAPSED`/`TAG_FILE`/`TAG_PENDING`/`TAG_WILL_SKIP`/`TAG_DRYRUN`) for centralized output styling
- Added comments to `run_with_timeout` on thread limits: after timeout, `mobi.extract` worker threads linger in the background consuming memory/IO; batch-processing many corrupt files may accumulate zombie threads; `multiprocessing` could be adopted later for terminable child processes but adds cross-platform complexity and has not been used yet
- Top-level global exception capture: `main()` wraps everything in `try/except`; uncaught exceptions and Ctrl+C outside the main loop (argument parsing/file collection) are printed with stack trace via `emit` to console and log (with timestamp) instead of a bare stack trace exit
- `--short-summary` compact summary: succeeded/skipped/precheck-skipped files show counts only (failed files always list full paths), unaffected by dry-run, complementary to `--quiet`

## [1.5.0] - 2026-08-13

### Added

- `--timeout` per-file timeout protection: default 600 seconds; when a corrupt/encrypted/oversized mobi blocks the underlying `mobi.extract()` indefinitely, the file is skipped automatically and counted as failed instead of stalling the whole batch; `0` means no limit
- Path case compatibility: cover comparison and directory alignment use normalized lowercase paths, so case-only naming differences are not misjudged as duplicates/missing on case-insensitive Windows filesystems
- Output timestamps: every output line (console and `--log` file) is prefixed with `[YYYY-MM-DD HH:MM:SS]`, making it easy to pinpoint when each conversion ran

### Changed

- Log write tolerance: `--log` write failures (invalid chars/overlong paths, disk full, read-only partition, file locked) no longer swallow exceptions silently; all `Exception`s are caught and a single warning is printed so users don't mistakenly believe the log was saved
- Ctrl+C interruption fallback: pressing Ctrl+C mid-batch no longer exits with a raw exception; the main loop catches `KeyboardInterrupt` and force-prints the progress summary of completed/failed files
- Summary completes the skip list: files skipped because the target cbz already exists (when `--overwrite` is off) are counted in "skipped files" and listed with full paths
- `--overwrite` regeneration marker keeps only the per-file `[overwrite]` log line, not in the final summary (written to the `--log` file)
- Removed the ineffective outer `TemporaryDirectory` fallback: extraction temp dirs are still cleaned uniformly by `extract_temp_paths` + `finally`

## [1.4.0] - 2026-08-13

### Added

- Dependency check moved to the top of the module, validated at startup
- DRM encryption detection: when unpacking fails or no images are extracted, clearly reports the file may be DRM-encrypted Kindle manga that the mobi library cannot decrypt, avoiding silent failure
- `--overwrite` parameter: force regeneration when the target cbz already exists, no need to manually delete old cbz after updating manga
- `--quiet` quiet mode: only errors and the final summary, no screen flooding during batch conversion
- `--log FILE`: append all output to the specified log file
- Lists full paths of pending mobi files before conversion starts, and full paths of output cbz files after conversion completes
- Lists failed file count and full paths after conversion (files skipped because they already exist are not counted as failures)

### Fixed

- Fixed temp-directory residue: `mobi.extract` does not support the `output_dir` parameter, changed to pass only the input file and record the extraction path it generates, cleaned uniformly in `finally` — no residue on normal/Ctrl+C/exception paths

## [1.3.0] - 2026-08-13

### Added

- Cover fallback: after spine extraction, automatically scans for images whose filenames contain cover/front; if the cover is already in the list, the list order wins; only inserted at the front when missing
- Fixed page loss when the cover is only defined by the OPF metadata meta and not referenced by the spine (e.g. `cover00198.jpeg`)
- Directory alignment fallback: when the image count differs from the collected count, extra images are appended to the end of the cbz in natural order by default; `--drop-extra` switches to dropping them, and the outcome is printed

## [1.2.0] - 2026-08-13

### Added

- OPF spine order image extraction: parses manifest and spine itemref, ordering by the real reading order
- `--version` parameter, `python manga-mobi2cbz.py --version` shows the version
- `select_mobi_dir` directory selection logic, preferring mobi7/mobi8 directory before extracting images
- Tiered sort fallback: falls back to natural filename sorting automatically when spine extraction is empty / OPF not found

### Changed

- Duplicate image names get a sequence prefix (`{idx:04d}_`) to guarantee order and avoid collisions
- Script renamed to `manga-mobi2cbz.py`

## [1.1.0] - 2026-08-13

### Added

- Version mechanism: `__version__` and `SCRIPT_NAME` constants

## [1.0.0] - 2026-08-12

### Added

- First usable version: recursive mobi collection, batch cbz conversion, dual-directory deduplication, EOCD + testzip integrity verification, cleanup of failed half-products

