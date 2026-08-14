**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md)

# manga-mobi2cbz

Kindle 漫画向けの一括変換 CLI ツールです。ワンコマンドで DRM フリーの MOBI / AZW / AZW3 電子書籍を標準 CBZ コミックパッケージに書き出します。
OPF spine の標準的な読み順に従って画像を抽出し、表紙の自動補完、同一巻の複数形式の重複排除、バッチのタイムアウト保護、ファイル完全性の検証、多言語出力などの実用機能を備えています。パッケージ化せずにメタデータ・解像度・NCX 目次・DRM 状態を確認できる `--inspect` 検査モードも付属し、全プラットフォームで漫画ライブラリの一括整理を安定して効率化します。

> ⚠️ 重要な制限: DRM 解除済みの Kindle 漫画のみ対応します。ストアで購入した暗号化電子書籍は解析できません。
>
> ⚠️ リスク注意: 本プロジェクトは AI 生成です。ご利用は自己責任でお願いします。
>
> 📝 備考: 個人利用を目的としたプロジェクトで、ファイル変換時に AI が生成したスクリプトを後から使えるように保存しています。

## 機能

- **一括変換** — 単一ファイル、またはディレクトリ全体を再帰的に変換（`.mobi` / `.azw` / `.azw3`）
- **OPF spine 順** — OPF spine の順序で画像を抽出し、実際の読み順を保ちます。OPF が無い場合はファイル名の自然順ソートにフォールバックします
- **表紙フォールバック** — ファイル名に cover/front を含む画像を自動スキャンします。表紙がすでに spine リスト内にあればリスト順を優先し、欠落時のみ先頭に補完します
- **ディレクトリ整合フォールバック** — ディレクトリ内の画像数が収集数と一致しない場合、余分な画像はデフォルトで自然順に cbz 末尾へ追記します。`--drop-extra` で破棄に変更でき、処理結果は出力されます
- **二重ディレクトリの重複排除** — mobi7/mobi8 の二重ディレクトリを自動検出し、デフォルトで mobi8 を保持します（画質が良い場合があります）。切替可能です
- **軽量多言語対応** — `--language auto|zh-CN|zh-TW|ja|en` で出力言語を切り替えます（デフォルト `auto` はシステム locale で自動判定: 簡体字中国語→zh-CN、繁体字中国語→zh-TW、日本語→ja、その他→en）。
- 実行時のメッセージと `--help` は選択言語に追従します。CLI のフラグ名、列挙値、技術用語（OPF / DRM / spine など）は翻訳しません
- **同名拡張子の重複排除** — 同じディレクトリ内で拡張子だけ異なるファイル（例: `Vol1.mobi` + `Vol1.azw3`）は 1 つだけ保持します。`--ext-priority` で保持優先度を制御します（デフォルト azw3）
- **自然順ソート** — ページ番号で自然順に並べ、`10.jpg` が `2.jpg` より前に来るのを防ぎます
- **完全性検証** — 変換後に CBZ を自動検証し、破損時は削除して通知します
- **無圧縮パッケージ** — 画像は既に圧縮済みのため、ZIP はデフォルトで store のみです。高速でサイズも抑えられます
- **任意圧縮** — `--compress LEVEL` で deflate 圧縮（1–9）を有効化できます。PNG ソースではサイズを大きく削減できることがあります。レベルが高いほど小さくなりますが遅くなります。JPEG ソースは効果が限定的で推奨しません（デフォルト `0` = 無圧縮）
- **検査モード** — `--inspect` で電子書籍を 1 冊ランダム抽出（`--inspect-all` で全冊）します。CBZ は作らず解凍して内部情報のみ読み取り、終了後に一時ディレクトリを削除します
- 基本検査（マジックバイト / サイズ / DRM）、見つかった場合の EXTH メタデータ、mobi7/mobi8 マーカー、OPF/spine の件数（先頭 5 ファイル名）、NCX のプレビュー、画像総数、表紙検出、形式分布、主流解像度、圧縮の目安などを表示します
- DRM の扱い: ヘッダーにフラグあり→DRM として解凍をスキップ / フラグなしで画像 0→疑い / フラグなしで画像あり→DRM なし
- **元ファイルの任意削除** — `--delete` で変換成功後に元の電子書籍を自動削除します
- **強制上書き** — `--overwrite` で既存の cbz を強制再生成します。漫画を更新しても古いファイルを手動削除する必要はありません
- **単一ファイルのタイムアウト保護** — `--timeout` で 1 ファイルあたりの変換時間を制限します。破損・暗号化・巨大ファイルが下層の解凍をブロックしても、自動スキップして失敗として計上し、バッチ全体が止まりません（デフォルト 600 秒、`0` は無制限）
- **サイレントモード** — `--quiet` で一括変換時にエラーと集計のみ表示します。`--log FILE` で全出力をログファイルに追記できます
- **簡潔な集計** — `--short-summary` で成功 / スキップ / 事前チェックスキップは件数のみ表示します（失敗は常にフルパス）。`--quiet` と組み合わせると大規模ディレクトリ向きです
- **DRM 暗号化の検出** — DRM 付き Kindle 漫画に遭遇した場合、黙って失敗せず復号できない旨を明示します
- **パスの大文字小文字対応** — 表紙比較とディレクトリ整合に正規化（小文字）パスを使い、大文字小文字を区別しない Windows 上でも誤判定しにくくします
- **出力タイムスタンプ** — 各行に `[YYYY-MM-DD HH:MM:SS]` を付与し、コンソールとログで統一します
- **カスタム出力ディレクトリ** — `--output-dir DIR` で CBZ を指定ディレクトリへ出力します（自動作成）。デフォルトでは入力の相対サブディレクトリ構造を保持します（例: `One Piece/001.mobi` → `DIR/One Piece/001.cbz`）。`--flatten` を付けると出力ルートへフラット化し、衝突時は自動で `base (2).cbz` のように番号付けします
- **事前チェックフィルタ** — 0 バイトやヘッダ破損（オフセット 60 に `BOOKMOBI` なし）のファイルは事前チェックでスキップし、フルパスと理由をログに出します
- **最小サイズフィルタ** — `--min-size BYTES` で指定バイト未満を除外します（数値省略時デフォルト 1000、`0` で無効、未指定でサイズフィルタオフ）
- **ドライラン** — `--dry-run` は変換フローの表示のみで、実際の解凍・パッケージ化は行いません
- **所要時間** — ファイルごとの変換時間をリアルタイム表示し、集計下部に合計を出します

## 対応画像形式

変換時に認識・パッケージ化する形式: `.jpg` / `.jpeg` / `.png` / `.gif` / `.webp` / `.bmp` / `.tiff` / `.tif`

## 環境要件

- Python 3.10+
- 依存: `mobi`

## インストール

```bash
pip install mobi
```

## 使い方

### 単一ファイルを変換

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi"
```

### ディレクトリ全体を一括変換（.mobi / .azw / .azw3 を再帰検索）

```bash
python manga-mobi2cbz.py "D:\Manga"
```

### 変換成功後に元の電子書籍を削除

```bash
python manga-mobi2cbz.py "D:\Manga" --delete
```

### 二重ディレクトリ mobi で mobi7 を保持

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --prefer mobi7
```

### ディレクトリ内の未収集の余分な画像を破棄

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --drop-extra
```

### 既存の cbz がある場合に強制再生成

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --overwrite
```

### 単一ファイル変換のタイムアウトを制限（破損ファイルによるバッチ停止を防止）

```bash
python manga-mobi2cbz.py "D:\Manga" --timeout 300
```

### カスタムディレクトリへ出力（デフォルトで相対サブディレクトリ構造を保持）

```bash
python manga-mobi2cbz.py "D:\Manga" --output-dir "E:\CBZ"
```

### フラット出力（すべての CBZ を出力ディレクトリ直下へ）

```bash
python manga-mobi2cbz.py "D:\Manga" --output-dir "E:\CBZ" --flatten
```

### ドライラン: 変換フローを表示するのみ（実際には変換しない）

```bash
python manga-mobi2cbz.py "D:\Manga" --dry-run
```

### サイレントモード + ログへ書き込み

```bash
python manga-mobi2cbz.py "D:\Manga" --quiet --log convert.log
```

### 簡潔な集計（大規模ディレクトリ、成功/スキップは件数のみ）

```bash
python manga-mobi2cbz.py "D:\Manga" --quiet --short-summary --log convert.log
```

### zip 圧縮を有効化（PNG ソースでサイズ削減しやすい）

```bash
python manga-mobi2cbz.py "D:\Manga" --compress 9
```

### 検査モード: 1 冊の内部情報をランダム確認

```bash
python manga-mobi2cbz.py "D:\Manga" --inspect
```

### 全電子書籍の内部情報を検査

```bash
python manga-mobi2cbz.py "D:\Manga" --inspect --inspect-all
```

### バージョン確認

```bash
python manga-mobi2cbz.py --version
```

## パラメータ説明

| パラメータ | 説明 |
| --- | --- |
| `target` | 電子書籍ファイルのパス、または `.mobi` / `.azw` / `.azw3` を含むディレクトリ（必須） |
| `--language LANG` | 出力言語。`auto` はシステム locale で自動選択（簡体字→zh-CN、繁体字 zh-TW/zh-Hant→zh-TW、日本語 ja/Japanese→ja、その他→en）。または `zh-CN` / `zh-TW` / `ja` / `en` を指定（デフォルト `auto`） |
| `--delete` | 変換成功後に元の電子書籍を削除（デフォルト: 削除しない） |
| `--prefer` | 二重ディレクトリ mobi で保持する側: `mobi7` または `mobi8`（デフォルト `mobi8`） |
| `--drop-extra` | 未収集の余分な画像を破棄（デフォルト: cbz 末尾に追記） |
| `--overwrite` | 対象 cbz が既にある場合に強制再生成（デフォルト: スキップ） |
| `--ext-priority EXTS` | 同一ディレクトリ・同名（拡張子のみ異なる）とき保持する形式。カンマ区切りで優先度が高い順。受け付ける値は `mobi` / `azw` / `azw3` のみ。デフォルト `azw3`。未指定分は azw3→mobi→azw にフォールバック。`--prefer`（mobi7/mobi8）とは無関係 |
| `--timeout` | 1 ファイルあたりのタイムアウト秒数。超過分はスキップして失敗計上（デフォルト 600、`0` は無制限） |
| `--min-size BYTES` | 指定バイト未満を除外。数値省略時は 1000、`0` で無効、オプション未指定でサイズフィルタオフ |
| `--output-dir DIR` | CBZ の出力先（自動作成）。デフォルトで入力の相対サブディレクトリ構造を保持（例: `One Piece/001.mobi` → `DIR/One Piece/001.cbz`）。`--flatten` でルート直下にフラット化 |
| `--flatten` | `--output-dir` と併用時のみ有効。すべての CBZ を出力ルート直下へフラット化し、衝突時は `base (2).cbz` と自動番号。単独指定（`--output-dir` なし）はエラー終了 |
| `--progress` | ファイル単位のプログレスバーを強制表示。デフォルトは stderr が TTY かつファイル数≥2 で自動表示。`--no-progress` と同時指定時は後に書いた方が有効。`--quiet` 下でもデフォルトは表示。stderr のみで `--log` には入らない |
| `--no-progress` | プログレスバーを強制オフ |
| `--dry-run` | スキャンと変換フロー表示のみ。解凍・パッケージ化・出力ディレクトリ作成はしない |
| `--quiet` | エラーと最終集計のみ表示 |
| `--short-summary` | 成功/スキップは件数のみ（失敗は常にフルパス） |
| `--compress LEVEL` | zip 圧縮レベル 0–9。`0`=無圧縮（デフォルト）、`1–9`=deflate（PNG 向け。高いほど小さいが遅い） |
| `--inspect` | 1 冊をランダム抽出し、内部情報のみ読取（CBZ 非生成、一時ディレクトリは終了時に削除） |
| `--inspect-all` | 全冊を検査（`--inspect` と併用が必要） |
| `--log FILE` | 全出力を指定ログへ追記 |
| `--version` | バージョン番号を表示 |

## 出力

- デフォルトでは `.cbz` は元の電子書籍と同じディレクトリに置きます。`--output-dir` 指定時はそのディレクトリへ出力します（自動作成）。デフォルトで入力の相対サブディレクトリ構造を保持し、`--flatten` でルート直下にフラット化します（衝突時は自動番号）
- 既存の `.cbz` はデフォルトでスキップし、上書きしません。`--overwrite` で強制再生成できます
- 0 バイト / ヘッダ破損は事前チェックでスキップし、フルパスと理由をログに出します
- ファイルごとの所要時間をリアルタイム表示し、集計下部に合計を出します
- 失敗したファイルはエラーを表示しますが、他ファイルの変換は継続します

## 既知の制限

- **DRM 暗号化ファイルには非対応** — 下層の mobi ライブラリは Kindle ストアの DRM 付き漫画を復号できません。該当ファイルは「DRM の可能性あり」と明示してスキップし、空の cbz を黙って作りません。変換前に DRM を解除してください
- **ComicInfo.xml は生成しない** — 画像のパッケージ化のみ行い、シリーズ名・著者・タグ等の ComicInfo.xml は含みません。必要なら別途注入してください
- **タイムアウト後のスレッドは強制終了できない** — `--timeout` 超過後、メイン処理はそのファイルをスキップして続行しますが、Python はブロック中の解凍スレッドを kill できません。残ったスレッドはプロセス終了までメモリ/IO を使うことがあり、破損ファイルが多いとバックグラウンドに積み上がる可能性があります。完全隔離には `multiprocessing` などが考えられますが、クロスプラットフォームの複雑さのため未採用です

## よくある質問

**Q: 変換後の CBZ で画像の順序が乱れるのは？**  
A: まず OPF spine 順（EPUB の標準的な読み順）で抽出するため、多くの場合は正しい順序になります。OPF が無い、または spine が空のときはファイル名の自然順にフォールバックします。それでもおかしい場合は、元ファイル内の画像名が不統一な可能性があります。ソースを確認してください。

**Q: CBZ に表紙が無いのはなぜ？**  
A: 一部のファイルでは表紙が OPF の cover メタのみで指され、spine から参照されないため漏れます。スクリプトは cover/front を含むファイル名を探し、無ければ先頭に補完します。すでに spine にあれば元の順を保ちます。キーワードの無いファイル名だと漏れることがあるので、リネームして再変換してください。

**Q: 変換後のサイズが極端に小さいのはなぜ？**  
A: mobi7+mobi8 の二重構成ではデフォルトで mobi8 のみ残し、内容の二重化を避けています。mobi7 が必要なら `--prefer mobi7` を指定してください。

**Q: 一括変換中に破損/暗号化ファイルで止まったように見える？**  
A: 1 ファイルあたりデフォルト 600 秒のタイムアウトがあります（`--timeout` で変更可）。超過分はスキップして失敗計上し、残りを続行します。早く切りたいときは `--timeout 30` など短くするか、`--quiet` で出力を減らしてください。

**Q: --output-dir でサブディレクトリが残るのはなぜ？**
A: v1.9.0 以降、`--output-dir` はデフォルトで入力の相対サブディレクトリ構造を保持します（旧版の一律フラットから破壊的変更）。フラット化したい場合は `--flatten` を追加してください。旧コマンド `python manga-mobi2cbz.py Manga --output-dir CBZ` は `python manga-mobi2cbz.py Manga --output-dir CBZ --flatten` に変更すると旧動作を復元できます。

**Q: .azw / .azw3 には対応していますか？**  
A: 対応しています。v1.8.0 以降、入力は `.mobi` / `.azw` / `.azw3` で、同じ変換パイプラインを使います。同一ディレクトリで同名・異拡張子のときはデフォルトで azw3 を残し、`--ext-priority` で変更できます。

## 更新履歴

### [1.9.0] - 2026-08-14

#### 破壊的変更（Breaking Change）

- `--output-dir DIR` を「DIR へ一律フラット」から「**デフォルトで入力の相対サブディレクトリ構造を保持**」に変更（例: `One Piece/001.mobi` → `DIR/One Piece/001.cbz`）
- 移行方法: 旧コマンド `python manga-mobi2cbz.py Manga --output-dir CBZ` は `python manga-mobi2cbz.py Manga --output-dir CBZ --flatten` に変更すると「フラット」動作を復元できます

#### 追加

- `--flatten`: `--output-dir` と併用時のみ有効。すべての CBZ を出力ルート直下へフラット化。命名規則: 入力直下 → `stem`、サブディレクトリ → `親ディレクトリ名 - stem`。不正なファイル名文字（`<>:"/\|?*`）は `_` に置換
- フラット時の衝突自動一意化: `base.cbz` → `base (2).cbz` → `base (3).cbz` …。黙って上書きせずスキップもせず、番号付け時に info を出力
- `--flatten` 単独指定（`--output-dir` なし）はエラー終了（exit 2）。メッセージは多言語化
- 実行ごとに出力モード（構造保持 / フラット）を 1 回表示。4 言語テーブルに `output.mode_preserve` / `output.mode_flatten` / `output.renamed_due_to_conflict` / `output.flatten_requires_dir` / `error.flatten_without_output_dir` / `rel_fallback` キーを追加
- 相対パス計算に失敗した場合（ドライブ跨ぎなど）は `DIR/stem.cbz` にフォールバックし warning を出力
- 単一ファイル入力 + `--output-dir` は `DIR/stem.cbz` へ出力（サブディレクトリなし）
- 構造保持時の `--overwrite` は従来どおり。フラット時は一意化を優先し、`--overwrite` は最終的に選ばれたパスのみに作用

#### リファクタリング

- `target_cbz_path` に `flatten` / `input_root` / `used_names` 引数を追加。`sanitize_filename_component` / `flat_base_name` / `unique_path` を独立関数化
- dry-run のフラット一意化は処理順に使用済み名を管理し、実実行と一致

#### 修正と強化（v1.9.0 に統合、バージョン据え置き）

- `run_with_timeout` の戻り値を `(timed_out, result)` タプルに変更: タイムアウト → `(True, None)`、正常 → `(False, 関数の戻り値)`。「タイムアウト」と「正常に None を返した」の曖昧さを解消
- `--inspect` のタイムアウト時に「展開された一時ディレクトリが残っている可能性があるため、手動でクリーンアップしてください」というヒントを追加（4 言語テーブルに `inspect_mode.timeout_residue` キーを追加）
- パッキング時に `seen` が正規化パスでも物理重複を判定: 同じ物理ファイルが複数回出現したらスキップ（同名別ファイルは従来どおり連番プレフィックス）、重複スキップ数を出力（4 言語に `convert.dedup_physical` キーを追加）
- `HtmlImgParser`（HTMLParser のサブクラス）を追加し `<img src>` 抽出のフォールバックに: HTML エンティティは HTMLParser が自動デコード、`%XX` は `unquote` で処理。OPF/spine の HTML 画像抽出に接続し、正規表現がヒットしないときのみ使用。ElementTree のメインフローには影響なし
- `--dry-run` で出力ディレクトリ（`--output-dir` または各ソースファイルの所在ディレクトリ）の書き込み可否を確認し、書き込み不可なら warning を出力（4 言語に `dryrun.output_not_writable` キーを追加）

### [1.8.0] - 2026-08-14

#### 追加

- 軽量多言語: `--language auto|zh-CN|zh-TW|ja|en`（デフォルト `auto` は locale で判定: 簡体字→zh-CN、繁体字 zh-TW/zh-Hant→zh-TW、日本語→ja、それ以外→en）。出力文面と `--help` を言語に追従（`--help` は `--language` を先に読んでから parser を構築）。キー欠落時は en→キー名へフォールバックし例外にしない。業務コードに `if lang` 分岐は置かない。フラグ名 / 列挙 / 書籍 metadata / OPF / DRM / spine などは翻訳しない。`TAG_*` を廃止して `t()` キーに統一
- `.azw` / `.azw3` 入力: 拡張子を `.mobi` / `.azw` / `.azw3`（大文字小文字無視）に拡大。共通パイプライン `extract → OPF/spine → 表紙 → 整合 → パッケージ → 検証` を再利用し、形式ごとの別実装は持たない
- `--ext-priority EXTS`: 同一ディレクトリ・同名（拡張子のみ違う）ときの保持形式。カンマ区切り・左が高優先。`mobi` / `azw` / `azw3` のみ。デフォルト `azw3`。未指定分は azw3→mobi→azw にフォールバックして warning。`--prefer`（mobi7/mobi8）とは無関係
- 同名拡張子の重複排除: グループキーは `parent.resolve() + stem.lower()`。別ディレクトリの同名は対象外。パス計算・プログレス計数より前に実行し、スキップ理由をログ出力
- マジックバイト事前チェックを 3 形式に拡大。オフセット 60 の `BOOKMOBI` を確認。拡張子は合っているがマジックがおかしい場合は「即破損スキップ」ではなく warning のうえ解凍を試行（`mobi.extract` 側の検証あり。失敗は失敗リストへ）
- `--delete` と `--inspect` / `--inspect-all` を 3 形式で統一
- ファイル単位プログレスバー: `--progress` / `--no-progress`。TTY かつ件数≥2 で自動表示、非 TTY はオフ。両方指定時は後勝ち。`--quiet` 下でもデフォルト表示。convert / inspect / dry-run 対応。total は重複排除後の件数。stderr のみ（`--log` 非対象）。tqdm は任意依存、無ければテキスト表示にフォールバック

#### リファクタリング

- `collect_mobi_files` → `collect_ebook_files`（旧名エイリアス維持）。`precheck_mobi` → `precheck_ebook`、`mobi_to_cbz` → `ebook_to_cbz`、`inspect_mobi` → `inspect_ebook`
- `SUPPORTED_INPUT_EXTENSIONS` を定数化。`PREFER_EXT_ORDER` → `KEEP_EXT_ORDER`
- ドキュメント・ヘルプ・ログの呼び方を「電子書籍」に寄せ、ヘルプ説明を mobi/azw/azw3 の一括 cbz 変換向けに更新

#### コード衛生・体験改善（[1.8.0] に統合）

- 重複していた `ThreadPoolExecutor` の import を削除
- `LANGUAGES` 辞書に機能別セクションコメントを追加（前処理 / 変換 / 検査 / 集計、help・progress・tag など）
- `--language auto` 時に INFO で検出言語を表示（`--quiet` 時は抑制。`emit` + `t()`）
- マジック検証の扱いを「即スキップ」から「warning + 解凍試行」へ変更
- `--ext-priority` 不正値メッセージを多言語化（`error.ext_priority_empty` / `error.ext_priority_invalid`）
- argparse と主要関数の引数に、入出力の説明コメントを追加

### [1.7.0] - 2026-08-13

#### 追加

- `--compress LEVEL`: zip 圧縮 0–9。`0` 無圧縮（デフォルト）、`1–9` deflate。PNG 向け。JPEG は効果が薄い
- `--inspect` / `--inspect-all`: CBZ を作らず内部情報を表示。一時ディレクトリは終了時に削除。基本検査、EXTH、二重ディレクトリ、OPF/spine、画像数、表紙、形式分布、解像度、圧縮提案。DRM 疑いと解凍タイムアウトを別集計
- inspect 強化: 表紙は OPF guide `type="cover"` 優先。spine 先頭 5 ファイル名プレビュー。NCX 件数と先頭 3 タイトル。EXTH に ASIN・著作権。DRM はヘッダー＋画像有無の二段判定

#### リファクタリング

- パッケージ化: `compress>0` は `ZIP_DEFLATED`+`compresslevel`、それ以外は `ZIP_STORED`。古い Python の非推奨警告を回避
- 二重ディレクトリ選択を `select_mobi_dir` に統一。出力インデントを 2 スペースに整理

### [1.6.0] - 2026-08-13

#### 追加

- `--output-dir DIR`: 指定ディレクトリへ CBZ 出力（自動作成）。`--overwrite` の判定も出力先基準
- 事前チェック: 0 バイト・`BOOKMOBI` なしをスキップし、パスと理由をログ
- `--dry-run`: 実書き込みなしでフローと出力先を表示
- `--min-size BYTES`: 小さすぎるファイルを除外。OSError 時のスキップ理由も追加
- ファイル単位・合計の所要時間
- 成功/スキップ/失敗の 1 行統計（0 件も含めて常に表示）

#### リファクタリング

- `ConvStatus`（`OK` / `SKIP` / `FAIL`）に状態を統一
- 出力タグを定数化（のちの 1.8.0 で `t()` へ移行）
- `run_with_timeout` のスレッド残留についてコメント
- `main()` でトップレベル例外と Ctrl+C を `emit` 経由で処理
- `--short-summary` を追加

### [1.5.0] - 2026-08-13

#### 追加

- `--timeout`（デフォルト 600 秒）
- パスの大文字小文字正規化
- 出力タイムスタンプ

#### 変更

- `--log` 書き込み失敗時に警告を 1 回表示
- Ctrl+C 時に途中集計を出力
- 既存 cbz によるスキップを集計に含める
- 無効だった外側 `TemporaryDirectory` を削除

### [1.4.0] - 2026-08-13

#### 追加

- 起動時の依存チェック
- DRM 可能性の明示
- `--overwrite` / `--quiet` / `--log`
- 変換前後のパス一覧、失敗一覧

#### 修正

- `mobi.extract` の一時ディレクトリを `finally` で確実に削除

### [1.3.0] - 2026-08-13

#### 追加

- 表紙フォールバック（cover/front）
- ディレクトリ余分画像の追記 / `--drop-extra`

### [1.2.0] - 2026-08-13

#### 追加

- OPF spine 順抽出
- `--version`
- `select_mobi_dir`
- spine 空時の自然順フォールバック

#### 変更

- 同名画像に `{idx:04d}_` プレフィックス
- スクリプト名を `manga-mobi2cbz.py` に変更

### [1.1.0] - 2026-08-13

#### 追加

- `__version__` と `SCRIPT_NAME`

### [1.0.0] - 2026-08-12

#### 追加

- 初の実用版: 再帰収集、一括 cbz 変換、二重ディレクトリ整理、EOCD + testzip、失敗時の半製品削除

## License

[MIT](./LICENSE)
