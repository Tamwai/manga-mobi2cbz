**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md)

# manga-mobi2cbz

Kindle 漫画向けの一括変換 CLI ツールです。ワンコマンドで DRM フリーの MOBI / AZW / AZW3 / EPUB 電子書籍を標準 CBZ コミックパッケージに書き出します。
OPF spine の標準的な読み順に従って画像を抽出し、表紙の自動補完、同一巻の複数形式の重複排除、バッチのタイムアウト保護、ファイル完全性の検証、多言語出力などの実用機能を備えています。パッケージ化せずにメタデータ・解像度・NCX 目次・DRM 状態を確認できる `--inspect` 検査モードも付属し、全プラットフォームで漫画ライブラリの一括整理を安定して効率化します。

> ⚠️ 対応しているのはDRMフリーのKindle漫画のみです。ストア購入のDRM保護された電子書籍は解析できません。
> 
> **開発の経緯**：漫画形式の処理のために、毎回の変換でAI生成スクリプトを利用しており、再利用しやすくスクリプトの紛失を防ぐため、GitHubにアップロードしました。
> その後の使用で、ページ順の乱れ、表紙の欠落、バッチ中断などの問題が相次ぎ、繰り返しの改良を経て現在の形に至りました。コードは完全にAI生成です。ご自由にお使いください。問題を見つけた場合はフィードバックも歓迎します。

## 機能

- **一括変換** — 単一ファイル、またはディレクトリ全体を再帰的に変換（`.mobi` / `.azw` / `.azw3` / `.epub`）
- **OPF spine 順** — OPF spine の順序で画像を抽出し、実際の読み順を保ちます。OPF が無い場合はファイル名の自然順ソートにフォールバックします
- **表紙フォールバック** — ファイル名に cover/front を含む画像を自動スキャンします。表紙がすでに spine リスト内にあればリスト順を優先し、欠落時のみ先頭に補完します
- **ディレクトリ整合フォールバック** — ディレクトリ内の画像数が収集数と一致しない場合、余分な画像はデフォルトで自然順に cbz 末尾へ追記します。`--drop` で破棄に変更でき、破棄した余分な画像のファイル名を 1 件ずつ列挙します（`--short-summary` 併用時は件数のみ）
- **二重ディレクトリの重複排除** — mobi7/mobi8 の二重ディレクトリを自動検出し、内容がある方のコピーを保持します（デフォルト `auto`: mobi8 を優先し、mobi8 に画像がない場合は mobi7 に自動フォールバック。`mobi7`/`mobi8` を明示指定した場合も、選択ディレクトリに画像がないときはもう一方へフォールバックします）
- **軽量多言語対応** — `--language auto|zh-CN|zh-TW|ja|en` で出力言語を切り替えます（デフォルト `auto` はシステム locale で自動判定: 簡体字中国語→zh-CN、繁体字中国語→zh-TW、日本語→ja、その他→en）。
- 実行時のメッセージと `--help` は選択言語に追従します。CLI のフラグ名、列挙値、技術用語（OPF / DRM / spine など）は翻訳しません
- **同名拡張子の重複排除** — 同じディレクトリ内で拡張子だけ異なるファイル（例: `Vol.01.mobi` + `Vol.01.azw3`）は 1 つだけ保持します。`--ext-priority` で保持優先度を制御します（デフォルト azw3）
- **自然順ソート** — ページ番号で自然順に並べ、`10.jpg` が `2.jpg` より前に来るのを防ぎます
- **完全性検証** — 変換後に CBZ を自動検証し、破損時は削除して通知します
- **ComicInfo.xml メタデータ** — デフォルトで CBZ ルートに ComicInfo.xml を生成（UTF-8、XML 宣言付き）し、Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary を書き込みます。Series/Number はファイル名から高確度で推測（`001` / `01` / `1` / `Vol.01` / `Vol 01` / `Volume 01` / `第 01 卷` などの形式に対応）し、シリーズ名のない巻マーカー（例: `Vol.01` / `01巻`）は推測しません。確度が足りない場合は省略します（見つからないより良い）。確かな情報源のないフィールドは空タグを生成しません。`--no-comicinfo` で無効化できます
- **無圧縮パッケージ** — 画像は既に圧縮済みのため、ZIP はデフォルトで store のみです。高速でサイズも抑えられます
- **任意圧縮** — `--compress LEVEL` で deflate 圧縮（1–9）を有効化できます。PNG ソースではサイズを大きく削減できることがあります。レベルが高いほど小さくなりますが遅くなります。JPEG ソースは効果が限定的で推奨しません（デフォルト `0` = 無圧縮）
- **検査モード** — `--inspect` で電子書籍を 1 冊サンプル検査（デフォルト `sample`）します。`--inspect all` で全冊検査（旧 `--inspect-all` と同等）します。CBZ は作らず解凍して内部情報のみ読み取り、終了後に一時ディレクトリを削除します
- 基本検査（マジックバイト / サイズ / DRM）、見つかった場合の EXTH メタデータ、mobi7/mobi8 マーカー、OPF/spine の件数（先頭 5 ファイル名）、NCX のプレビュー、画像総数、表紙検出、形式分布、主流解像度、末尾の解像度サマリー（主解像度の枚数・割合 + 異常小図の枚数）、圧縮の目安などを表示します
- DRM の扱い: DRM フラグは情報マーカーのみで検査をブロックしません。フラグがあっても解凍を試み、画像が抽出できたら `drm` マーク付きで読める状態と判定します。解凍に失敗し画像が 0 枚の場合のみ DRM と判定します
- **元ファイルの任意削除** — `--delete` で変換成功後に元の電子書籍を自動削除します
- **強制上書き** — `--overwrite` で既存の cbz を強制再生成します。漫画を更新しても古いファイルを手動削除する必要はありません
- **単一ファイルのタイムアウト保護** — `--timeout` で 1 ファイルあたりの変換時間を制限します。破損・暗号化・巨大ファイルが下層の解凍をブロックしても、自動スキップして失敗として計上し、バッチ全体が止まりません（デフォルト 600 秒、`0` は無制限）
- **サイレントモード** — `--quiet` で一括変換時にエラーと集計のみ表示します。`--log FILE` で全出力をログファイルに追記できます
- **簡潔な集計** — `--short-summary` で成功 / スキップ / 事前チェックスキップは件数のみ表示します（失敗は常にフルパス）。`--quiet` と組み合わせると大規模ディレクトリ向きです
- **DRM 暗号化の検出** — DRM 付き Kindle 漫画に遭遇した場合、黙って失敗せず復号できない旨を明示します
- **パスの大文字小文字対応** — 表紙比較とディレクトリ整合に正規化（小文字）パスを使い、大文字小文字を区別しない Windows 上でも誤判定しにくくします
- **出力タイムスタンプ** — 各行に `[YYYY-MM-DD HH:MM:SS]` を付与し、コンソールとログで統一します
- **カスタム出力ディレクトリ** — `--output-dir DIR` で CBZ を指定ディレクトリへ出力します（自動作成）。デフォルトでは入力の相対サブディレクトリ構造を保持します（例: `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`）。`--flatten` を付けると出力ルートへフラット化し、同名ファイルは `--overwrite` 未指定時はスキップ（SKIP）します
- **事前チェックフィルタ** — 0 バイトやヘッダ破損（オフセット 60 に `BOOKMOBI` なし）のファイルは事前チェックでスキップし、フルパスと理由をログに出します
- **最小サイズフィルタ** — `--min-size BYTES` で指定バイト未満を除外します（数値省略時デフォルト 1000、`0` で無効、未指定でサイズフィルタオフ）
- **ドライラン** — `--dry-run` は変換フローの表示のみで、実際の解凍・パッケージ化は行いません
- **再開サポート** — 対象 CBZ が既に存在し完全性検証に合格した場合はスキップ（SKIP）します。破損・無効な場合は自動で再変換します。ソースファイルが対象 CBZ より新しい場合も自動で再変換します。`--overwrite` は無条件で上書きします
- **失敗の分類** — 変換失敗を原因別に集計します（`timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other`）。集計にカテゴリ別の件数を表示します
- **検査モードが CBZ 対応** — `--inspect` で `.cbz` を直接検査できます（zipfile のみで解凍しません）。表紙行に解像度+サイズ、形式統計に総ファイル数、Spine 先頭 5 件の各行に幅/高さを追加
- **画像一覧の読み取り専用表示** — `--list-images [FILTER]` で対象電子書籍の全画像を（No. / ファイル名 / 解像度 / サイズ / モード・深度 / 向き / 目次 / タグ）で列挙し、全量統計ブロック（形式 / モード・深度 / 寸法分布 / 見開き横幅 / アニメーション GIF / 小画像 / 異常明細）を付加。変換せず、CBZ 書き込みも ComicInfo 生成もしません。FILTER は任意で条件式をサポート（形式 / `res` / `size` / 向き / モード / ビット深度 / タグ / `small[=比率]`。カンマ = OR、`+` = AND、`-` 接頭辞 = 除外）。EXIF Orientation≠1 の画像には `[回転N]` マーク（N=2~8、正常=1 は無印）を付け `[異常]` 集計にも加算。方向ワードでフィルタ: 値なし = 方向異常の全画像を選択（rotate=auto で回転予定）、値あり = EXIF Orientation の正確一致（例: `方向=6`）。`--json-out` は `orientation` フィールド（v3.6.0）
- **ファイル名 glob フィルタ** — `name=` の値に `*` / `?` を含む場合は glob 一致でファイル名をマッチ（大文字小文字を無視、特別扱いは `*` と `?` のみ、`[]` はリテラル）、含まない場合は従来の部分一致を維持。`--list-images` / `--drop` / `--pages` の三入口で有効、例 `name=*_表紙*`、`name=p00?`
- **画像処理パイプライン** — `--img-edit` で出力画像に回転 / 鏡像反転 / グレースケール化 / 形式変換 / 再エンコード品質制御 / 拡縮 / 白辺トリミング / EXIF 除去を適用（繰り返し指定可、値内の '+' で分割してフラット化）：`rotate[=auto|90|180|270]` は EXIF Orientation をピクセルに焼き込み Orientation フィールドを削除して再エンコード（値なし = auto、Orientation≠1 の画像のみ処理）、`flip=x|y|both` は鏡像反転（x = 水平、y = 垂直、both = 両方）、`grayscale` はグレースケール化（常に flip の直後に挿入、出力は RGB 三チャンネル等値）、`format=jpeg|png|webp`（別名 jpg；目標形式、再エンコード後に cbz 内エントリの拡張子を同期変更；透明→JPEG はデフォルトで白を補填、`format=jpeg,black` や `#RRGGBB` で色変更可；JPEG/WebP は quality で保存、PNG は可逆）、`quality=1-100` は再エンコード品質を上書き（デフォルト 95、範囲外はエラー）、`scale=NNN%` はパーセント相対拡縮（ページ間の比率を維持、例 `200%`=2 倍、1~1000）または `scale=NNNw` は目標幅ピクセルに統一（高さは元の比率、例 `1200w`、1~100000、二つの構文は二択）、`trim[=許容差]` は辺縁の均一背景色を検出して白辺を自動トリミング（値なし/auto = 0.05、安全マージンで誤トリミング防止）、`strip` は画像の全 EXIF メタデータを除去。固定順序 `rotate→flip→grayscale→format→quality→scale→trim→strip` は記述順に関係なし。三つの入口：mobi→cbz 変換出力前 / `--repack` パッキング前 / 既存 `.cbz` のその場修正（CBZ 方向修正モード）。`--dry-run`/`--json`/`--json-out`/`--log` と連動
- **見開き検出** — `--double-page` で跨ぎページ（見開き）を自動判定（幅/高 ≥ 閾値、デフォルト 2.0）。有効時はページ毎に DoublePage を書き込みます（Manga 要素は書きません）。値なし / `auto` で有効、数値で閾値調整、`off` / `no` / `0` で無効
- **小画像の破棄** — `--drop small[=比率]` で面積が明らかに小さい画像（幅×高さ < 面積中央値×比率、デフォルト 0.5）を除外します（表紙サムネイル等）。破棄後は PageCount を実画像数で再計算。値なし / `auto` = 0.5、0〜1 の数値で比率調整、`off` / `no` / `0` で無効。旧 `--drop-small` は隠しエイリアス（`--drop small` と同等）として引き続き利用可
- **ComicInfo フィールド上書き** — `--setinfo FIELD=VALUE` で ComicInfo フィールドを上書き/追加します（最優先）。VALUE は固定値 / `%series` / `%number` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` プレースホルダに対応し、複数指定可能。`FIELD` は ComicInfo 標準フィールドのホワイトリスト内である必要があります（単純フィールド 39 個、複雑な `Pages` は除外。ホワイトリスト外は warning を出して無視）。既存 `.cbz` 入力では `%series`/`%number`/`%volume` は ComicInfo 内の明示的な Series/Number/Volume を優先して読み、欠落時のみファイル名推測へフォールバックします。入力が既存 `.cbz` の場合はその ComicInfo.xml を直接変更します（未指定フィールドは元の値を保持、一時ファイル + アトミック置換で書き込み）
- **ログの自動命名** — `--log` をファイル名なしで指定すると `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（カレントディレクトリ）を自動生成します
- **解凍表示** — `--unpack` は変換せず解凍のみ行い、各ソースファイルの「元名_拡張子」サブディレクトリへ出力します（例 vol.cbz → vol_cbz/。既存時は `(2)(3)` と自動採番）。mobi は extract で完全な構造を保持、cbz は extractall（zip-slip パストラバーサル対策付き）。`--unpack` または `--setinfo` 指定時は `.cbz` 入力も収集します
- **所要時間** — ファイルごとの変換時間をリアルタイム表示し、集計下部に合計を出します
- **JSON 構造化出力** — `--json` は実行結果を JSON として stdout に出力（変換/変更モードは全体の 1 行コンパクト JSON、検査モードはファイルごとに 1 行のスリム JSON。AI / パイプライン / スクリプト向け、有効時は人間向けテキスト出力を抑制）。`--json-out [FILE]` は構造化結果を JSON ファイルに書き込み（インデント形式、ファイル名省略時はタイムスタンプ付きファイルを自動生成、`--log` と同一挙動）。両者は併用可能で、変換モード / `--setinfo` 変更モード / `--inspect` 検査モードの全てに対応
- **出力リネーム** — `--rename[=TEMPLATE]` で出力 CBZ のファイル名をリネーム（デフォルトオフ）：無値 = デフォルトテンプレート（シリーズ名 + 自動マーカー接頭辞。タイプに応じて `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]` を自動選択、連話 `話005-006` は `[Ch.5-6]`）。テンプレートは `%series` / `%number` / `%volume` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` と `%03number` ゼロ埋めをサポート。`%description` はファイル名には推奨しません（内容が長くなりがち）。`%subN_M` と組み合わせて切り出すと良いでしょう。入力が既存 `.cbz` の場合は独立リネームモード（リネームのみ・変換なし）
- **色制御** — `--no-color` で ANSI カラー出力を無効化（端末が対応していても着色しない）。ログ / JSON / パイプ出力は元々色なし
- **撞名分類プロンプト** — `--rename` スキップ時に 2 種類のプロンプトを区別：対象ファイルが既に存在（`--overwrite` を提案）と本バッチ内の撞名（命名テンプレートの調整を提案）。JSON の `reason` フィールドにそれぞれ `existing` / `conflict` を書き込み。dry-run プレビューでは `[スキップ予定]` を撞名クラス別に着色（ディスク既存同名 = 黄、バッチ内撞名 = マゼンタ。TTY かつ `--no-color` 未指定時のみ）。非 dry-run のサマリーはスキップ総数を「ディスク既存同名 N / バッチ内撞名 M」に分解し、スキップファイル一覧もクラス別にグループ化して表示
- **デバッグモード** — `--debug` で stderr に debug レベルログを出力（デフォルトは静か、指定時のみ出力。`--quiet` と同時指定でも debug は出力される）。問題の切り分けに便利

## 対応画像形式

変換時に認識・パッケージ化する形式: `.jpg` / `.jpeg` / `.png` / `.gif` / `.webp` / `.bmp` / `.tiff` / `.tif`

## 環境要件

- Python 3.10+
- 実行時依存: `mobi`（必須）
- オプション: `pillow`（`--img-edit` 画像パイプライン使用時のみ必要）、`tqdm`（プログレスバー。無い場合は簡易テキスト進捗に自動フォールバック）

## インストール

```bash
pip install mobi          # 必須
pip install pillow tqdm   # 任意: --img-edit パイプライン / プログレスバー（無ければテキスト進捗にフォールバック）
```

## 使い方

### 単一ファイルを変換

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi"
```

### ディレクトリ全体を一括変換（.mobi / .azw / .azw3 / .epub を再帰検索）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary"
```

### 変換成功後に元の電子書籍を削除

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --delete
```

### 二重ディレクトリ mobi で mobi7 を保持

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --prefer mobi7
```

### ディレクトリ内の未収集の余分な画像を破棄

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --drop
```

### 既存の cbz がある場合に強制再生成

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --overwrite
```

### 単一ファイル変換のタイムアウトを制限（破損ファイルによるバッチ停止を防止）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --timeout 300
```

### カスタムディレクトリへ出力（デフォルトで相対サブディレクトリ構造を保持）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --output-dir "E:\CBZ_Output"
```

### フラット出力（すべての CBZ を出力ディレクトリ直下へ）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --output-dir "E:\CBZ_Output" --flatten
```

### ドライラン: 変換フローを表示するのみ（実際には変換しない）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --dry-run
```

> 既存 CBZ に対して `--setinfo` と併用すると、正式実行・dry-run の両方で、実行前にファイルごとに変更予定の ComicInfo フィールドを列挙します（`~ フィールド: 旧 → 新`）。新規追加のみのフィールドは `+`、値が変わらないフィールドは省略されます。

### サイレントモード + ログへ書き込み

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --quiet --log convert.log
```

### 簡潔な集計（大規模ディレクトリ、成功/スキップは件数のみ）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --quiet --short-summary --log convert.log
```

### zip 圧縮を有効化（PNG ソースでサイズ削減しやすい）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --compress 9
```

### 検査モード: 1 冊の内部情報をサンプル確認（デフォルト）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --inspect
```

### 全電子書籍の内部情報を検査

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --inspect all
```

### ComicInfo フィールドを上書き/追加（複数指定可、最優先）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --setinfo "Title=Sample Series" --setinfo "Number=%number" --setinfo "Summary=Vol. 1, First Edition"
```

> 補足: `--setinfo` はカンマの直後に「フィールド名=」が続く場合のみ分割します。値自体に `Key=...` 構造が含まれる場合は、誤分割を避けるため複数回の `--setinfo` で渡してください。入力ディレクトリに既存 `.cbz` と `.mobi` が混在する場合、`--setinfo` 有効時は `.cbz` の ComicInfo.xml を直接変更し（未指定フィールドは元の値を保持）、それ以外のファイルは通常どおり変換します。

### 解凍表示（変換せず解凍のみ、同名サブディレクトリへ出力）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --unpack
```

### その場で向きを修正（向き異常ページを EXIF で自動回転、CBZ その場修正モード）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.cbz" --img-edit rotate
```

`--img-edit` 画像処理パイプラインは mobi→cbz 変換出力前と `--repack` パッキング前にも適用されます。rotate 値なし（auto）は EXIF Orientation で向き異常画像を自動回転します（v3.6.0）。

### JSON 構造化出力（stdout 1 行 / ファイル書き込み）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --json
python manga-mobi2cbz.py "D:\ComicsLibrary" --json-out
python manga-mobi2cbz.py "D:\ComicsLibrary" --json --json-out inspect_result.json
```

> 補足: `--json` / `--json-out` は「変換」「CBZ 変更」「検査」「dry-run」の 4 モードで構造化結果を出力します。`--unpack` モードでは出力しません。変換/変更モードの `--json` は全体の 1 行コンパクト JSON、検査モードはファイルごとに 1 行のスリム JSON（status/series/number/source/page_count/drm、status は ok/drm/invalid/noimg/timeout/fail）、`--json-out` は全量（spine/toc と summary を含む）を書き込みます。dry-run モードでは各レコードに `dry_run: true` フラグが付き、ステータスは `will_skip` / `pending` です。プログレスバーと人間向け表示は stderr、JSON は stdout に書き込まれ自然に分離しますが、`2>&1` で結合リダイレクトするとプログレスバーが JSON に混入するため、その場合は `--no-progress` を併用してください。

### バージョン確認

```bash
python manga-mobi2cbz.py --version
```

## パラメータ説明

| パラメータ | 説明  |
| --- | --- |
| `target` | 電子書籍ファイルのパス、電子書籍（.mobi/.azw/.azw3/.epub）を含むディレクトリ、または `*` / `?` を含むグロブパターン（例: `*.epub`、`巻*/001.mobi`）；現在のディレクトリは `.` を指定（必須） |
| `--language LANG` | 出力言語。`auto` はシステム locale で自動選択（簡体字→zh-CN、繁体字 zh-TW/zh-Hant→zh-TW、日本語 ja/Japanese→ja、その他→en）。または `zh-CN` / `zh-TW` / `ja` / `en` を指定（デフォルト `auto`）。一般的な表記も許容: `zh`/`cn`→zh-CN、`zhtw`/`tw`→zh-TW、`jp`→ja、`eng`→en |
| `--top-only` | target ディレクトリ直下の電子書籍のみ処理（サブディレクトリへ再帰しない） |
| `--delete` | 変換成功後に元の電子書籍を削除（デフォルト: 削除しない） |
| `--prefer` | 二重ディレクトリ mobi で保持する側: `auto` / `mobi7` / `mobi8`（デフォルト `auto`）。`auto` は mobi8 を優先し、mobi8 に画像がない場合は mobi7 に自動フォールバック。`mobi7`/`mobi8` を明示指定した場合も、選択ディレクトリに画像がないときはもう一方へフォールバック |
| `--drop [EXPR]` | 統一破棄エントリ（`nargs='?'`、繰り返し指定 = OR 和集合）。値なし = `extra`（未収集の余分な画像をすべて破棄。デフォルトは cbz 末尾に追記）。値を指定すると条件で破棄 — 形式ワード / 条件ワード（`res` / `size` / 向き / モード / ビット深度 / タグ: `double` / `thumbnail` / `animated` / `cover` など、向きクラス `landscape`/`portrait`/`square` 横向き/縦向き/正方形）/ `small[=比率]` 小画像。複数条件はカンマ = OR、`+` = AND、`-` 接頭辞 = 除外。例: `--drop gif,extra`、`--drop small=0.4`、`--drop 表紙+overscale`。`off` / `no` / `0` で無効化。実行順: 余分な画像の破棄 → 重複除去 → 条件フィルタ → 小画像の破棄。破棄したファイル名を 1 件ずつ列挙（`--short-summary` 併用時は件数のみ）。旧 `--drop-extra` / `--drop-small` は本オプションに統合（隠しエイリアスとして引き続き利用可） |
| `--overwrite` | 対象 cbz が既にある場合に強制再生成（デフォルト: スキップ） |
| `--ext-priority EXTS` | 同一ディレクトリ・同名（拡張子のみ異なる）とき保持する形式。カンマ区切りで優先度が高い順。受け付ける値は `mobi` / `azw` / `azw3` / `epub`。デフォルト `azw3`。未指定分は azw3→epub→mobi→azw にフォールバック。`--prefer`（mobi7/mobi8）とは無関係 |
| `--timeout` | 1 ファイルあたりのタイムアウト秒数。超過分はスキップして失敗計上（デフォルト 600、`0` は無制限） |
| `--min-size BYTES` | 指定バイト未満を除外。数値省略時は 1000、`0` で無効、オプション未指定でサイズフィルタオフ |
| `--output-dir DIR` | CBZ の出力先（自動作成）。デフォルトで入力の相対サブディレクトリ構造を保持（例: `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`）。`--flatten` でルート直下にフラット化 |
| `--flatten` | `--output-dir` と併用時のみ有効。すべての CBZ を出力ルート直下へフラット化し、同名ファイルは `--overwrite` 未指定時はスキップ（SKIP）、指定時は優先名を上書き。単独指定（`--output-dir` なし）はエラー終了 |
| `--progress` | プログレスバー表示ポリシー。`auto` は stderr が TTY かつファイル数≥2 かつ `--json`/`--json-out` 未使用時に表示、`on` は強制表示、`off` は強制オフ（デフォルト `off` で非表示）。stderr のみで `--log` には入らない |
| `--no-progress` | プログレスバーを強制オフ（`--progress off` と同等、旧コマンド互換） |
| `--dry-run` | スキャンと変換フロー表示のみ。解凍・パッケージ化・出力ディレクトリ作成はしない |
| `--rename[=TEMPLATE]` | 出力 CBZ のファイル名をリネーム（オプションのテンプレート、デフォルトオフ）：無値 = デフォルトテンプレート（シリーズ名 + 自動マーカー接頭辞。タイプに応じて `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]` を自動選択、連話 `話005-006` は `[Ch.5-6]`）。テンプレートは `%series` / `%number` / `%volume` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` と `%03number` ゼロ埋めプレースホルダをサポート。出所優先順：ファイル名推測 > ファイル内蔵メタデータ（OPF / ComicInfo.xml）フォールバックで `--setinfo` は関与しない。入力が既存 `.cbz` の場合は独立リネームモード（リネームのみ・変換なし、他モードと併用可）。`%description` はファイル名には推奨しません（内容が長くなりがち）。`%subN_M` と組み合わせて切り出すと良いでしょう。スキップ時は 2 種類のヒントを区別（対象ファイルが既に存在 → `--overwrite` を提案、本バッチ内の撞名 → テンプレート調整を提案）、JSON `reason` は `existing` / `conflict`。dry-run プレビューでは `[スキップ予定]` をクラス別に着色（ディスク既存同名 = 黄、バッチ内撞名 = マゼンタ、TTY かつ `--no-color` 未指定時のみ）、サマリーはスキップ数を「ディスク既存同名 N / バッチ内撞名 M」に分解してクラス別にグループ表示。`--dry-run` と併用して先にプレビュー推奨 |
| `--no-color` | ANSI カラー出力を無効化（端末が対応していても着色しない）。ログ / JSON / パイプ出力は元々色なし |
| `--quiet` | エラーと最終集計のみ表示 |
| `--debug` | デバッグモード。stderr に debug レベルログを出力（デフォルトは静か、指定時のみ出力。`--quiet` と同時指定でも debug は出力される） |
| `--short-summary` | 成功/スキップは件数のみ（失敗は常にフルパス） |
| `--compress LEVEL` | zip 圧縮レベル 0–9。`0`=無圧縮（デフォルト）、`1–9`=deflate（PNG 向け。高いほど小さいが遅い） |
| `--inspect [MODE][,FILTER]` | 検査モード。`sample` で 1 冊ランダム検査（デフォルト）、`all` で全冊検査。フィルタを付与可能（例: `all,small=0.6`）で、条件に一致した画像の枚数 + ファイル名一覧（サイズ付き）を出力。位置引数が単一ファイルの場合はそのファイルを直接検査し、内部情報のみ読取（CBZ 非生成、一時ディレクトリは終了時に削除）。画像プレビューは先頭 5 枚を表示し、それ以上ある場合は英語の省略記号行 `...`（例: `...（全 N 枚）`）を追記。目次（NCX）/ nav プレビューの省略も英語 `...` に統一。本単位サマリーに「向き異常 N 枚（rotate=auto で回転予定）」行を追加（`--json-out` は `rotate_count` フィールド）、フィルタは方向ワードをサポート（例: `all,方向`）（v3.6.0） |
| `--inspect-all` | 全冊を検査（`--inspect all` と同等、旧コマンド互換） |
| `--no-comicinfo` | ComicInfo.xml を生成しない（デフォルト: CBZ ルートに Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary を書き込み） |
| `--setinfo FIELD=VALUE` | ComicInfo フィールドを上書き/追加（複数指定可、最優先）。`FIELD` は ComicInfo 標準フィールドのホワイトリスト内である必要があります（39 個の単純フィールド、複雑な `Pages` は除外。ホワイトリスト外は warning を出して無視）。`VALUE` は固定値 / `%series` / `%number` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` プレースホルダに対応（`%subN_M`=N 文字目から M 文字、1-based。値全体が単一の既知プレースホルダで対応値が無い場合のみそのフィールドを書き込まない）。プレースホルダは固定テキストと混在可能（例: `%writer·重制`、`第%number话`）。混在時は欠落値を空文字列としてレンダリング。スマート分割: カンマの直後に `フィールド名=` が続く場合のみ分割し、それ以外はカンマを値の一部とみなす（例: `Summary=Vol. 1, First Edition` は分割しない）。既存 `.cbz` 入力では `%series`/`%number`/`%volume` は ComicInfo 内の明示的な Series/Number/Volume を優先して読み、欠落時のみファイル名推測へフォールバックします。入力が既存 `.cbz` の場合、その ComicInfo.xml を直接変更（未指定フィールドは元の値を保持）。値に `Key=` が含まれる場合は複数回の `--setinfo` で渡す。有効時は入力に混在する `.cbz` を直接変更し、他のファイルは通常どおり変換。`Manga` はデフォルトで書き込まず、`--setinfo Manga=Unknown\\|No\\|Yes\\|YesAndRightToLeft` で明示指定（公式 v2.0 の列挙のみ）。`CommunityRating`（0-5）/ `MainCharacterOrTeam` / `Review` の 3 つの公式フィールドにも対応 |
| `--unpack` | 解凍表示: 変換せず解凍のみ。各ソースファイルの「元名_拡張子」サブディレクトリへ出力（例 vol.cbz → vol_cbz/、元ファイルと衝突しない。既存時は `(2)(3)` と自動採番。`--output-dir DIR` で解凍出力先を指定可、未指定時は各ソースファイルのあるディレクトリが既定（v3.6.0））。mobi は extract で完全な構造を保持、cbz は extractall（zip-slip パストラバーサル対策付き）。`--unpack` / `--setinfo` 指定時は `.cbz` 入力も収集 |
| `--repack` | 再パックモード: 解凍済みの `_cbz` ディレクトリ（ディレクトリ名が `_cbz` で終わる、例 vol_cbz/）を CBZ に再パックし、出力名は元のファイル名に戻します（vol_cbz → vol.cbz）。単一ディレクトリまたは親ディレクトリの一括処理に対応し、実行前に処理リストを表示（各行 `解凍ディレクトリ名 → 出力.cbz`）。ディレクトリ内の ComicInfo.xml は既存ならそのまま持ち越し、無ければ基本版を生成。`--setinfo` で上書き・追加可、`--no-comicinfo` で無効化。既存出力はデフォルトでスキップ、`--overwrite` で上書き。`--rename` は本モードでは適用外 |
| `--double-page VALUE` | 見開きページ検出: 未指定または `auto` で有効（閾値 2.0。幅/高さ ≥ 閾値の横長見開き大画像を検出し、ComicInfo にページごとの `Type="DoublePage"` を書き込む。`Manga` は自動で宣言しない）。数値指定（例 `2.5`）で有効化し閾値を調整。`off` / `no` / `0` で無効化。不正値はエラー |
| `--drop small[=比率]` | 小画像の破棄: 変換時に他の画像より明らかに小さい画像（表紙サムネイル / 版権ページなど）を除外。幅×高さ < 面積中央値 × 比率 で小画像と判定。`small` 値なし / `auto` はデフォルト比率 0.5、`0~1` の数値（例 `--drop small=0.4`）で比率調整、`off` / `no` / `0` で無効化（デフォルト無効、既存動作は不変）。破棄後は ComicInfo `PageCount` を実画像数で再計算。集計 / `--log` / `--json` に「破棄した小画像」カウントを追加（`--json` は `dropped_small` フィールド）し、破棄したファイル名を 1 件ずつ列挙（`--short-summary` 併用時は件数のみ）。`--inspect` プレビューで「--drop small 有効時は N 枚破棄されます」と表示。横長見開き（幅は小さくない）は誤破棄されない。変換モードのみ有効。旧 `--drop-small` は `--drop small` と同等（隠しエイリアスとして引き続き利用可） |
| `--img-edit [EDIT]` | 画像処理パイプライン（繰り返し指定可、値内の '+' で分割してフラット化）：`rotate[=auto\|90\|180\|270]` EXIF Orientation をピクセルに焼き込み再エンコード（値なし = auto、Orientation≠1 の画像のみ）、`flip=x\|y\|both` 鏡像反転、`grayscale` グレースケール（常に flip の直後）、`format=jpeg\|png\|webp` 形式変換（透明→JPEG はデフォルトで白補填、`format=jpeg,black` や `#RRGGBB` で変更可）、`quality=1-100` 再エンコード品質（デフォルト 95）、`scale=NNN%` または `scale=NNNw` 拡縮、`trim[=許容差]` 白辺トリミング（値なし / auto = 0.05）、`strip` EXIF 全除去。固定順序 `rotate→flip→grayscale→format→quality→scale→trim→strip` は記述順に関係なし。三つの入口: mobi→cbz 変換出力前 / `--repack` パッキング前 / 既存 `.cbz` のその場修正。`--dry-run` / `--json` / `--json-out` / `--log` と連動 |
| `--pages PAGES` | ページ指定処理（繰り返し指定可、値内のカンマ区切りで引用符不要）：指定したページ番号のみ処理。ページ番号は 1 始まり（第 1 ページ = 巻内の 1 枚目）。単一 `5`｜閉区間 `1-3`｜開区間 `7-*`（* = 最終ページ）をサポートし、カンマで混在可（例: `1-3,5,7-*`）。範囲外ページは無視して 1 ページごとに警告、全範囲外 / 空ヒットはエラー終了。`--img-edit`（選択ページのみパイプライン処理）、`--drop`（AND 共存: ページ確定後にフィルタ）、`--unpack` / `--repack`（選択ページのみ）と連携（v3.6.0）。フィルタ語でもページを選択可能：`name=` の値に `*` か `?` を含むと glob 一致（例 `name=*_表紙*`、`name=p00?`）、他の語彙は `--drop` と同じ |
| `--list-images [FILTER]` | 画像一覧の読み取り専用表示: 値なし = 対象電子書籍の全画像を列挙。値を指定すると FILTER 式（`--drop` と共通のフィルタエンジン: 形式 / `extra`（OPF spine に無い余分な画像）/ `res` / `size` / 向き / モード / ビット深度 / タグ / `small[=比率]`、向きクラス `landscape`/`portrait`/`square` 横向き/縦向き/正方形 にも対応。カンマ = OR、`+` = AND、`-` 接頭辞 = 除外。例: `jpeg,size>1MB`、`-webp`）。読み取り専用スキャン — 変換なし、CBZ 生成なし、ComicInfo なし、ファイル書き込みなし。CBZ は zip 直接読み取り（目次列なし / 変換状態タグなし）。ファイルごとに（No. / ファイル名 / 解像度 / サイズ / モード・深度 / 向き / 目次 / タグ）の一覧 + 全量統計ブロック（フィルタの影響を受けず常に全量）。EXIF Orientation≠1 の画像には `[回転N]` マーク（N=2~8、正常=1 は無印）を付け `[異常]` 集計にも加算。方向ワードによるフィルタ（同義: orient/orientation/direction、日本語=方向/方向異常）を新設: 値なし = 方向異常の全画像を選択（rotate=auto で回転予定）、値あり = EXIF Orientation の正確一致（例: `方向=6`）。`--json-out` の画像レコードに `orientation` フィールドを追加（v3.6.0）。`--json`（ファイルごとに 1 行のスリム JSON）/ `--quiet`（明細抑制、件数のみ）と併用可。`--inspect` とは完全に独立 |
| `--log FILE` | 全出力を指定ログへ追記。ファイル名なしで指定すると `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（カレントディレクトリ）を自動生成 |
| `--json` | 実行結果を JSON として stdout に出力（AI / パイプライン / スクリプト向け）。有効時は人間向けテキスト出力（プログレスバー / emit 表示 / 集計）を抑制。変換/変更モードは全体の 1 行コンパクト JSON、検査（`--inspect`）モードはファイルごとに 1 行のスリム JSON（status/series/number/source/page_count/drm）。dry-run モードでは `dry_run` フラグ付きで出力（ステータス `will_skip` / `pending`）、unpack では出力しない。`--json-out` と併用可。プログレスバーは stderr に書き込まれ混ざらないが、2>&1 結合リダイレクトでは混入する |
| `--json-out [FILE]` | 構造化結果を JSON ファイルに書き込み（インデント形式）。ファイル名なしで指定するとタイムスタンプ付きファイル（カレントディレクトリ）を自動生成、`--log` と同一挙動。`--json` と併用可。変換/変更モードはファイル単位の結果、検査（`--inspect`）モードは全量（spine/toc と summary を含む）を書き込み |
| `--version` | バージョン番号を表示 |

## パラメータとモードの有効行列

一部のパラメータはモードによって効きません。該当しないモードでは黙って無視されます（エラーも警告も出ません）。以下が正となります：

| パラメータ | mobi→cbz 変換 | `--unpack` | `--list-images` | `--repack` | CBZ その場修正 |
| --- | --- | --- | --- | --- | --- |
| `--img-edit` | ✅ 出力前パイプライン | ⏭ 無視 | ⏭ 無視 | ✅ 画像書き込み前にパイプライン | ✅ その場再エンコード |
| `--drop` | ✅ 破棄/フィルタ | ⏭ 無視 | ⏭ 無視（読み取り専用フィルタは FILTER 語を使う） | ⏭ 無視 | ⏭ 無視 |
| `--pages` | ✅ 選択ページのみ | ✅ 選択ページのみ残す | ⏭ 無視 | ✅ 選択ページのみパッキング | ✅ 選択ページのみ |
| `--double-page` | ✅ DoublePage マーク書き込み | ⏭ 無視 | ⏭ 無視 | ✅ ComicInfo 引き継ぎ時は既存マーク維持 | ⏭ 無視 |
| `--rename` | ✅ 出力ファイル名変更 | ⏭ 無視 | ⏭ 無視 | ⏭ 該当なし | ✅ その場リネーム |
| `--setinfo` | ✅ ComicInfo 上書き | ⏭ 無視 | ⏭ 無視 | ✅ ComicInfo 上書き/生成 | ✅ その場 ComicInfo 編集 |
| `--no-comicinfo` | ✅ ComicInfo 生成なし | ⏭ 無視 | ⏭ 無視 | ✅ ComicInfo 引き継ぎなし | ⏭ 無視 |
| `--delete` | ✅ 成功後に元ファイル削除 | ⏭ 無視 | ⏭ 無視 | ⏭ 該当なし | ⏭ 該当なし |

> 注: `--double-page` / `--rename` / `--setinfo` / `--no-comicinfo` / `--delete` の行は実際のコード挙動に基づきます。`--unpack` は既存 `.cbz` / `.epub` 入力（プレーン zip 解凍）も扱い、`--pages` 指定時は解凍後に選択ページの画像だけを自然ソート順の番号で残します。

## 出力

- デフォルトでは `.cbz` は元の電子書籍と同じディレクトリに置きます。`--output-dir` 指定時はそのディレクトリへ出力します（自動作成）。デフォルトで入力の相対サブディレクトリ構造を保持し、`--flatten` でルート直下にフラット化します（同名ファイルは `--overwrite` 未指定時はスキップ）
- 既存の `.cbz` はデフォルトでスキップし、上書きしません。`--overwrite` で強制再生成できます
- 0 バイト / ヘッダ破損は事前チェックでスキップし、フルパスと理由をログに出します
- ファイルごとの所要時間をリアルタイム表示し、集計下部に合計を出します
- 失敗したファイルはエラーを表示しますが、他ファイルの変換は継続します

## JSON 出力契約

`--json` / `--json-out` の構造化出力において、`status` フィールドは機械的な利用側との契約です。モード別の値は以下の通り:

| モード | `status` の値 | 失敗の詳細 |
| --- | --- | --- |
| 変換（デフォルト） | `ok` / `skip` / `fail` / `timeout` | 失敗理由は `reason` フィールド: `drm` / `corrupt` / `verify` / `comicinfo` / `other` |
| 検査（`--inspect`） | `ok` / `drm` / `invalid` / `noimg` / `timeout` / `fail` | `--json` はファイルごとに 1 行のスリム JSON、`--json-out` は全量（spine/toc と summary を含む）を書き込み |
| 変更（`--setinfo`） | `modified` / `nochange` / `fail` | 失敗理由は `reason` フィールド |
| dry-run（`--dry-run`） | `will_skip` / `pending` | 各レコードに `dry_run: true` フラグが付き、機械側で実実行と区別可能 |

各レコードの固定フィールドは `source` / `status` / `target` / `reason` / `elapsed_sec`。変換モードでは追加で `series_source` / `number_source` / `cover_source` / `dropped_small` を持ちます。

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
A: v1.9.0 以降、`--output-dir` はデフォルトで入力の相対サブディレクトリ構造を保持します（旧版の一律フラットから破壊的変更）。フラット化したい場合は `--flatten` を追加してください。旧コマンド `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output` は `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output --flatten` に変更すると旧動作を復元できます。

**Q: .azw / .azw3 には対応していますか？**  
A: 対応しています。v1.8.0 以降、入力は `.mobi` / `.azw` / `.azw3` で、同じ変換パイプラインを使います。同一ディレクトリで同名・異拡張子のときはデフォルトで azw3 を残し、`--ext-priority` で変更できます。

**Q: EPUB には対応していますか？**
A: 対応しています。v2.4.0 以降、入力は `.mobi` / `.azw` / `.azw3` / `.epub` です。EPUB は ZIP コンテナのため zipfile で安全に解凍し、OPF spine 抽出パイプラインを再利用します。表紙は EPUB2（`<meta name="cover">`）と EPUB3（`properties="cover-image"`）の両方に対応。EXTH ヘッダが無いため、メタデータは OPF の `dc:` フィールドから読み取ります。`--prefer` は EPUB では静かに無視されます。暗号化された EPUB（Adobe DRM など）は内容を解析できず、画像なし/有効なメタデータなしとしてスキップされます。変換前に DRM を除去してください。

## 更新履歴

更新履歴は [CHANGELOG_ja.md](CHANGELOG_ja.md) を参照してください。

## License

このプロジェクトは [GPL-3.0](./LICENSE) ライセンスで提供されます。

### サードパーティ依存ライセンス

本ツールは実行時に mobi ライブラリ（v0.4.1、Titusz Pan メンテナンス版）に依存しており、そのライセンスは GPL-3.0-only です。配布時は GPL-3.0 の要件に従ってください。