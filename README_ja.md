**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md)

# manga-mobi2cbz

Kindle 漫画向けの一括変換 CLI ツールです。ワンコマンドで DRM フリーの MOBI / AZW / AZW3 / EPUB 電子書籍を標準 CBZ コミックパッケージに書き出します。
OPF spine の標準的な読み順に従って画像を抽出し、表紙の自動補完、同一巻の複数形式の重複排除、バッチのタイムアウト保護、ファイル完全性の検証、多言語出力などの実用機能を備えています。パッケージ化せずにメタデータ・解像度・NCX 目次・DRM 状態を確認できる `--inspect` 検査モードも付属し、全プラットフォームで漫画ライブラリの一括整理を安定して効率化します。

> ⚠️ 対応しているのはDRMフリーのKindle漫画のみです。ストア購入のDRM保護された電子書籍は解析できません。
>
> ⚠️ 本コードは完全にAIによって生成されています。私は一行ずつ監査することはできないため、ご利用の際は自己責任でリスクをご評価ください。
>
> 📝 補足：本プロジェクトは個人利用のために作成されました。AI生成スクリプトを後で再利用できるよう保存する目的で公開しています。
>
> **開発の経緯**：当初は自身のKindle漫画を変換するため、毎回AIにスクリプトを生成してもらっていました。再利用を簡単にし、スクリプトを失わないよう、GitHubへアップロードするに至りました。
> その後の使用で、ページ順の乱れ、表紙の欠落、バッチ処理のフリーズといった問題が判明し、AIへ修正を繰り返し依頼しました。コードが読めないため、信頼性を確認するために同一のコードを複数のAIに渡して相互検証するワークフローを確立しました。当初の使い捨てスクリプトが、反復的な改善を経て現在の形へと進化しました。コードは完全にAIが生成しており、私は要件定義と結果の検収のみを担当しています。専門的なツールではありませんが、初期バージョンよりは格段に完成度が高まっています。同じような悩みをお持ちの方がいれば、ご自由にお使いください。不具合を見つけた場合はご連絡ください。引き続きAIに修正させます。

## 機能

- **一括変換** — 単一ファイル、またはディレクトリ全体を再帰的に変換（`.mobi` / `.azw` / `.azw3` / `.epub`）
- **OPF spine 順** — OPF spine の順序で画像を抽出し、実際の読み順を保ちます。OPF が無い場合はファイル名の自然順ソートにフォールバックします
- **表紙フォールバック** — ファイル名に cover/front を含む画像を自動スキャンします。表紙がすでに spine リスト内にあればリスト順を優先し、欠落時のみ先頭に補完します
- **ディレクトリ整合フォールバック** — ディレクトリ内の画像数が収集数と一致しない場合、余分な画像はデフォルトで自然順に cbz 末尾へ追記します。`--drop-extra` で破棄に変更でき、処理結果は出力されます
- **二重ディレクトリの重複排除** — mobi7/mobi8 の二重ディレクトリを自動検出し、内容がある方のコピーを保持します（デフォルト `auto`: mobi8 を優先し、mobi8 に画像がない場合は mobi7 に自動フォールバック。`mobi7`/`mobi8` を明示指定した場合も、選択ディレクトリに画像がないときはもう一方へフォールバックします）
- **軽量多言語対応** — `--language auto|zh-CN|zh-TW|ja|en` で出力言語を切り替えます（デフォルト `auto` はシステム locale で自動判定: 簡体字中国語→zh-CN、繁体字中国語→zh-TW、日本語→ja、その他→en）。
- 実行時のメッセージと `--help` は選択言語に追従します。CLI のフラグ名、列挙値、技術用語（OPF / DRM / spine など）は翻訳しません
- **同名拡張子の重複排除** — 同じディレクトリ内で拡張子だけ異なるファイル（例: `Vol1.mobi` + `Vol1.azw3`）は 1 つだけ保持します。`--ext-priority` で保持優先度を制御します（デフォルト azw3）
- **自然順ソート** — ページ番号で自然順に並べ、`10.jpg` が `2.jpg` より前に来るのを防ぎます
- **完全性検証** — 変換後に CBZ を自動検証し、破損時は削除して通知します
- **ComicInfo.xml メタデータ** — デフォルトで CBZ ルートに ComicInfo.xml を生成（UTF-8、XML 宣言付き）し、Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary を書き込みます。Series/Number はファイル名から高確度で推測（`001` / `01` / `1` / `Vol.01` / `Vol 01` / `Volume 01` / `第 01 卷` などの形式に対応）し、シリーズ名のない巻マーカー（例: `Vol.01` / `01巻`）は推測しません。確度が足りない場合は省略します（見つからないより良い）。確かな情報源のないフィールドは空タグを生成しません。`--no-comicinfo` で無効化できます
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
- **カスタム出力ディレクトリ** — `--output-dir DIR` で CBZ を指定ディレクトリへ出力します（自動作成）。デフォルトでは入力の相対サブディレクトリ構造を保持します（例: `One Piece/001.mobi` → `DIR/One Piece/001.cbz`）。`--flatten` を付けると出力ルートへフラット化し、同名ファイルは `--overwrite` 未指定時はスキップ（SKIP）します
- **事前チェックフィルタ** — 0 バイトやヘッダ破損（オフセット 60 に `BOOKMOBI` なし）のファイルは事前チェックでスキップし、フルパスと理由をログに出します
- **最小サイズフィルタ** — `--min-size BYTES` で指定バイト未満を除外します（数値省略時デフォルト 1000、`0` で無効、未指定でサイズフィルタオフ）
- **ドライラン** — `--dry-run` は変換フローの表示のみで、実際の解凍・パッケージ化は行いません
- **再開サポート** — 対象 CBZ が既に存在し完全性検証に合格した場合はスキップ（SKIP）します。破損・無効な場合は自動で再変換します。ソースファイルが対象 CBZ より新しい場合も自動で再変換します。`--overwrite` は無条件で上書きします
- **失敗の分類** — 変換失敗を原因別に集計します（`timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other`）。集計にカテゴリ別の件数を表示します
- **検査モードが CBZ 対応** — `--inspect` で `.cbz` を直接検査できます（zipfile のみで解凍しません）。表紙行に解像度+サイズ、形式統計に総ファイル数、Spine 先頭 5 件の各行に幅/高さを追加
- **ComicInfo フィールド上書き** — `--setinfo FIELD=VALUE` で ComicInfo フィールドを上書き/追加します（最優先）。VALUE は固定値 / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN` プレースホルダに対応し、複数指定可能。`FIELD` は ComicInfo 標準フィールドのホワイトリスト内である必要があります（単純フィールド 39 個、複雑な `Pages` は除外。ホワイトリスト外は warning を出して無視）。入力が既存 `.cbz` の場合はその ComicInfo.xml を直接変更します（未指定フィールドは元の値を保持、一時ファイル + アトミック置換で書き込み）
- **ログの自動命名** — `--log` をファイル名なしで指定すると `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（カレントディレクトリ）を自動生成します
- **解凍表示** — `--unpack` は変換せず解凍のみ行い、各ソースファイルと同じ名前のサブディレクトリへ出力します（既存時は `(2)(3)` と自動採番）。mobi は extract で完全な構造を保持、cbz は extractall（zip-slip パストラバーサル対策付き）。`--unpack` または `--setinfo` 指定時は `.cbz` 入力も収集します
- **所要時間** — ファイルごとの変換時間をリアルタイム表示し、集計下部に合計を出します
- **JSON 構造化出力** — `--json` は実行結果を 1 行のコンパクト JSON として stdout に出力（AI / パイプライン / スクリプト向け、有効時は人間向けテキスト出力を抑制）。`--json-out [FILE]` は構造化結果を JSON ファイルに書き込み（インデント形式、ファイル名省略時はタイムスタンプ付きファイルを自動生成、`--log` と同一挙動）。両者は併用可能で、変換モードと `--setinfo` 変更モードの両方に対応

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

### ディレクトリ全体を一括変換（.mobi / .azw / .azw3 / .epub を再帰検索）

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

### ComicInfo フィールドを上書き/追加（複数指定可、最優先）

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --setinfo "Title=My Manga" --setinfo "Number=%number" --setinfo "Summary=hello, world"
```

> 補足: `--setinfo` はカンマの直後に「フィールド名=」が続く場合のみ分割します。値自体に `Key=...` 構造が含まれる場合は、誤分割を避けるため複数回の `--setinfo` で渡してください。入力ディレクトリに既存 `.cbz` と `.mobi` が混在する場合、`--setinfo` 有効時は `.cbz` の ComicInfo.xml を直接変更し（未指定フィールドは元の値を保持）、それ以外のファイルは通常どおり変換します。

### 解凍表示（変換せず解凍のみ、同名サブディレクトリへ出力）

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --unpack
```

### JSON 構造化出力（stdout 1 行 / ファイル書き込み）

```bash
python manga-mobi2cbz.py "D:\Manga" --json
python manga-mobi2cbz.py "D:\Manga" --json-out
python manga-mobi2cbz.py "D:\Manga" --json --json-out result.json
```

> 補足: `--json` / `--json-out` は「変換」または「CBZ 変更」の実行後にのみ構造化結果を出力します。`--dry-run` / `--inspect` / `--unpack` モードでは出力しません。プログレスバーと人間向け表示は stderr、JSON は stdout に書き込まれ自然に分離しますが、`2>&1` で結合リダイレクトするとプログレスバーが JSON に混入するため、その場合は `--no-progress` を併用してください。

### バージョン確認

```bash
python manga-mobi2cbz.py --version
```

## パラメータ説明

| パラメータ | 説明 |
| --- | --- |
| `target` | 電子書籍ファイルのパス、または `.mobi` / `.azw` / `.azw3` / `.epub` を含むディレクトリ（必須） |
| `--language LANG` | 出力言語。`auto` はシステム locale で自動選択（簡体字→zh-CN、繁体字 zh-TW/zh-Hant→zh-TW、日本語 ja/Japanese→ja、その他→en）。または `zh-CN` / `zh-TW` / `ja` / `en` を指定（デフォルト `auto`）。一般的な表記も許容: `zh`/`cn`→zh-CN、`zhtw`/`tw`→zh-TW、`jp`→ja、`eng`→en |
| `--delete` | 変換成功後に元の電子書籍を削除（デフォルト: 削除しない） |
| `--prefer` | 二重ディレクトリ mobi で保持する側: `auto` / `mobi7` / `mobi8`（デフォルト `auto`）。`auto` は mobi8 を優先し、mobi8 に画像がない場合は mobi7 に自動フォールバック。`mobi7`/`mobi8` を明示指定した場合も、選択ディレクトリに画像がないときはもう一方へフォールバック |
| `--drop-extra` | 未収集の余分な画像を破棄（デフォルト: cbz 末尾に追記） |
| `--overwrite` | 対象 cbz が既にある場合に強制再生成（デフォルト: スキップ） |
| `--ext-priority EXTS` | 同一ディレクトリ・同名（拡張子のみ異なる）とき保持する形式。カンマ区切りで優先度が高い順。受け付ける値は `mobi` / `azw` / `azw3` / `epub`。デフォルト `azw3`。未指定分は azw3→epub→mobi→azw にフォールバック。`--prefer`（mobi7/mobi8）とは無関係 |
| `--timeout` | 1 ファイルあたりのタイムアウト秒数。超過分はスキップして失敗計上（デフォルト 600、`0` は無制限） |
| `--min-size BYTES` | 指定バイト未満を除外。数値省略時は 1000、`0` で無効、オプション未指定でサイズフィルタオフ |
| `--output-dir DIR` | CBZ の出力先（自動作成）。デフォルトで入力の相対サブディレクトリ構造を保持（例: `One Piece/001.mobi` → `DIR/One Piece/001.cbz`）。`--flatten` でルート直下にフラット化 |
| `--flatten` | `--output-dir` と併用時のみ有効。すべての CBZ を出力ルート直下へフラット化し、同名ファイルは `--overwrite` 未指定時はスキップ（SKIP）、指定時は優先名を上書き。単独指定（`--output-dir` なし）はエラー終了 |
| `--progress` | ファイル単位のプログレスバーを強制表示。デフォルトは stderr が TTY かつファイル数≥2 で自動表示。`--no-progress` と同時指定時は後に書いた方が有効。`--quiet` 下でもデフォルトは表示。stderr のみで `--log` には入らない |
| `--no-progress` | プログレスバーを強制オフ |
| `--dry-run` | スキャンと変換フロー表示のみ。解凍・パッケージ化・出力ディレクトリ作成はしない |
| `--quiet` | エラーと最終集計のみ表示 |
| `--short-summary` | 成功/スキップは件数のみ（失敗は常にフルパス） |
| `--compress LEVEL` | zip 圧縮レベル 0–9。`0`=無圧縮（デフォルト）、`1–9`=deflate（PNG 向け。高いほど小さいが遅い） |
| `--inspect` | 位置引数が単一ファイルの場合はそのファイルを直接検査、ディレクトリの場合は 1 冊をランダム抽出して内部情報のみ読取（CBZ 非生成、一時ディレクトリは終了時に削除） |
| `--inspect-all` | 全冊を検査（`--inspect` と併用が必要、単独指定時は自動的に `--inspect` を有効化） |
| `--no-comicinfo` | ComicInfo.xml を生成しない（デフォルト: CBZ ルートに Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary を書き込み） |
| `--setinfo FIELD=VALUE` | ComicInfo フィールドを上書き/追加（複数指定可、最優先）。`FIELD` は ComicInfo 標準フィールドのホワイトリスト内である必要があります（ホワイトリスト外は warning を出して無視）。`VALUE` は固定値 / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN` プレースホルダに対応（対応値が無い場合はそのフィールドを書き込まない）。スマート分割: カンマの直後に `フィールド名=` が続く場合のみ分割し、それ以外はカンマを値の一部とみなす（例: `Summary=hello, world` は分割しない）。入力が既存 `.cbz` の場合、その ComicInfo.xml を直接変更（未指定フィールドは元の値を保持）。値に `Key=` が含まれる場合は複数回の `--setinfo` で渡す。有効時は入力に混在する `.cbz` を直接変更し、他のファイルは通常どおり変換。`Manga` はデフォルトで書き込まず、`--setinfo Manga=Unknown\|No\|Yes\|YesAndRightToLeft` で明示指定（公式 v2.0 の列挙のみ）。`CommunityRating`（0-5）/ `MainCharacterOrTeam` / `Review` の 3 つの公式フィールドにも対応 |
| `--unpack` | 解凍表示: 変換せず解凍のみ。各ソースファイルと同じ名前のサブディレクトリへ出力（既存時は `(2)(3)` と自動採番）。mobi は extract で完全な構造を保持、cbz は extractall（zip-slip パストラバーサル対策付き）。`--unpack` 指定時は `.cbz` 入力も収集 |
| `--double-page VALUE` | 見開きページ検出: 未指定または `auto` で有効（閾値 2.0。幅/高さ ≥ 閾値の横長見開き大画像を検出し、ComicInfo にページごとの `Type="DoublePage"` を書き込む。`Manga` は自動で宣言しない）。数値指定（例 `2.5`）で有効化し閾値を調整。`off` / `no` / `0` で無効化。不正値はエラー |
| `--drop-small [VALUE]` | 小画像の破棄: 変換時に他の画像より明らかに小さい画像（表紙サムネイル / 版権ページなど）を除外。幅・高さとも 中央値 × 比率 未満で小画像と判定。値なし/`auto` はデフォルト比率 0.5、`0~1` の数値（例 `0.4`）で比率調整、`off` / `no` / `0` で無効化（デフォルト無効、既存動作は不変）。破棄後は ComicInfo `PageCount` を実画像数で再計算。集計 / `--log` / `--json` に「破棄した小画像」カウントを追加（`--json` は `dropped_small` フィールド）。`--inspect` プレビューで「--drop-small 有効時は N 枚破棄されます」と表示。横長見開き（幅は小さくない）は誤破棄されない。変換モードのみ有効 |
| `--log FILE` | 全出力を指定ログへ追記。ファイル名なしで指定すると `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（カレントディレクトリ）を自動生成 |
| `--json` | 実行結果を 1 行のコンパクト JSON として stdout に出力（AI / パイプライン / スクリプト向け）。有効時は人間向けテキスト出力（プログレスバー / emit 表示 / 集計）を抑制。`--json-out` と併用可。変換/変更モードでのみ出力（dry-run/inspect/unpack では出力しない）。プログレスバーは stderr に書き込まれ混ざらないが、2>&1 結合リダイレクトでは混入する |
| `--json-out [FILE]` | 構造化結果を JSON ファイルに書き込み（インデント形式）。ファイル名なしで指定するとタイムスタンプ付きファイル（カレントディレクトリ）を自動生成、`--log` と同一挙動。`--json` と併用可。`--json` と同様、変換/変更モードのみ書き込み |
| `--version` | バージョン番号を表示 |

## 出力

- デフォルトでは `.cbz` は元の電子書籍と同じディレクトリに置きます。`--output-dir` 指定時はそのディレクトリへ出力します（自動作成）。デフォルトで入力の相対サブディレクトリ構造を保持し、`--flatten` でルート直下にフラット化します（同名ファイルは `--overwrite` 未指定時はスキップ）
- 既存の `.cbz` はデフォルトでスキップし、上書きしません。`--overwrite` で強制再生成できます
- 0 バイト / ヘッダ破損は事前チェックでスキップし、フルパスと理由をログに出します
- ファイルごとの所要時間をリアルタイム表示し、集計下部に合計を出します
- 失敗したファイルはエラーを表示しますが、他ファイルの変換は継続します

## 既知の制限

- **DRM 暗号化ファイルには非対応** — 下層の mobi ライブラリは Kindle ストアの DRM 付き漫画を復号できません。該当ファイルは「DRM の可能性あり」と明示してスキップし、空の cbz を黙って作りません。変換前に DRM を解除してください
- **タイムアウト後のスレッドは強制終了できない** — `--timeout` 超過後、メイン処理はそのファイルをスキップして続行しますが、Python はブロック中の解凍スレッドを kill できません。残ったスレッドはプロセス終了までメモリ/IO を使うことがあり、破損ファイルが多いとバックグラウンドに積み上がる可能性があります。完全隔離には `multiprocessing` などが考えられますが、クロスプラットフォームの複雑さのため未採用です

## よくある質問

**Q: 変換後の CBZ で画像の順序が乱れるのは？**  
A: まず OPF spine 順（EPUB の標準的な読み順）で抽出するため、多くの場合は正しい順序になります。OPF が無い、または spine が空のときはファイル名の自然順にフォールバックします。それでもおかしい場合は、元ファイル内の画像名が不統一な可能性があります。ソースを確認してください。

**Q: CBZ に表紙が無いのはなぜ？**  
A: 一部のファイルでは表紙が OPF の cover メタのみで指され、spine から参照されないため漏れます。スクリプトは cover/front を含むファイル名を探し、無ければ先頭に補完します。すでに spine にあれば元の順を保ちます。キーワードの無いファイル名だと漏れることがあるので、リネームして再変換してください。

**Q: 変換後のサイズが極端に小さいのはなぜ？**  
A: mobi7+mobi8 の二重構成ではデフォルトで 1 コピーのみ残します（`--prefer auto`）: mobi8 を優先し、mobi8 に画像がない場合は mobi7 に自動フォールバックして内容の二重化を避けます。mobi7 を強制したい場合は `--prefer mobi7` を指定してください。

**Q: 一括変換中に破損/暗号化ファイルで止まったように見える？**  
A: 1 ファイルあたりデフォルト 600 秒のタイムアウトがあります（`--timeout` で変更可）。超過分はスキップして失敗計上し、残りを続行します。早く切りたいときは `--timeout 30` など短くするか、`--quiet` で出力を減らしてください。

**Q: --output-dir でサブディレクトリが残るのはなぜ？**
A: v1.9.0 以降、`--output-dir` はデフォルトで入力の相対サブディレクトリ構造を保持します（旧版の一律フラットから破壊的変更）。フラット化したい場合は `--flatten` を追加してください。旧コマンド `python manga-mobi2cbz.py Manga --output-dir CBZ` は `python manga-mobi2cbz.py Manga --output-dir CBZ --flatten` に変更すると旧動作を復元できます。

**Q: .azw / .azw3 には対応していますか？**  
A: 対応しています。v1.8.0 以降、入力は `.mobi` / `.azw` / `.azw3` で、同じ変換パイプラインを使います。同一ディレクトリで同名・異拡張子のときはデフォルトで azw3 を残し、`--ext-priority` で変更できます。

**Q: EPUB には対応していますか？**
A: 対応しています。v2.4.0 以降、入力は `.mobi` / `.azw` / `.azw3` / `.epub` です。EPUB は ZIP コンテナのため zipfile で安全に解凍し、OPF spine 抽出パイプラインを再利用します。表紙は EPUB2（`<meta name="cover">`）と EPUB3（`properties="cover-image"`）の両方に対応。EXTH ヘッダが無いため、メタデータは OPF の `dc:` フィールドから読み取ります。`--prefer` は EPUB では静かに無視されます。暗号化された EPUB（Adobe DRM など）は内容を解析できず、画像なし/有効なメタデータなしとしてスキップされます。変換前に DRM を除去してください。

## 更新履歴

### [2.5.1] - 2026-08-20

#### 修正

- **同名 `.cbz` が重複除去で削除されないように** — `--setinfo` / `--inspect` / `--unpack` モードで、変換成果物 `.cbz` は mobi/azw/azw3/epub の同名重複除去に参加せず、既存 CBZ を正常に変更・検査できる
- **flatten 同名衝突の専用ヒント** — flatten モードで 2 つ目の同名ソースがスキップされる際、汎用の「対象は既に存在」ではなく flatten 衝突と明示し、`--overwrite` を提案

### [2.5.0] - 2026-08-20

#### 変更

- **`Manga` を自動で書き込まない** — 見開きページ検出（`--double-page`）は `<Pages>` のページごとの `Type="DoublePage"` マーカーのみ生成し、`<Manga>Yes</Manga>` 宣言は自動付与しない（Mihon などのリーダーはこのフィールドを読まないため、見開きが無くても Manga と宣言されるのを回避）。`Manga` は `--setinfo Manga=Unknown|No|Yes|YesAndRightToLeft` で明示指定。公式 v2.0 の列挙のみ受け付け、不正値は warning を出して無視
- **`--ext-priority` が EPUB に対応** — `mobi` / `azw` / `azw3` / `epub` を受け付け。優先度が未指定のグループのフォールバック順は `azw3 → epub → mobi → azw` に変更（EPUB を mobi 系より優先）
- **画像なしヒントを拡張子で分岐** — 画像の無い EPUB には中立なヒント（漫画画像を含み暗号化されていないか確認）を出し、Kindle DRM の誤警告をやめる。mobi/azw/azw3 は従来どおり DRM の可能性を提示

#### 追加

- **`--setinfo` のホワイトリスト拡張（39 → 42）** — 公式 ComicInfo v2.0 の 3 フィールド `CommunityRating`（0-5 評価）/ `MainCharacterOrTeam` / `Review` を追加
- **`--drop-small` で小画像を破棄** — デフォルト無効。有効にすると変換時に他の画像より明らかに小さい画像（表紙サムネイル / 版権ページなど）を除外: 幅・高さとも 中央値 × 比率 未満で小画像と判定（デフォルト比率 0.5、`0~1` の数値で調整、`off`/`no`/`0` で無効化）。画像ごとに PNG/JPEG ヘッダーの幅・高さを読むだけで、新規依存なし。破棄後は ComicInfo `PageCount` を実画像数で再計算。集計 / `--log` / `--json` に「破棄した小画像」カウントを追加（`--json` は `dropped_small` フィールド）。`--inspect` プレビューで「--drop-small 有効時は N 枚破棄されます」と表示。横長見開き（幅は小さくない）は誤破棄されない

#### ドキュメント

- **`--help` を 4 言語で同期** — `help.description` / `help.target` / `help.ext_priority` に `.epub` を追記。`help.setinfo` に Manga 列挙と明示指定の説明を追加
- **暗号化 EPUB の注記** — FAQ に暗号化 EPUB（Adobe DRM など）は変換不可、先に DRM 除去と明記

### [2.4.0] - 2026-08-20

#### 追加

- **EPUB 入力に対応** — 入力拡張子を `.mobi` / `.azw` / `.azw3` / `.epub` に拡大。`ebook_to_cbz` / `--inspect` / `--unpack` は拡張子で分岐: EPUB（ZIP コンテナ）は zipfile で安全に解凍（zip-slip 対策付き）、mobi/azw/azw3 は従来どおり `mobi.extract`。既存の OPF spine 抽出・ComicInfo メタデータのパイプラインを再利用し、形式ごとの別実装は持たない
- **EPUB の表紙フォールバックを強化** — `get_opf_guide_cover_href` を 3 ソースに: ① guide `type="cover"` ② manifest `properties="cover-image"`（EPUB3）③ `<meta name="cover">` が指す item href（EPUB2）。表紙 href の解決を OPF ディレクトリ相対に修正（EPUB の OPF は通常 OEBPS/ 配下）
- **EPUB のメタデータ補完** — EXTH ヘッダが無い場合、`--inspect` は OPF の `dc:` フィールドからタイトル/作者/言語/出版日/出版社を読み取る。`get_drm_flag` は EPUB では直接通過（ZIP コンテナに PalmDB DRM フィールドが無く、誤検出を回避）
- **`--prefer` は EPUB では静かに無視** — EPUB に mobi7/mobi8 の二重ディレクトリは無く、自然に単一ディレクトリ
- **EPUB3 nav 目次に対応** — `--inspect` は OPF manifest の `properties="nav"` から nav ドキュメントを特定（フォールバック: `*nav*.xhtml`）、`<nav epub:type="toc">` 内の `<a>` タイトルを解析（多段の入れ子を含む）。EPUB2 の `toc.ncx` と同時に表示され、.ncx が無い純粋な EPUB3 でも目次を表示
- **ComicInfo のシリーズ/巻数をメタデータ優先で読み取り** — ComicInfo 生成時、Series/Number は OPF メタデータを優先（`dc:series` / `dc:number`、EPUB3 の `belongs-to-collection` / `group-position`、calibre の `meta[name=calibre:series/series_index]`）。`dc:number` は巻マーカーを自動除去（`卷12` → `12`）、OPF メタデータが無い場合のみファイル名推測にフォールバック
- **見開きページ検出（`--double-page`）** — デフォルトで有効（閾値 2.0）: 幅/高さ ≥ 閾値の横長見開き大画像を検出し、ComicInfo に `<Manga>Yes</Manga>` トップレベルタグ + ページごとの `Type="DoublePage"` を書き込む。`--double-page auto` はデフォルトと同等、`--double-page 2.5` で閾値を調整、`--double-page off`（または `no` / `0`）で無効化。不正値はエラー
- **ComicInfo フィールドの出所注記** — `--inspect` のプレビューで Series/Number に出所（`[setinfo]` / `[opf]` / `[inferred]`）を注記し、ユーザー指定・OPF メタデータ・ファイル名推測のどれ由来かを一目で判別できるように。`--json` 出力にも `series_source` / `number_source` / `cover_source` フィールドを追加（値は `setinfo` / `opf` / `inferred` / `filename` など）。AI / パイプラインがフィールドの信頼度を判断するためのもの

#### 変更

- **`--unpack` の安全解凍を統一** — CBZ と EPUB で `_safe_zip_extract`（zip-slip 対策）を共用し、ロジックを単一化
- **`--setinfo` の CBZ 変更をストリーミング化** — `modify_cbz_comicinfo` はアーカイブ全体をメモリに読み込まず、双方向ハンドルで 1MB チャンクずつコピーし、`ComicInfo.xml` のみメモリに読み込む。各エントリの圧縮方式・タイムスタンプ・属性を保持し、アトミック置換と例外時のクリーンアップは従来どおり（大容量アーカイブのメモリ使用量が O(全体) から O(単一エントリ) に低減）
- **ComicInfo の優先順位を変更（setinfo > OPF メタデータ > ファイル名推測）** — 従来 Series/Number はファイル名推測（`infer_series_number`）の結果をそのまま使っていた。現在はユーザー指定の `--setinfo` を最優先、次に OPF メタデータ、最後にファイル名推測。シリーズ名の無い純巻マーカーのファイル（例 `Vol.01.mobi`）は巻番号のみ返し、偽のシリーズ名は付けない
- **巻番号推測の正規表現を拡充** — `infer_series_number` の対応を追加: `巻N` 前置式、`vN`、`第N册`/`N册`、`巻N` 前置式（日本語「巻N」）、フランス語 `tome N`、韓国語 `권N`、タイ語 `เล่ม N`、ロシア語 `Том N`、漢数字の巻（`第一卷`/`卷二`）、小数の巻（`Vol 7.5`）
- **Notes から CoverSource を削除** — 表紙の出所を ComicInfo の `Notes` フィールドに書き込まない（非標準の注記がソフト間で共有される ComicInfo.xml に入らないように）。代わりに `--inspect` の表紙行と `--json` の `cover_source` フィールドで表示し、Notes は内容フィールドのみに

### [2.3.1] - 2026-08-19

#### 修正

- **変換ブランチのアトミック置換を強化** — 一時ファイルを validate_cbz で検証してから `os.replace` で対象を上書き。失敗時は tmp のみ削除し旧 CBZ を保持。ComicInfo 生成失敗時に既存の対象 CBZ を削除しなくなった。Ctrl+C（KeyboardInterrupt）で残る `.tmp` は finally で確実にクリーンアップ
- **`--setinfo` 未知プレースホルダの warning** — ホワイトリスト外のプレースホルダは warning を出力した上でそのまま書き込む（4 言語の i18n キーを追加）
- **sanitize 拡張** — ASCII 制御文字を除去、末尾のピリオド/スペースを除去
- **find_opf の命名優先度** — 複数 OPF がある場合 `content.opf` / `package.opf` を優先
- **メンテナンス** — 古い docstring を整理。`_strip_html` を HTMLParser に変更（不要な `import html` を削除）

#### ドキュメント

- **`--help` 文言を拡充（zh-CN/zh-TW/en/ja）** — `--setinfo`: 値に `Key=` が含まれる場合は複数回指定、有効時は既存 `.cbz` を直接変更。`--json`/`--json-out`: 変換/変更モードでのみ出力（dry-run/inspect/unpack では出力しない）、プログレスバーは stderr へ書き込まれ分離されるが 2>&1 結合では混入
- **README の使用説明を同期** — setinfo / JSON セクションとパラメータ表を更新

### [2.3.0] - 2026-08-19

#### 追加

- **JSON 構造化出力** — `--json` は stdout に単行のコンパクト JSON を出力（AI / パイプ / スクリプト向け。有効時は人間向けテキスト出力を抑止）；`--json-out [FILE]` は構造化結果を JSON ファイルに書き込み（インデント形式、ファイル名省略時はタイムスタンプファイルを自動作成、`--log` と同様の挙動）；両者は併用可能で、変換モードと `--setinfo` 変更モードの両方に対応

#### 修正（v2.2.1 の中間修正を併合してリリース）

- **変換パスのアトミック置換** — CBZ パッケージングを `xxx.cbz.tmp` 一時ファイルに書き込み、すべて成功後に `os.replace` で対象を上書きする方式に変更。パッケージ前の旧 CBZ 削除と失敗分岐での削除を撤廃し、例外時は半成品の tmp のみクリーンアップ。Ctrl+C / 途中クラッシュによる壊れた CBZ の残存、上書き失敗時に旧ファイルが失われるデータ損失リスクを解消（CBZ 変更モードの既存アトミック置換と一貫）
- **`--inspect` の非数値 PageCount 警告** — ComicInfo の PageCount が数値でない場合、黙って無視せず warning を出力（新 i18n キー `inspect.pagecount_non_numeric`、四言語同期）
- **`--timeout` ヘルプ文言** — タイムアウト後に基盤の解凍スレッドがバックグラウンドに残る可能性がある旨を追記。`--overwrite` の表示も「古いファイルを上書きし再生成」に変更し、実際のアトミック置換動作に一致させた

### [2.2.0] - 2026-08-18

#### Added

- **CBZ 変更モード** — 入力が既存 `.cbz` で `--setinfo` 指定時、その ComicInfo.xml を直接変更: 元 XML を読む → 指定フィールドを上書き、未指定フィールドは元の値を保持 → 一時ファイル + アトミック置換（`os.replace`）で書き込み。`--dry-run` プレビュー / 集計 / `--log` に対応
- **setinfo ホワイトリスト** — `--setinfo` のフィールド名は ComicInfo 標準フィールドのホワイトリスト内である必要があります（単純フィールド 39 個、複雑な `Pages` は除外）。ホワイトリスト外は warning を出して無視
- **ソース更新で自動再変換** — 再開サポートに、ソースファイルが対象 CBZ より新しい場合の自動再変換を追加
- **`--unpack` / `--setinfo` が CBZ 入力に対応** — 収集段階で `--unpack` または `--setinfo` 指定時は `.cbz` も収集
- **`--prefer auto`（デフォルト）** — 二重ディレクトリ mobi のデフォルトを auto に: mobi8 を優先し、mobi8 に画像がない場合は mobi7 に自動フォールバック。`mobi7`/`mobi8` 明示指定時も、選択ディレクトリに画像がない場合はもう一方へフォールバック
- **Summary の HTML クリーンアップ** — ComicInfo の Summary フィールドから HTML タグを取り除き、プレーンテキストを書き込み
- **表紙ソースの注記** — ComicInfo の Notes フィールドに `CoverSource`（OPF guide / ファイル名マッチ）を追記
- **CBZ 事前チェック** — `.cbz` 入力も 0 バイト / `--min-size` チェックの対象に
- **`--inspect` の PageCount 整合性チェック** — CBZ 内の ComicInfo PageCount と実際の画像数を比較し、不一致を報告

#### Changed

- **`--unpack` のパス安全性** — cbz 解凍に zip-slip パストラバーサル対策（`..` / 絶対パスを拒否）と解凍集計を追加
- **複数 OPF の warning** — ディレクトリに複数の `.opf` がある場合 warning を出し、先頭のものを使う
- **破損 CBZ 再変換の理由表示** — 再開パスで破損 CBZ を再変換する際、`validate_cbz` の具体的な失敗理由を出力
- **HTML 画像パスの互換性** — `<img>` の src 抽出で、ローカルパス解決前にクエリ / フラグメント（`?` / `#`）を除去
- **ディレクトリ作成タイミング** — 対象 CBZ が既に存在し SKIP される場合、出力ディレクトリを早期に作成しない
- **コードの衛生** — `ebook_to_cbz` の戻り値型注釈を 3 要素タプルに補完、`_auto_language` 末尾を明示化

### [2.1.0] - 2026-08-17

#### 追加

- **再開サポート（デフォルト動作）** — 対象 CBZ が既に存在し `validate_cbz` に合格した場合は SKIP、破損・無効な場合は自動で再変換。`--overwrite` は無条件で上書き
- **失敗の分類** — `ebook_to_cbz` は 3 要素タプル `(result, status, reason)` を返すようになり、失敗理由を `timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other` に分類。主フローに `failed_reasons` 集計を追加し、集計に出力
- **`--inspect` が CBZ 対応** — `inspect_ebook` に統合。CBZ 分岐は zipfile のみで解凍しない。`image_dimensions_bytes(bytes)` を抽出して再利用
- **`--inspect` 出力の強化** — 表紙行に解像度+サイズ、形式統計に総ファイル数、Spine 先頭 5 件の各行に幅/高さを追加
- **`--setinfo FIELD=VALUE`** — ComicInfo フィールドを上書き/追加（複数指定可、最優先）。VALUE は固定値 / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN` に対応。スマート分割（カンマ直後に `フィールド名=` が続く場合のみ分割）。CBZ 変更モードは zip を直接書き直し。`--inspect` プレビューブロックにも適用
- **ComicInfo を同一 zip パスで書き込み** — `write_comicinfo` 関数を削除し、Step4 の with ブロック内で `zf.writestr`
- **`--log` の自動命名** — `nargs="?"` + `const="auto"`。auto 時は `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（カレントディレクトリ）を生成
- **`--unpack` 解凍表示** — 変換せず解凍のみ。mobi は extract で完全な構造を保持、cbz は extractall。デフォルトで同名ディレクトリへ出力し、既存時は `(2)(3)` と自動採番

### [2.0.2] - 2026-08-17

#### 変更

- `infer_series_number` が括弧付きサフィックスに対応: ファイル名の `(著者)` などの括弧が巻号推測を妨げなくなりました
- 純粋な巻マーカー（`Vol.01` / `第 01 卷` / `01巻` など）は巻号のみ `(None, number)` を返すようになり、`(None, None)` ではなくなりました。ComicInfo に Number を書き込めます
- `--flatten` の同名処理を SKIP/`--overwrite` に変更: フラット出力ルートの同名ファイルは自動番号で `(2).cbz` に再変換されず、`--overwrite` 未指定時はスキップ（SKIP）、指定時は優先名を上書きします。dry-run と実実行は一致します
- 参照がなくなった `unique_path` 関数を削除

#### 修正

- PageCount の整合性を修正: 物理重複の除去を ComicInfo 生成より前に移動し、PageCount とパッケージングの両方で重複除去後の実書き込み数を採用
- `run_with_timeout` のバージョン間互換を修正: 組み込み `TimeoutError` と `concurrent.futures.TimeoutError` の両方を捕捉（Python 3.10 対応）
- `infer_series_number` のドット不具合を修正: `path.name` で拡張子を手動除去する方式に変更し、`One Piece Vol.01` のようなドット付き巻号を正しく推測
- LanguageISO ホワイトリスト + alias: ISO 639-1 全 184 コードのホワイトリスト検証と、`jp→ja` / `cn→zh` / `zhtw→zh` などの一般的な別名を追加
- Year の厳格な日付解析: 完全な日付フィールドを優先し、範囲/複数値（`2001-2005`）は None を返す
- `emit` の warning を `--quiet` 下でも表示
- EXTH ループ変数 `t` を `type_id` に改名し、グローバル `t()` の遮蔽を回避
- 正規表現 img src 抽出に `unquote` を適用し、HtmlImgParser フォールバックと一致
- `--language` の寛容化: `zh`/`cn`/`zhtw`/`jp` などの一般的な表記を `_normalize_lang` で正規化（argparse の choices 制限を撤廃）

### [2.0.1] - 2026-08-17

#### 修正

- `infer_series_number` がシリーズ名のない巻マーカーのみのファイル名（`Vol.01` / `Volume 01` / `01巻` など）からシリーズ名を誤って推測する問題を修正。`_is_volume_marker` による巻マーカー語フィルタを追加

### [2.0.0] - 2026-08-14

#### 追加

- デフォルトで ComicInfo.xml を生成（CBZ ZIP ルートへ書き込み、UTF-8、XML 宣言付き）。`--no-comicinfo` で無効化
- 4 つの関数を追加: `build_comicinfo`（`xml.etree.ElementTree` で生成、手動文字列連結は禁止）、`write_comicinfo`、`normalize_language`（言語コードを ISO 639-1 に正規化）、`infer_series_number`（ファイル名から Series/Number を高確度で推測、`001`/`01`/`1`/`Vol.01`/`Vol 01`/`Volume 01`/`第 01 卷` などの形式に対応、確度不足時は None を返す＝見つからないより良い）
- フィールド対応: Title=OPF title→EXTH title→ファイル名 stem、Writer=OPF creator→EXTH author、Publisher=OPF publisher→EXTH publisher、Year=PublicationDate の年、LanguageISO=電子書籍自身の言語（ファイル名から推測しない）、PageCount=最終的に CBZ へ書き込む実際の画像数（必須）、Series/Number=ファイル名からの高確度推測、Summary=OPF description（取得時のみ）。確かな情報源のないフィールドは省略（空タグを生成しない）
- フロー挿入: 最終的な画像集合の確定後に ComicInfo を構築し、CBZ 作成時に画像と ComicInfo.xml を同時に書き込み。完全性検証に 3 項目を追加（ComicInfo.xml の存在、標準 XML パーサーで解析可能、ルートノードが ComicInfo）。生成・検証の失敗＝変換全体の失敗とし、`--delete` によるソース削除を禁止
- `--dry-run` は ComicInfo.xml を作成しないが、有効かどうかを 1 行表示
- `--inspect` の出力に ComicInfo プレビューブロックを追加（Title/Series/Number/Writer/Publisher/Year/LanguageISO/PageCount/Summary は値がある場合のみ表示）。推測フィールドには `[inferred]` を明示
- i18n: 4 言語に 6 キーを追加: `comicinfo.generating` / `comicinfo.created` / `comicinfo.disabled` / `comicinfo.invalid` / `comicinfo.inferred` / `help.no_comicinfo`

### [1.9.1] - 2026-08-14

#### 追加

- `--inspect-all` を単独で使用（`--inspect` なし）した場合、自動的に `--inspect` を有効化し warning を出力（4 言語に `warn.inspect_all_auto_enable` キーを追加）
- `--inspect` の説明を更新: 位置引数が単一ファイルの場合はそのファイルを直接検査、ディレクトリの場合はランダムに 1 冊抽出
- `--inspect-all` の説明を更新: `--inspect` と併用必須、単独指定時は自動的に `--inspect` を有効化

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
