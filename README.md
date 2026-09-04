**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md

# manga-mobi2cbz

一款专为Kindle漫画打造的批量转换CLI工具，一键将无DRM MOBI / AZW / AZW3 / EPUB 电子书导出标准CBZ漫画包。
原生遵循OPF Spine官方阅读顺序提取图片，内置封面自动修复、同卷多格式去重、批量超时防护、文件完整性校验、多语言自动输出等全套实用能力；附带 `--inspect` 探查模式，无需打包即可查看漫画元数据、分辨率、NCX目录与DRM状态，全平台通用，批量整理漫画库高效稳定。

> ⚠️ 仅支持已去除 DRM 的 Kindle 漫画，商店加密电子书无法解析。
> 
> ⚠️ 代码完全由 AI 生成，本人无法逐行审计，请自行评估风险后使用。
> 
> 📝 说明：本项目为个人自用，用于保存文件转换时AI生成的脚本以便于后期使用。
> 
> **项目由来**：最初为处理个人Kindle漫画，每次转换都让AI生成脚本处理，为便于复用和避免脚本丢失，便上传到了GitHub。
> 后续使用中陆续遇到顺序错乱、封面丢失、批量中断等问题，于是不断向AI提出修改需求。由于不懂代码，为了验证可靠性，逐渐形成了将同一段代码交给不同AI交叉验证的工作方式。项目从最初的一次性脚本，经反复迭代，逐步演变为现在的形态。代码完全由AI生成，本人仅负责需求与验收，它不专业，但已比最初完善很多。如果你也有类似需求，欢迎使用；若发现问题，也欢迎反馈，我会继续让AI修。

## 功能特点

- **批量转换** — 支持单个文件或整个目录递归转换 `.mobi` / `.azw` / `.azw3` / `.epub` 电子书
- **OPF spine 排序** — 优先按 OPF spine 顺序提取图片，保证真实阅读顺序；无 OPF 时兜底按文件名自然排序
- **封面兜底** — 自动扫描文件名含 cover/front 的图片；封面已在 spine 列表中则以列表顺序为准，仅缺失时插入首位补齐
- **目录对齐兜底** — 目录图片数与收集数不一致时，多出的图片默认按自然排序追加到 cbz 末尾；`--drop` 可改为放弃，处理结果会逐条列出多余图片文件名（`--short-summary` 下只显数量）
- **双目录去重** — 自动识别 mobi7/mobi8 双目录，默认 `auto`：优先保留 mobi8（画质可能更好），mobi8 无图片时自动回退 mobi7；`--prefer mobi7|mobi8` 可强制指定，指定目录无图片时自动回退另一份
- **轻量多语言** — `--language auto|zh-CN|zh-TW|ja|en` 切换输出语言（默认 `auto` 按系统 locale 自动判定：简体中文归 zh-CN、繁体中文归 zh-TW、日文归 ja、其余归 en）；全量输出文案与 `--help` 随语言翻译，参数名/枚举/专有词不翻译
- **同名扩展名去重** — 同目录下仅扩展名不同（如 `Vol.01.mobi` + `Vol.01.azw3`）时只保留一份，`--ext-priority` 控制保留优先级（默认 azw3）
- **自然排序** — 按页码自然排序，避免 `10.jpg` 排在 `2.jpg` 前面
- **完整性校验** — 转换后自动校验 CBZ 文件，损坏则删除并提示
- **ComicInfo.xml 元数据** — 默认在 CBZ 根目录生成 ComicInfo.xml（UTF-8，含 XML 声明），写入 Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary 漫画元数据；Series/Number 由文件名高置信度推断（支持 `001` / `01` / `1` / `Vol.01` / `Vol 01` / `Volume 01` / `第 01 卷` 等形式），无系列名的卷标记（如 `Vol.01` / `01巻`）不推断，无法高置信度判断时省略（宁缺勿错）；无可靠来源的字段不生成空标签；`--no-comicinfo` 关闭生成
- **无压缩打包** — 图片已是压缩格式，ZIP 默认仅存储不压缩，速度快、体积小
- **可选压缩** — `--compress LEVEL` 启用 deflate 压缩（1-9），PNG 源漫画可显著减小体积，级别越高越小但越慢；JPEG 源收益有限，不建议开启（默认 `0` 不压缩）
- **检查模式** — `--inspect` 默认随机抽查 1 个电子书（`sample`），`--inspect all` 全量检查（等价旧 `--inspect-all`），只解包读取内部信息不生成 CBZ：基础检查（魔数/大小/DRM 双重判断）、EXTH 元数据（标题/作者/语言/出版日期/出版社/ISBN/ASIN/版权，读到才显示）、双目录标记、OPF 与 spine 提取数（前 5 文件名竖排预览）、目录(NCX) 条目数与预览、目录全部图片数、封面（OPF guide 官方引用优先，未命中回退文件名匹配）、图片格式分布、主流分辨率（主流高/宽 + 另一维范围）、末尾分辨率分布摘要（主分辨率张数占比 + 异常小图数）、压缩建议；DRM 标记仅作信息降级不阻断检查——有标记仍尝试解包，解出图片→判为可读并带 drm 标记，仅解包失败且图片 0→判 DRM；结束后自动清理临时目录
- **可选删除原文件** — `--delete` 参数转换成功后自动删除原始电子书
- **强制覆盖** — `--overwrite` 参数对已存在的 cbz 强制重新生成，更新漫画后无需手动删旧文件
- **单文件超时保护** — `--timeout` 参数限制单个文件转换时长，损坏/加密/超大电子书导致底层解包无限阻塞时自动跳过并计入失败，不再卡死整批转换（默认 600 秒，`0` 表示不限制）
- **静默模式** — `--quiet` 批量转换只显示错误与汇总，不再刷屏；`--log FILE` 可将全部输出追加写入日志文件
- **调试模式** — `--debug` 向 stderr 输出 debug 级日志（默认静默，仅在指定时输出；与 `--quiet` 同给时 debug 级仍输出），便于排查问题
- **精简汇总** — `--short-summary` 成功/跳过/预处理跳过文件只显示数量不列出路径（失败文件始终全路径列出），与 `--quiet` 互补，适合大批量目录
- **DRM 加密识别** — 遇到 DRM 加密的 Kindle 漫画时明确提示无法解密，避免静默失败
- **路径大小写兼容** — 封面比对与目录对齐使用归一化小写路径，Windows 不区分大小写的文件系统下不会因大小写命名差异误判重复/遗漏
- **输出时间戳** — 每条输出自动追加 `[YYYY-MM-DD HH:MM:SS]` 前缀，控制台与日志文件一致，方便定位每次转换的执行时刻
- **自定义输出目录** — `--output-dir DIR` 将 CBZ 输出到指定目录（自动创建），默认保留相对输入的子目录结构（如 `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`）；加 `--flatten` 平铺到目录根下，同名文件未指定 `--overwrite` 时跳过（SKIP）
- **预处理过滤** — 0 字节、文件头损坏（偏移 60 处无 `BOOKMOBI` 魔数）的电子书在预处理阶段直接跳过，日志输出跳过文件完整路径与原因
- **大小下限过滤** — `--min-size BYTES` 过滤小于指定字节数的电子书（不带数字默认 1000，`0` 关闭，不传则关闭大小过滤），兜住头部恰好完整但内容被截断的边缘损坏样本
- **试运行模式** — `--dry-run` 只扫描与打印转换流程，不实际解压打包，适合先确认转换结果
- **输出重命名** — `--rename[=TEMPLATE]` 重命名输出的 CBZ 文件名（默认关闭）：无值 = 默认模板（系列名 + 自动标记前缀，前缀按类型自动选 `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`，连话 `話005-006` 标 `[Ch.5-6]`）；模板支持 `%series` / `%number` / `%volume` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 及 `%03number` 补零占位符；来源优先级：文件名推断 > 文件自带元数据（OPF / ComicInfo.xml）兜底，`--setinfo` 不参与；输入为已有 `.cbz` 时进入独立重命名模式（只改名不转换，可与其他模式叠加）；`%description` 不建议用于文件名（内容可能过长），可配合 `%subN_M` 截取片段；建议配合 `--dry-run` 先预览
- **颜色控制** — `--no-color` 禁用 ANSI 颜色输出（即使终端支持也不上色）；日志 / JSON / 管道输出本就不含颜色
- **撞名分类提示** — `--rename` 跳过时区分两类提示：目标文件已存在（建议加 `--overwrite`）与本批内部撞名（建议调整命名模板），dry-run 与非 dry-run 分支均生效，JSON `reason` 字段分别记为 `existing` / `conflict`；dry-run 预览中 `[将跳过]` 按类别着色（磁盘同名=黄、本批撞名=品红），实际执行汇总将跳过数分组统计（磁盘同名 / 本批撞名）
- **断点续跑** — 目标 CBZ 已存在且完整性校验有效时直接跳过（SKIP）；源文件比 CBZ 更新时自动重新转换；损坏/无效自动重新转换；`--overwrite` 无条件覆盖
- **失败分类** — 转换失败按原因分类统计（timeout / drm / corrupt / no_images / comicinfo / verify / other），汇总输出各类失败数量
- **检查模式支持 CBZ** — `--inspect` 可直接检查 `.cbz` 文件（纯 zipfile 读取不解压）；封面行加分辨率+大小、格式统计加总文件数、Spine 前 5 列表每行加宽高
- **只读图片清单** — `--list-images [FILTER]` 列出目标电子书内全部图片（序号 / 文件名 / 分辨率 / 大小 / 模式·色深 / 方向 / 目录 / 标记）+ 全量统计区块（格式 / 模式·色深 / 尺寸分布 / 双页横幅 / 动图 / 小图 / 异常明细），不转换、不写 CBZ、不生成 ComicInfo；FILTER 可选，支持条件表达式（格式 / `res` / `size` / 方向 / 模式 / 位深 / 标记，逗号 = OR、`+` = AND、`-` 前缀 = 排除）
- **双页检测** — `--double-page` 识别跨页横幅（宽/高 ≥ 阈值，默认 2.0），开启时逐页写入 DoublePage 标记（不写 Manga 声明）；不带值 / `auto` 开启，可传数值调阈值，`off` / `no` / `0` 关闭
- **丢弃小图** — `--drop small[=比例]` 剔除面积明显偏小的图片（宽×高 < 面积中位数×比例，默认 0.5），丢弃后 PageCount 按实际图片数重算；不带值 / `auto` = 0.5，可传 0~1 数值调比例，`off` / `no` / `0` 关闭；旧 `--drop-small` 为隐藏别名（等价 `--drop small`）仍可用
- **ComicInfo 字段覆盖** — `--setinfo FIELD=VALUE` 覆盖/新增 ComicInfo 字段（优先级最高），VALUE 支持固定值 / `%series` / `%number` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 占位符，可多次指定；字段名需在 ComicInfo 标准字段白名单内，白名单外字段 warning 忽略；已有 CBZ 场景下 `%series`/`%number`/`%volume` 优先读取 ComicInfo 内显式 Series/Number/Volume，缺失才回退文件名推断；输入为已有 CBZ 时直接修改其 ComicInfo.xml（未指定字段保留原值）
- **日志自动命名** — `--log` 不带文件名时自动生成 `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（当前目录）
- **解包查看** — `--unpack` 只解压不转换，输出到源文件同名子目录（已存在自动加序号避让），mobi 保留完整结构、cbz 直接解包（含 zip-slip 路径穿越防护）；`--unpack` / `--setinfo` 时也会收集 `.cbz` 输入
- **耗时统计** — 每个文件转换耗时实时输出，汇总底部显示总耗时
- **JSON 结构化输出** — `--json` stdout 输出 JSON（转换/修改模式为整体单行紧凑 JSON，检查模式为每文件一行精简 JSON，供 AI / 管道 / 脚本读取，开启时屏蔽人类文本输出）；`--json-out [FILE]` 将结构化结果写入 JSON 文件（缩进格式，省略文件名自动生成时间戳文件，行为对齐 `--log`）；两者可共存，转换 / `--setinfo` 修改 / `--inspect` 检查模式均支持

## 支持的图片格式

转换时识别并打包以下格式的图片：`.jpg` / `.jpeg` / `.png` / `.gif` / `.webp` / `.bmp` / `.tiff` / `.tif`

## 环境要求

- Python 3.10+
- 依赖：`mobi`

## 安装

```bash
pip install mobi
```

## 使用方法

### 转换单个文件

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi"
```

### 批量转换整个目录（递归搜索所有 .mobi / .azw / .azw3 / .epub）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary"
```

### 转换成功后删除原始电子书

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --delete
```

### 双目录 mobi 时保留 mobi7 版本

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --prefer mobi7
```

### 目录中有未被收集的多余图片时放弃追加

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --drop
```

> **extra（多余图）的定义**：指不在 OPF spine 阅读顺序中的图片（如广告页、出版信息页、
> 出版社水印页等）。`--drop`（不带值）等价于 `--drop extra`——丢弃全部多余图；
> 带过滤表达式时（如 `--drop gif,extra`）按「格式/分辨率/大小/方向/模式/位深/标记」
> 过滤，`extra` 关键字即指「不在 spine 中的图」。在 `--list-images` 中多余图会带 `[多余]` 性质标记。
> 旧 `--drop-extra` 已并入 `--drop`（隐藏别名，仍可用）。

### 已存在 cbz 时强制重新生成

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --overwrite
```

### 限制单文件转换超时（防止损坏文件卡死批量任务）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --timeout 300
```

### 输出到自定义目录（默认保留相对子目录结构）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --output-dir "E:\CBZ_Output"
```

### 平铺输出（所有 CBZ 直接放到输出目录根下）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --output-dir "E:\CBZ_Output" --flatten
```

### 试运行：只扫描并打印转换流程，不实际转换

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --dry-run
```

> 对已有 CBZ 配合 `--setinfo` 时，正式执行与试运行都会在执行前逐文件列出将变化的 ComicInfo 字段（`~ 字段: 旧 → 新`），仅新增的字段标 `+`，值不变的字段省略。

### 静默模式 + 输出写入日志

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --quiet --log convert.log
```

### 精简汇总（大批量目录，成功/跳过只看数量）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --quiet --short-summary --log convert.log
```

### 开启 zip 压缩（PNG 源漫画可显著减小体积）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --compress 9
```

### 检查模式：随机抽查 1 个电子书内部信息（元数据/结构/图片/分辨率/DRM/NCX 目录）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --inspect
```

### 检查全部电子书内部信息

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --inspect all
```

### 覆盖/新增 ComicInfo 字段（可多次指定，优先级最高）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --setinfo "Title=Sample Series" --setinfo "Number=%number" --setinfo "Summary=Vol. 1, First Edition"
```

> 说明：`--setinfo` 只在逗号后紧跟「字段名=」时才拆分，若值本身含 `Key=...` 结构，请拆成多次 `--setinfo` 传入以免误拆分。输入目录若混有已有 `.cbz` 与 `.mobi`，开启 `--setinfo` 时 `.cbz` 会被就地修改其 `ComicInfo.xml`（未指定字段保留原值），其余文件照常转换。

### 解包查看（只解压不转换，输出到源文件同名子目录）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.mobi" --unpack
```

### JSON 结构化输出（stdout 单行 / 写入文件）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary" --json
python manga-mobi2cbz.py "D:\ComicsLibrary" --json-out
python manga-mobi2cbz.py "D:\ComicsLibrary" --json --json-out inspect_result.json
```

> 说明：`--json` / `--json-out` 在「转换」「CBZ 修改」「检查」「试运行」四种模式输出结构化结果（试运行输出带 `dry_run` 标记，详见下方契约）；`--unpack` 模式不输出。转换/修改模式 `--json` 为整体单行紧凑 JSON，检查模式为每文件一行精简 JSON（含 status/series/number/source/page_count/drm，status 取值 ok/drm/invalid/noimg/timeout/fail），`--json-out` 落盘全量（含 spine/toc 与 summary）。进度条与人类可读提示写 stderr、JSON 写 stdout 天然分流；若用 `2>&1` 合并重定向会把进度条混入 JSON 流，建议同时加 `--no-progress`。

### 查看版本号

```bash
python manga-mobi2cbz.py --version
```

## 参数说明

| 参数  | 说明  |
| --- | --- |
| `target` | 电子书文件路径、包含电子书（.mobi/.azw/.azw3/.epub）的目录，或含 `*` / `?` 的通配符模式（如 `*.epub`、`卷*/001.mobi`）；处理当前目录可写 `.`（必填） |
| `--language LANG` | 输出语言：`auto` 按系统 locale 自动选择（zh 前缀→中文，zh-TW/zh-Hant→繁体中文，ja/Japanese→日文，否则→英文），或指定 `zh-CN`/`zh-TW`/`ja`/`en`（默认 `auto`）；兼容常见写法：`zh`/`cn`→zh-CN，`zhtw`/`tw`→zh-TW，`jp`→ja，`eng`→en |
| `--top-only` | 仅处理 target 目录顶层的电子书文件，不递归子目录 |
| `--delete` | 转换成功后删除原始电子书文件（默认不删除） |
| `--prefer` | 双目录 mobi 时保留哪份：`auto` / `mobi7` / `mobi8`（默认 `auto`）；`auto` 优先 mobi8、mobi8 无图片自动回退 mobi7；明确指定 `mobi7`/`mobi8` 时该目录无图片自动回退另一份 |
| `--drop [EXPR]` | 统一丢弃入口（`nargs='?'`）：无值 = `extra` 丢弃全部多余图片（默认追加到 cbz 末尾）；带值按条件丢弃——格式词 / 条件词（`res` / `size` / 方向 / 模式 / 位深 / 标记：`double` / `thumbnail` / `animated` / `cover` 等）/ `small[=比例]` 小图；多条件逗号 = OR、`+` = AND、`-` 前缀 = 排除，如 `--drop gif,extra`、`--drop small=0.4`、`--drop 封面+超大页`；`off` / `no` / `0` 关闭；执行顺序：多余图丢弃 → 去重 → 条件过滤 → 小图丢弃；处理结果逐条列出被丢弃图片文件名，`--short-summary` 下只显示数量；旧 `--drop-extra` / `--drop-small` 并入本参数（隐藏别名仍可用） |
| `--overwrite` | 目标 cbz 已存在时强制重新生成（默认跳过） |
| `--ext-priority EXTS` | 同目录同名（仅扩展名不同）时保留哪种格式：逗号分隔、顺序即优先级从高到低，仅接受 mobi/azw/azw3/epub，默认 azw3；优先级未覆盖时回退兜底顺序 azw3→epub→mobi→azw；与 `--prefer`（双目录选择）无关 |
| `--timeout` | 单文件转换超时秒数，超时自动跳过并计入失败（默认 600，`0` 表示不限制） |
| `--min-size BYTES` | 过滤小于指定字节的电子书；不带数字默认 1000，`0` 关闭，不传则关闭大小过滤 |
| `--output-dir DIR` | CBZ 输出到指定目录（自动创建），默认保留相对输入的子目录结构（如 `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`）；加 `--flatten` 可平铺到目录根下 |
| `--flatten` | 仅与 `--output-dir` 联用：所有 CBZ 平铺到输出目录根下，同名文件未指定 `--overwrite` 时跳过（SKIP），指定时覆盖首选名；单独使用（无 `--output-dir`）将报错退出 |
| `--progress` | 进度条显示策略：`auto` 在 TTY 且文件数≥2 且未用 `--json`/`--json-out` 时显示；`on` 强制显示；`off` 强制关闭（默认 `off` 不显示）；进度条写 stderr，不进 `--log` 日志 |
| `--no-progress` | 强制关闭进度条（等价 `--progress off`，兼容旧命令） |
| `--dry-run` | 试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录 |
| `--rename[=TEMPLATE]` | 重命名输出 CBZ 文件名（可选模板，默认关闭）：无值 = 默认模板（系列名 + 自动标记前缀，前缀按类型自动选 `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`，连话 `話005-006` 标 `[Ch.5-6]`）；模板支持 `%series` / `%number` / `%volume` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 及 `%03number` 补零占位符；来源优先级：文件名推断 > 文件自带元数据（OPF / ComicInfo.xml）兜底，`--setinfo` 不参与；输入为已有 `.cbz` 时进入独立重命名模式（只改名不转换，可与其他模式叠加）；跳过时区分两类提示（磁盘同名建议 `--overwrite` / 本批撞名建议调模板），JSON `reason` 分别记 `existing` / `conflict`；dry-run 预览中 `[将跳过]` 按撞名类别着色（磁盘同名=黄、本批撞名=品红，仅 TTY 且未 `--no-color` 时生效），实际执行汇总将跳过数拆分为「磁盘同名 N / 本批撞名 M」并分组列出；`%description` 不建议用于文件名（内容可能过长），可配合 `%subN_M` 截取片段；建议配合 `--dry-run` 先预览 |
| `--no-color` | 禁用 ANSI 颜色输出（即使终端支持也不上色）；日志 / JSON / 管道输出本就不含颜色 |
| `--quiet` | 静默模式，只显示错误与最终汇总 |
| `--debug` | 调试模式：向 stderr 输出 debug 级日志（默认静默，仅指定时输出；与 `--quiet` 同给时 debug 仍输出） |
| `--short-summary` | 精简汇总：成功/跳过文件只显示数量不列出路径（失败文件始终全路径列出） |
| `--compress LEVEL` | zip 压缩级别 0-9：`0`=不压缩（默认，图片本身已压缩），`1-9`=deflate 压缩（PNG 源有收益，级别越高越小但越慢） |
| `--inspect [MODE][,FILTER]` | 检查模式：`sample` 随机抽查 1 个（默认），`all` 全量检查；可附过滤器（如 `all,small=0.6`），命中条件的图片输出数量 + 文件名清单（含尺寸）；位置参数为单个文件时直接检查该文件，只解包读取内部信息（元数据/结构/图片/分辨率/DRM 双重判断/NCX 目录），不生成 CBZ，结束自动清理临时目录；图片预览仅列前 5 张，图数 > 5 时末尾追加省略号行（英文 `...`，如 `...（共 N 张）`）；目录(NCX) / nav 预览截断统一为英文 `...` |
| `--inspect-all` | 检查全部电子书（等价 `--inspect all`，兼容旧命令） |
| `--no-comicinfo` | 不生成 ComicInfo.xml（默认生成：向 CBZ 根目录写入 Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary 漫画元数据） |
| `--setinfo FIELD=VALUE` | 覆盖/新增 ComicInfo 字段（可多次指定，优先级最高）：`FIELD` 为 ComicInfo 字段名（需在 ComicInfo 标准字段白名单内，白名单外 warning 忽略），`VALUE` 支持固定值 / `%series` / `%number` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 占位符（`%subN_M`=第 N 字符起 M 个，1-based；整段恰为单个已知占位符且对应值缺失时该字段不写入）；占位符可与固定文本混用（如 `%writer·重制`、`第%number话`），混用时缺失值渲染为空串；智能拆分：仅当逗号后紧跟"字段名="时才拆分，否则逗号视为值的一部分（如 `Summary=Vol. 1, First Edition` 不拆分）；值内含 `Key=` 结构请用多次 `--setinfo` 传入；`Manga` 默认不写入，需显式 `--setinfo Manga=Unknown\\|No\\|Yes\\|YesAndRightToLeft`（限官方 v2.0 枚举）；另支持 `CommunityRating`（0-5）/ `MainCharacterOrTeam` / `Review` 三个官方字段；已有 CBZ 场景下 `%series`/`%number`/`%volume` 优先读取 ComicInfo 内显式 Series/Number/Volume，缺失才回退文件名推断；开启 `--setinfo` 时输入目录中混有的已有 `.cbz` 会就地修改其 ComicInfo.xml（未指定字段保留原值），其余文件照常转换 |
| `--unpack` | 解包查看：只解压不转换，输出到各源文件所在目录的同名子目录（已存在自动加序号避让）；mobi 走 extract 保留完整结构，cbz 走 extractall（含 zip-slip 路径穿越防护）；`--unpack` / `--setinfo` 时也会收集 `.cbz` 输入 |
| `--repack` | 重新打包模式：把已解包的 `_cbz` 解包目录（目录名以 `_cbz` 结尾，如 `vol_cbz/`）重新打包回 CBZ，输出名还原为源文件名（`vol_cbz` → `vol.cbz`）；支持单个目录或父目录批量，执行前先打印待处理清单（每行标注 `解包目录名 → 输出.cbz`）；目录内 ComicInfo.xml 有则原样带回、无则生成基础版，可 `--setinfo` 叠加覆盖、`--no-comicinfo` 关闭；已存在默认跳过、`--overwrite` 覆盖；`--rename` 不适用于本模式 |
| `--double-page VALUE` | 双页检测：不传或 `auto` 开启（阈值 2.0，检测宽/高 ≥ 阈值的横幅跨页大图，ComicInfo 写入逐页 `Type="DoublePage"`，`Manga` 不再自动声明）；传数值（如 `2.5`）开启并调整阈值；`off` / `no` / `0` 关闭；非法值报错 |
| `--drop small[=比例]` | 丢弃小图：转换时剔除面积明显偏小的图片（宽×高 < 面积中位数×比例 判为小图，如封面缩略图 / 版权页）；`small` 无参 / `auto` 用默认比例 0.5，可传 `0~1` 数值（如 `--drop small=0.4`）调比例；`off` / `no` / `0` 关闭（默认关闭，不改变现有行为）；丢弃后 ComicInfo `PageCount` 按实际剩余图数重算，汇总 / `--log` / `--json` 新增"丢弃小图"计数（`--json` 输出 `dropped_small` 字段）并逐条列出被丢弃文件名（`--short-summary` 下只显示数量）；`--inspect` 预览会提示"开启 --drop small 时将丢弃 N 张"；横幅双页（宽不小）不会被误删；仅转换模式生效；旧 `--drop-small` 等价 `--drop small`（隐藏别名仍可用） |
| `--list-images FILTER` | 只读图片清单（`nargs='?'`）：列出目标电子书内全部图片（序号 / 文件名 / 分辨率 / 大小 / 模式·色深 / 方向 / 目录 / 标记）+ 全量统计区块（格式 / 模式·色深 / 尺寸分布 / 双页横幅 / 动图 / 小图 / 异常明细），不转换、不写 CBZ、不生成 ComicInfo、不落盘；与 `--inspect` 完全独立。无值 = 全部列出；带值 = FILTER 筛选表达式（与 `--drop` 同源引擎：格式 / `res` / `size` / 方向 / 模式 / 位深 / 标记 / `small[=比例]` 条件词，逗号 = OR、`+` = AND，`-` 前缀排除，如 `jpeg,size>1MB`、`-webp`），筛选只影响清单行，统计恒全量。CBZ 直读 zip 不落盘（无目录列 / 无转换态标记）；配 `--json` 每文件一行精简 JSON，配 `--quiet` 抑制明细只剩计数 |
| `--log FILE` | 将全部输出追加写入指定日志文件；不带文件名时自动生成 `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（当前目录） |
| `--json` | stdout 输出 JSON（供 AI / 管道 / 脚本读取），开启时屏蔽人类可读文本输出（进度条 / emit 提示 / 汇总）；转换/修改模式为整体单行紧凑 JSON，检查（`--inspect`）模式为每文件一行精简 JSON（status/series/number/source/page_count/drm，status 取值 ok/drm/invalid/noimg/timeout/fail）；试运行（`--dry-run`）输出带 `dry_run` 标记的 JSON（status 取值 will_skip/pending），unpack 模式不输出；进度条写 stderr 不混流，但 `2>&1` 合并重定向会混入进度条 |
| `--json-out FILE` | 将结构化结果写入 JSON 文件（缩进格式）；不带文件名时自动生成时间戳文件（当前目录），带文件名写入指定路径，行为对齐 `--log`；与 `--json` 可共存；转换/修改模式写入文件级结果，检查（`--inspect`）模式写入全量（含 spine/toc 与 summary） |
| `--version` | 显示版本号 |

## 输出

- 默认转换后的 `.cbz` 文件与原电子书文件在同一目录；指定 `--output-dir` 时输出到该目录（自动创建），默认保留相对输入的子目录结构，加 `--flatten` 可平铺到输出目录根下（同名文件未指定 `--overwrite` 时跳过）
- 已存在的 `.cbz` 默认自动跳过，不会覆盖；加 `--overwrite` 可强制重新生成
- 0 字节 / 文件头损坏的电子书在预处理阶段直接跳过，日志输出完整路径与原因
- 每个文件转换耗时实时输出，汇总底部显示总耗时
- 转换失败的文件会打印错误信息，不影响其他文件继续转换

## JSON 输出契约

`--json` / `--json-out` 的结构化输出中，`status` 字段是机器消费的关键契约，三种模式取值如下：

| 模式  | status 取值 | 失败细分 |
| --- | --- | --- |
| 转换（默认） | `ok` / `skip` / `fail` / `timeout` | 失败原因走 `reason` 字段：`drm` / `corrupt` / `verify` / `comicinfo` / `other` |
| 检查（`--inspect`） | `ok` / `drm` / `invalid` / `noimg` / `timeout` / `fail` | `--json` 每文件一行精简 JSON；`--json-out` 落盘全量（含 spine/toc 与 summary） |
| 修改（`--setinfo`） | `modified` / `nochange` / `fail` | 失败原因在 `reason` 字段 |
| 试运行（`--dry-run`） | `will_skip` / `pending` | 每条记录带 `dry_run: true` 标记，机器可与真实运行区分 |

每条记录固定字段：`source` / `status` / `target` / `reason` / `elapsed_sec`；转换模式额外含 `series_source` / `number_source` / `cover_source` / `dropped_small`。

## 已知限制

- **DRM 加密的 mobi 不兼容** — 底层 mobi 库无法解密 Kindle 商店购买的 DRM 加密漫画，此类文件会明确提示"可能为 DRM 加密"并跳过，不会静默产生空 cbz。请先去除 DRM 后再转换
- **超时后线程无法强制终止** — 单个文件超过 `--timeout` 后主流程会跳过它继续处理，但 Python 无法杀死已阻塞的解包线程，卡死的线程会残留到进程结束并持续占用内存/IO；批量大量损坏文件时可能堆积后台僵尸线程。若需彻底隔离卡死任务，可改用 `multiprocessing` 实现可终止子进程，但会增加跨平台兼容复杂度，暂未采用

## 常见问题

**Q: 转换后 CBZ 里的图片顺序乱了？**
A: 优先按 OPF spine 顺序（EPUB 标准阅读顺序）提取图片，绝大多数情况下顺序正确；若源文件无 OPF 或 spine 提取为空，会兜底按文件名自然排序。如果仍有问题，可能是原 mobi 内部图片命名不规范，请检查源文件。

**Q: 为什么 CBZ 里少了封面？**
A: 部分 mobi 的封面只由 OPF metadata 的 cover meta 指向、未被 spine 引用，按 spine 提取时会漏掉。脚本会自动扫描文件名含 cover/front 的图片，缺失时插入首位补齐；若封面已在 spine 列表中则保持原顺序。若封面文件名不含上述关键字，可能仍会遗漏，可改名后重转。

**Q: 为什么有些 mobi 转换后体积很小？**
A: 双目录 mobi（mobi7+mobi8）默认 `auto` 只保留有内容的一份（优先 mobi8，mobi8 无图片自动回退 mobi7），避免内容重复导致体积翻倍。如需强制保留 mobi7 请加 `--prefer mobi7`。

**Q: 批量转换时遇到损坏/加密 mobi 卡住不动了？**
A: 单文件转换默认有 600 秒超时（`--timeout` 可调），超时后会自动跳过该文件并计入失败，主流程继续处理后续文件。若你更早发现某个文件卡住，可用 `--timeout 30` 之类的较小值加快跳过，或用 `--quiet` 减少输出。

**Q: 使用 --output-dir 后为什么保留了子目录？**
A: v1.9.0 起 `--output-dir` 默认保留相对输入的子目录结构（旧版一律平铺，属破坏性变更）。需要平铺时加 `--flatten`，旧命令 `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output` 改为 `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output --flatten` 即可恢复旧行为。

**Q: 支持 .azw / .azw3 吗？**
A: 支持。v1.8.0 起输入扩展名扩展为 `.mobi` / `.azw` / `.azw3`，三种格式统一走同一转换链路；同目录同名不同扩展名时默认保留 azw3，可用 `--ext-priority` 调整。

**Q: 支持 EPUB 吗？**
A: 支持。v2.4.0 起输入扩展名扩展为 `.mobi` / `.azw` / `.azw3` / `.epub`。EPUB 本质为 ZIP 容器，直接走 zipfile 安全解包并复用 OPF spine 提取链路；封面自动识别支持 EPUB2（`<meta name="cover">`）与 EPUB3（`properties="cover-image"`）两种约定；无 EXTH 头时元数据从 OPF `dc:` 字段读取；`--prefer` 对 EPUB 静默忽略。加密 EPUB（Adobe DRM 等）无法解析内容，会提示无图片/无有效元数据并跳过，请先去除 DRM 再转换。

## 更新日志

### [3.5.4] - 2026-09-04

#### 修复

- **`--dry-run` 在 `--unpack` / `--repack` 模式失效修复** — 此前两模式忽略 `--dry-run`，真实执行解包/打包落盘；现入口优先判定 `dry_run` 短路，只打印解包/打包计划不写盘（含 `--json` / `--json-out` 输出），对齐 help 契约「不实际解压打包、不创建输出目录」
  
  #### 维护
  
- **解包目标目录命名抽为 `_unpack_target_dir`** — 真实解包与 `--dry-run` 预览共用同一命名规则，保证试运行预览与实跑一致

### [3.5.3] - 2026-09-02

#### 修复

- **`--list-images` 非法过滤表达式退出码修复** — 非法表达式分支裸 `return` 改为 `return 1`，避免 `_main` 尝试 `max(mode_codes)` 时对空列表触发 TypeError
- **`get_drm_flag` EXTH 偏移修正** — 读取 DRM 标志的 EXTH 项内偏移从 `+14` 修正为 `+12`（`0x0E` → `0x0C`）

### [3.5.2] - 2026-09-01

#### 维护

- **`_list_ebook` 复用 `ensure_cover_first`** — 消除重复的封面兜底扫描代码（文件名关键词封面补齐逻辑合并为单一实现）
- **`parse_inspect_arg` 局部变量 `t` 改名 `tok`** — 消除对 i18n 翻译函数 `t()` 的遮蔽
- **`emit` 日志改为持久句柄** — 消除每次写日志 open/close

### [3.5.1] - 2026-08-31

#### 修复

- **P0：四语 `help.setinfo` / `help.rename` 占位符恢复 `%%`** — 帮助文本占位符误改为单 `%`，argparse 把 help 当 `%` 格式串展开触发 TypeError；已恢复为 `%%`（模块 docstring 保持单 `%`）
- **P1：三模式退出码改用 return 返回** — `--unpack` / `--inspect` / `--list-images` 不再直接 `sys.exit`，改为 return 退出码，`_main` 统一 `sys.exit(max(mode_codes))`，模式串联执行不被中断
- **P2：`--repack` 示例与注释 `_cbz` 结尾修正** — 示例与代码注释中「目录名以 .cbz 结尾」改为 `_cbz` 结尾，docstring 示例 `Vol_cbz --repack` 同步修正
- 文件头用法行 `[--inspect sample|all]` → `[--inspect [sample|all][,FILTER]]`
- 四语 `help.output_dir` 追加「`--unpack` 模式忽略此参数」说明
  
  #### 变更
  
- **主循环通用异常兜底** — 提取 `_convert_one` 嵌套函数并补 `except Exception`，未预期异常计入失败文件而非裸退；四语新增 `run.unexpected_error` 文案键

### [3.5.0] - 2026-08-28

#### 新增

- **`-` 前缀排除** — `--drop` / `--inspect` 过滤器支持负向条件（如 `all,small=0.6,-gif`），与逗号 OR / 加号 AND 由同一表达式引擎统一解析
- **`--repack` 忽略 `--rename` 提示** — repack 模式输出名由解包目录名推断，`--rename` 被忽略时给出提示
- **`--repack` 处理清单标注推断输出名** — 执行前打印的待处理清单每行标注 `解包目录名 → 输出.cbz`，推断来源一目了然（`--repack` 模式的内部清单展示，非独立参数）
  
  #### 变更
  
- **退出码语义细化** — 目标路径不存在退出 `2`；`--repack` 无可用解包目录 / 无 `_cbz` 目录退出 `2` 且计入失败 1；`--unpack` 解包失败退出 `1`；`--inspect` 异常退出 `1`；转换中 Ctrl+C 退出 `130`（128+SIGINT）
  
  #### 修复
  
- `--drop-small` 无效值文案矛盾（同时提示 off/no/0）改为"支持 auto 或数值(0~1)"
- `--setinfo` 帮助与文件头示例中占位符 `%%` 误写改为单 `%`
- `--unpack` 目录撞名避让说明措辞（默认 源名_扩展名，撞名时以 `(N)` 序号避让）
- `--inspect` 帮助补充 FILTER 语法说明（与 `--drop` 相同：逗号=OR、加号=AND、`-` 前缀排除）
- 四语 `help.setinfo` / `help.rename` 帮助文本占位符 `%%` 误写统一为单 `%`
  
  #### 维护
  
- 回归测试退出码预期更新（目标不存在 `1` → `2`）

### [3.4.0] - 2026-08-26

#### 新增

- **退出码语义** — `0` = 全部成功（含全部跳过、无失败）；`1` = 存在转换失败文件（转换失败 / DRM / 校验失败等）；`2` = 参数用法错误（argparse 内置），便于脚本化判断成败
  
  #### 变更
  
- `--inspect --json` 精简输出新增 `formats` 汇总字段（各图片格式数量分布）
  
  #### 维护
  
- 回归测试增至 56 项（新增退出码语义 / inspect formats / 版本号护栏）

### [3.3.0] - 2026-08-25

#### 新增

- **`--drop [EXPR]` 统一丢弃入口** — 无值 = 丢弃目录外多余图（同旧 `--drop-extra` 无值语义）；格式词 / 条件词 / `small[=比例]` 均可；多条件逗号 = OR、加号 = AND、`-` 前缀排除，`off` 关闭；旧 `--drop-extra` / `--drop-small` 降为隐藏别名并入
- **`--inspect [MODE][,FILTER]`** — 在 sample/all 基础上可附过滤器（如 `all,small=0.6`），命中条件的图片输出数量 + 文件名清单（含尺寸）；`--json` 对应新增 `filter_hits` 结构
- **`small` 独立带参条件词** — 无参 / auto = 默认比例 0.5，可传 0~1 数值；四语别名（异常小图 / 異常小圖 / 異常小画像 / 極小画像）均可带参
  
  #### 变更
  
- 三链路（转换丢弃 / inspect 预览 / list 清单）统一由 `--drop` 表达式驱动，小图面积口径单一来源
- `--drop-extra` / `--drop-small` 从 `--help` 隐藏（兼容仍可用）
  
  #### 维护
  
- 回归测试增至 46 项

### [3.2.0] - 2026-08-24

#### 新增

- **[异常] 行内恒显标记** — 首列汇总该行任一异常，一眼可见
- **[推断] 独立推断标记，替代「疑似」** — 旋转跨页 / 缩略图 / 封面补位等推断性标注去除「疑似」：仅凭尺寸 / 文件名推断、非 OPF 明确声明者标 `[推断]`（OPF guide 封面 / 动图 / 多余不标）；新增四语筛选别名 `inferred` / `推断` / `推斷` / `推測` / `推定`
  
  #### 变更
  
- **模式列统一英文规范名** — `index` / `gray` / `rgb` / `graya` / `rgba`，取消四语本地化键，省维护
- **小图判定改面积口径** — 宽×高 < 面积中位数×比例，并与 `--drop-small` 比例统一——标了即会丢；`--list-images` / `--inspect` 预览 / 转换丢弃三条链路同一口径
- **`--drop-small` 关闭时不再标 [小图]** — 与「标了即会丢」口径一致
  
  #### 维护
  
- 回归测试同步（34 项全通过）

### [3.1.1] - 2026-08-24

#### 修复

- `--unpack` 的 help 文案残留旧「自动加序号避让」描述，与 v3.1.0 起「源名_扩展名」统一命名矛盾，四语同步更正
  
  #### 维护
  
- `--repack` 的 help 注明 `--rename` 不适用于本模式；`--list-images` 的 help 补充 [追加] / [舍弃] / [筛选] 处置标记说明
- 回归测试扩充至 34 项（新增 repack 还原 + ComicInfo 叠加、`_safe_zip_extract` 的 `C:foo` 逃逸、`name` 原子 WindowsPath 三组）

### [3.1.0] - 2026-08-24

#### 新增

- **过滤表达式多语言支持** — `--list-images` / `--drop-extra` 的 FILTER 支持中/繁/日/英四语别名（如 `封面` / `cover` / `表紙`），可直接粘贴展示标签（自动剥掉方括号）
- **新统计标签筛选词** — `超大页`（overscale）/ `疑似旋转跨页`（rotated_double）/ `异常`（anom）；`--drop-extra` 同步支持，转换时按标签丢弃；异常与多余（extra）为独立维度，互不连带
- **文件名筛选 `name=关键词`** — 按文件名（含扩展名）大小写不敏感子串匹配，可与标签/属性条件混用
- **处置筛选词** — `追加`（append）/ `舍弃`（drop）/ `筛选`（filter），筛出将被追加 / 被舍弃 / 被丢弃过滤器命中的图
- **`--repack` 重新打包模式** — 把已解包的 `_cbz` 解包目录（目录名以 `_cbz` 结尾，如 `vol_cbz/`）打包回 CBZ，输出名还原为源文件（`vol_cbz` → `vol.cbz`），支持单个目录或父目录批量，执行前先列出待处理清单；目录内 `ComicInfo.xml` 有则原样带回、无则生成基础版，可 `--setinfo` 叠加覆盖、`--no-comicinfo` 关闭；已存在默认跳过、`--overwrite` 覆盖
- **解包目录统一命名 `源名_扩展名`** — `--unpack` 解包目录名由 `vol.cbz/` 改为 `vol_cbz/`（`vol.mobi` → `vol_mobi/`），与源文件不撞名、不再出现序号避让；`_cbz` 结尾即可被 `--repack` 识别重新打包
- **`--setinfo` 执行前输出变更计划清单** — 非 dry-run 分支执行前也逐文件列出将新增/修改的 ComicInfo 字段（`~ 字段: 旧 → 新`，仅新增标 `+`），与 `--unpack` / `--repack` 的「处理清单 + 完成汇总」约定一致
  
  #### 修复
  
- `cover` / `extra` 筛选词未覆盖封面补位图（cover_extra），导致封面筛选曾命中 0
- `_parse_atom` 对 `8bit` 的解析崩溃、`name` 原子在 Windows 下的 WindowsPath 崩溃
- 封面补位图被误计入「异常」明细
- `_safe_zip_extract` 补驱动器相对路径（`C:foo`）逃逸防护，zip-slip 防护链闭环
  
  #### 维护
  
- 新增回归测试 `tests/test_mobi2cbz.py`（30 项，覆盖多语言别名 / 方括号粘贴 / name / 异常标签 / 处置筛选 / cover_extra 修复）

### [3.0.0] - 2026-08-24

#### 破坏性变更

- **许可证切换为 GPL-3.0-only** — 因运行时依赖 mobi 库（GPL-3.0-only），本项目公开分发即构成分发，许可证由 MIT 切换为 GPL-3.0-only；LICENSE 替换为 GNU GPL v3，本 README 许可章节已同步更新
- **进度条默认关闭** — 不再智能自动显示，需显式 `--progress on` / `--progress auto` 开启；统一为 `--progress auto|on|off`（不传或 `off` = 关闭；`auto` = TTY 且文件数 ≥ 2 且未用 `--json`/`--json-out` 时显示）；旧 `--no-progress` 保留为隐藏别名
- **`--inspect` 参数收敛** — `--inspect [sample|all]`（默认 `sample` = 旧抽查 1 个，`all` = 旧 `--inspect-all`）；旧 `--inspect-all` 单独使用时自动启用 `--inspect` 的黑盒行为已删除，需显式 `--inspect all`；`--inspect-all` 保留为隐藏别名

#### 新增

- **target 支持 glob 通配符** — `target` 可传含 `*` / `?` 的模式（如 `*.epub`、`卷*/001.mobi`），命中多个文件时按扩展名过滤后作为平铺文件列表处理；处理当前目录可写 `.`
- **`--top-only`** — 仅处理 target 目录顶层的电子书文件，不递归子目录
- **`--setinfo` 新增 `%subN_M` 占位符** — 截取文件名第 N 个字符（1-based）起的 M 个字符，如 `[Anon][Demo Series]話005-006` 配 `--setinfo "Series=%sub8_11"` 得 `Demo Series`；越界时该字段不写入
- **`--inspect` 支持 JSON 输出** — `--json` 每文件一行精简 JSON（`status` / `series` / `number` / `source` / `page_count` / `drm`，`status` 取值 `ok` / `drm` / `invalid` / `noimg` / `timeout` / `fail`）；`--json-out` 落盘全量（含 `spine` / `toc` 与 summary）；`inspect_ebook` 内部重构为返回 `(InspectStatus, info dict)` 结构化元组
- **dry-run 配合 `--setinfo` 字段级预览** — 逐文件列出将变更的 ComicInfo 字段（`~ 字段: 旧 → 新`；仅新增标 `+`；值不变省略），不写盘
- **`--inspect` 分辨率分布摘要** — 抽查 / 全量扫描末尾输出分辨率分布摘要：主分辨率 `WxH` 张数及占比、异常小图数量（判定口径与 `--drop-small` 一致：宽高均 < 中位数 × 0.5）
- **`--debug` 调试日志** — 新增 `--debug` 参数 + emit debug 级：仅指定 `--debug` 时向 stderr 输出 debug 级日志（默认静默，不刷屏），与 `--quiet` 同给时 debug 仍输出；四语言 help.debug
- **`--inspect` 刷屏治理** — inspect 逐文件进度行降为 info 级，`--quiet` 可抑制刷屏，零新参数
- **磁盘空间预检** — 新增 `estimate_expanded_size` + `check_disk_space`，主循环逐文件预检解压所需空间，不足时 `warn.disk_space` 提示但放行继续（不阻断批量，四语言）
- **临时目录清理失败提示** — 三处 `rmtree(ignore_errors=True)` 改为 try/except + `warn.cleanup_tmp_fail`，清理失败不再静默吞掉（四语言）
- **`--drop-extra` / `--drop-small` 输出对称** — 两者处理结果均逐条列出文件名（`--drop-extra` 列出放弃追加的多余图片、`--drop-small` 列出被丢弃的小图），配合 `--short-summary` 时只显示数量不列路径，与成功/跳过文件汇总口径一致
- **`--rename` 输出重命名** — 重命名输出的 CBZ 文件名（可选模板，默认关闭）：无值 = 默认模板（系列名 + 自动标记前缀，前缀按类型自动选 `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`，连话 `話005-006` 标 `[Ch.5-6]`）；模板支持 `%series` / `%number` / `%volume` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 及 `%03number` 补零占位符；来源优先级：文件名推断 > 文件自带元数据（OPF / ComicInfo.xml）兜底，`--setinfo` 不参与；输入为已有 `.cbz` 时进入独立重命名模式（只改名不转换，可与其他模式叠加）；`%description` 不建议用于文件名（内容可能过长），可配合 `%subN_M` 截取片段；建议配合 `--dry-run` 先预览
- **`--no-color` 颜色控制** — 禁用 ANSI 颜色输出（即使终端支持也不上色）；日志 / JSON / 管道输出本就不含颜色
- **撞名分类提示** — `--rename` 跳过时区分两类提示：目标文件已存在（`skip_existing`，建议加 `--overwrite`）与本批内部撞名（`skip_conflict`，建议调整命名模板），dry-run 与非 dry-run 分支均区分，JSON `reason` 字段分别写 `existing` / `conflict`
- **新增 `--list-images [FILTER]` 只读图片清单** — 列出目标电子书内全部图片（序号 / 文件名 / 分辨率 / 大小 / 模式·色深 / 方向 / 目录 / 标记）+ 全量统计区块（格式 / 模式·色深 / 尺寸分布 / 双页横幅 / 动图 / 小图 / 异常明细），不转换、不写 CBZ、不生成 ComicInfo、不落盘；与 `--inspect` 完全独立。无值 = 全部列出；带值 = FILTER 筛选表达式（格式 / `res` / `size` / 方向 / 模式 / 位深 / 标记 / `small[=比例]` 条件词，逗号 = OR、`+` = AND，`-` 前缀排除，如 `jpeg,size>1MB`、`-webp`），筛选只影响清单行，统计恒全量；CBZ 直读 zip 不落盘（无目录列 / 无转换态标记）；配 `--json` 每文件一行精简 JSON，配 `--quiet` 抑制明细只剩计数
- **`--drop-extra` 改造为通用丢弃过滤器** — 由布尔改为 `nargs='?'`：无值 = `extra` 丢弃全部多余图片（等价旧行为）；带值按条件丢弃（格式 / `res` / `size` / 方向 / 模式 / 位深 / 标记 条件词，与 `--list-images` 同源引擎，逗号 = OR、`+` = AND，如 `--drop-extra gif`、`--drop-extra gif,extra`）；`off` / `no` / `0` 关闭；执行顺序：多余图丢弃 → 去重 → 条件过滤 → 小图丢弃，与 `--drop-small` 可叠加
- **`--inspect` 省略号统一英文 `...`** — 图片预览仅列前 5 张，图数 > 5 时末尾追加省略号行（如 `...（共 N 张）`）；目录(NCX) / nav 预览截断统一为英文 `...`（替换原 Unicode `…`）
- **撞名 A/B 预览着色与汇总分组统计** — `--rename` dry-run 预览中 `[将跳过]` 按撞名类别着色：A 类（磁盘已存在同名目标）黄色、B 类（本批内部撞名）品红（仅 TTY 且未 `--no-color` 时生效）；实际执行汇总将跳过总数拆分为「磁盘同名 N / 本批撞名 M」，跳过文件列表按两类分组列出（各自带标题）；JSON `reason` 字段沿用 `existing` / `conflict`，`skipped` 计数口径不变（两组合计 + nochange）

#### 修复

- **NCX 定位漏检** — 新增 `find_ncx` 统一定位（优先按 OPF manifest 的 `media-type=application/x-dtbncx+xml`，其次 spine 的 `toc` 属性指向 id，最后兜底 `*.ncx`），兼容把 NCX 命名为 `xml/vol.nav` 等非 `.ncx` 扩展名的封装；`parse_ncx_toc` / `parse_ncx_entries` 均改用
- **`--inspect` 目录(NCX) 计数口径** — 仅统计 `<navLabel><text>` 目录条目（此前把 docTitle/docAuthor 也算入，条目数虚高 1-2）
- **`--rename` 的 `%title%` 占位符支持 OPF `dc:title` 兜底** — 此前 `%title%` 仅取 ComicInfo.xml `<Title>`，epub 无 ComicInfo 时恒空；现补充 OPF `dc:title` 兜底，来源优先级：OPF `dc:title` → ComicInfo.xml `<Title>`（与 series/number 的 OPF 兜底一致）
- **`--rename` / `--setinfo` 新增 `%writer` / `%publisher` / `%date` / `%language` / `%description` 占位符** — OPF 读 `dc:creator` / `dc:publisher` / `dc:date` / `dc:language`（经归一化）/ `dc:description`，ComicInfo 读 `<Writer>` / `<Publisher>` / `<LanguageISO>` / `<Summary>`；`%date` 保留原始日期字符串（如 `2024-01-15`，ComicInfo 无对应字段）；OPF 优先于 ComicInfo
- **DRM 误报修复** — `get_drm_flag` 原读 PalmDB 头偏移 12 的 2 字节（落在 name 字段，文件名含 `-`/`_` 的 [Anon] 系列等被误判加密），改读 attributes 偏移 32 的 copy-protection 位 + PalmDOC header encryption type（偏移 78 + 8×nrec + 0x0E）作为权威判据
- **`--inspect` 遇 DRM 标记不再跳过解包** — DRM 标记降级为信息项，仍尝试解包：解出图片 → `status=ok` 并带 `drm` 标记，仅当解包失败且图片数为 0 才判 DRM
- **`--drop-extra cover` 原子哑弹修复** — 封面按 OPF guide + COVER_KEYWORDS 打标，list 与转换两链路均生效，`--drop-extra cover` 可可靠舍弃封面
- **`--setinfo` 占位符与固定文本混用** — 值支持占位符与固定文本混写（如 `%writer·重制`、`第%number话`），与 `--rename` 一致的全局替换：缺失值渲染为空串、未知占位符原样保留；整段恰为单个已知占位符时保留原语义（缺值不写入该字段）
- **NCX / NAV 目录解析顺序与实体解码** — `parse_ncx_entries` 改栈建树 + 文档顺序先序遍历（父条目恒在子条目前、同层保持文档顺序），标题剥离嵌套标签并解码 HTML 实体（`&amp;` → `&`）；`parse_nav_entries` 同步补实体解码

#### 安全修复

- **XXE 注入防护（P0）** — `ET.parse` 全部替换为 `safe_et_parse`（7 处调用点），仅拦截 `<!ENTITY` 实体声明（裸 DOCTYPE 放行）；字符串路径仅拦截 `..` 穿越（放行 `./` 前缀与纯相对路径，兼容解包内 OPF/NCX 引用）

#### 修复 / 维护

- **转换链路超时残留提示** — 补充 `run.timeout_residue`（此前仅 inspect 链路有）
- **卷号推断修正** — 4 位年份（`19xx` / `20xx`）不再误判为卷号（如 `Series 2024`）
- **卷/话号推断增强（Kavita 语义对齐）** — 新增话/章族词库（話 / 话 / 話数 / 话数 / Chapter / Ch. / ch / chp / c / Episode / 화 / 회 / 回 / 集 / บทที่ / ตอนที่ / Глава），支持紧贴式（`c001` / `ch001` / `v01` / `T3` / `S01`）、卷+章同现（`Vol.0001 Ch.0001`、`Том 1 Глава 3`）、卷/章区间（`v16-17`、`c001-006` 取起始值）、小数（`025.5`）、尾字母半话（`153b` → 153.5）、多语言卷补漏（`冊N` / `1권` / `장N` / `季N` / `第N季`）、括号/方括号注释剔除；修复英文标记词被吞入系列名与区间取尾数的旧缺陷
- **魔数提升为命名常量** — `HEAD_READ_BYTES = 65536`、`DEFAULT_TIMEOUT = 600`
- **错误状态字符串收敛为枚举** — `ConvStatus` / `InspectStatus`
- **清理死代码** — 实跑链路 `used_names` 死参数、`target_cbz_path` 死形参、`sys.argv` 扫描
- **维护性** — `_VOLUME_PATTERNS` 补充匹配语义注释；游离注释归位
- **ComicInfo 错误分级** — 生成失败与写入失败拆分独立文案（`comicinfo.build_fail` / `comicinfo.write_fail`），错误提示更精准
- **`validate_cbz` 文档卫生** — 补充 EOCD 读取策略、ComicInfo 三连校验与返回语义说明（无行为变更）
- **类型注解补齐** — `_main() -> None` 等函数返回类型注解补齐
- **natural_key 超长数字兜底** — 超长纯数字串（Python int 位数上限）不再中断排序，回退按字符串比较
- **`extract_epub_to_temp` 异常自愈** — 解包中途异常时自行清理本次 mkdtemp 的临时目录再上抛，避免目录泄漏
- **ZIP_EOCD_READ_TAIL 命名常量** — `validate_cbz` 读取 EOCD 的尾部字节数提升为命名常量（70000，远大于单条 EOCD 上限）
- **磁盘预检目录级缓存** — `check_disk_space` 按目录缓存磁盘剩余空间（`_disk_free`），批量多文件时避免重复 syscall
- **ComicInfo setinfo 白名单移除 PageCount** — `PageCount` 不再可被 `--setinfo` 覆盖，始终按实际写入图片数计算（白名单 42 → 41）
- **HTML 实体解码补齐（P1-3）** — `extract_images_from_html` 正则路径对提取到的 src 补一轮 `html.unescape` 实体解码（此前仅 HtmlImgParser 兜底路径解码实体，畸形 HTML 中 `&amp;` 等实体 src 会残留）
- **残留 `.cbz.tmp` 启动告警** — 启动时扫描输出侧目录中上次中断/强杀/断电残留的 `*.cbz.tmp` 半成品，发现即 warning 提示（只告警不自动删除，保护数据），与原子写入 finally 兜底形成完整兜底链
- **JSON 状态契约文档化** — 见下方「JSON 输出契约」小节，三模式 `status` 枚举显性化，机器消费不再依赖猜测
- **文档与注释修正** — `--double-page` 过时注释（"写入 Manga>Yes"）改为"仅 DoublePage、Manga 用 --setinfo"；顶层用法行补 `--json` / `--json-out` / `--double-page` / `--drop-small` / `--debug`；`dedupe_ebook_files` docstring 兜底顺序补 epub；删除错位过时的旧签名注释
- **ComicInfo 来源标签本地化** — `--inspect` 预览块 Series/Number 的来源标注（`setinfo` / `opf` / `inferred`）改走 i18n、随界面语言显示（中文下 `[文件名推断]` 等）；`--json` 的 `series_source` / `number_source` 字段保持英文机器可读不变；原 `comicinfo.inferred` 单键重构为 `comicinfo.src.setinfo` / `comicinfo.src.opf` / `comicinfo.src.inferred` 三键（四语言同步）
- **dry-run JSON 输出修复** — `--dry-run` 配合 `--json` / `--json-out` 时输出结构化 JSON（此前契约缺失、文档称不输出）：每条记录带 `dry_run` 布尔标记区分试运行与真实运行，dry-run 状态取值 `will_skip` / `pending`；同步修正「JSON 输出契约」小节与参数说明中"dry-run 不输出"的旧描述
- **脚本头 SPDX 标识** — 补充 `SPDX-License-Identifier: GPL-3.0-only`

#### 评审修复（追加批）

- **GIF 帧数误报修复（P0）** — `gif_frame_count` 由 `head.count(b"\x2c")` 扫描 LZW 压缩数据改为按 GIF 结构块解析（仅计数图像描述符 `0x2C`，LZW 子块按边界整体跳过、不读内容），静态 GIF 压缩数据内任意 `0x2C` 不再被误计为帧而误标 `animated`；头部截断安全退出
- **zip-slip 盘符 / UNC 逃逸防护（P0）** — `_safe_zip_extract` 补 `Path.is_absolute()` 检查，拦截 `C:/...` 盘符与 `//server/share` UNC 绝对路径条目的越界写盘（此前仅拦 `/` 开头与 `..` 段）
- **`validate_cbz` 尾部 seek（P1）** — 文件 > 70KB 时 `seek` 只读末尾 `ZIP_EOCD_READ_TAIL`（70000）字节，不再整包 `read_bytes()` 后切片，大 CBZ 校验内存峰值由 O(文件大小) 降为 O(70KB)
- **`build_cbz_image_attrs` 流式取头（P1）** — 改用 `zf.open().read(HEAD_READ_BYTES)` 惰性解压取头，不再 `zf.read(name)` 整图解压后切片，大图条目解压与内存占用下降
- **`_fill_small_mark` 魔法数字替换（P2）** — 硬编码 `0.5` 替换为常量 `DEFAULT_DROP_SMALL_RATIO`，语义与行为完全不变

### [2.5.1] - 2026-08-20

#### 修复

- **去重不再误删同名 `.cbz`** — `--setinfo` / `--inspect` / `--unpack` 模式下，转换产物 `.cbz` 不再参与 mobi/azw/azw3/epub 的同名去重，已转好的 CBZ 可被正常修改 / 检查
- **flatten 同名冲突增加专用提示** — 平铺模式下第二个同名源文件跳过时，明确提示为 flatten 冲突（而非通用「目标已存在」），并建议用 `--overwrite`

### [2.5.0] - 2026-08-20

#### 变更

- **Manga 不再自动写入** — 双页检测（`--double-page`）只生成 `<Pages>` 逐页 `Type="DoublePage"` 标记，不再自动附带 `<Manga>Yes</Manga>` 声明（Mihon 等阅读器不读该字段，且避免无跨页也声明）；`Manga` 改由 `--setinfo Manga=Unknown|No|Yes|YesAndRightToLeft` 显式指定，取值限官方 v2.0 枚举，非法值输出 warning 并忽略
- **`--ext-priority` 支持 EPUB** — 仅接受 `mobi` / `azw` / `azw3` / `epub`；优先级未覆盖时兜底顺序调整为 `azw3 → epub → mobi → azw`（EPUB 优先于 mobi 族保留）
- **无图提示按扩展名分流** — EPUB 无图时改用中性提示（确认含漫画图片且未加密），不再误报 Kindle DRM；mobi/azw/azw3 仍提示 DRM 可能

#### 新增

- **`--setinfo` 白名单扩展（39 → 42）** — 新增 `CommunityRating`（0-5 评分）/ `MainCharacterOrTeam` / `Review` 三个官方 ComicInfo v2.0 字段
- **`--drop-small` 丢弃小图** — 默认关闭，开启后转换时剔除尺寸明显偏小的图片（封面缩略图 / 版权页等）：宽和高均 < 中位数 × 比例 判为小图（默认比例 0.5，可传 `0~1` 数值调整，`off`/`no`/`0` 关闭）；逐图读 PNG/JPEG 头部宽高，不引入新依赖；丢弃后 ComicInfo `PageCount` 按实际剩余图数重算；汇总 / `--log` / `--json` 新增"丢弃小图"计数（`--json` 输出 `dropped_small` 字段）；`--inspect` 预览提示"开启 --drop-small 时将丢弃 N 张"；横幅双页（宽不小）不会被误删

#### 文档

- **`--help` 四语言文案同步** — `help.description` / `help.target` / `help.ext_priority` 补充 `.epub`；`help.setinfo` 补充 Manga 枚举与显式指定说明
- **加密 EPUB 说明** — FAQ 明确加密 EPUB（Adobe DRM 等）无法转换，需先去除 DRM

### [2.4.0] - 2026-08-20

#### 新增

- **EPUB 输入支持** — 输入扩展名扩展为 `.mobi` / `.azw` / `.azw3` / `.epub`；`ebook_to_cbz` / `--inspect` / `--unpack` 按扩展名分流：EPUB（ZIP 容器）走 zipfile 安全解包（含 zip-slip 路径穿越防护），mobi/azw/azw3 仍走 `mobi.extract`；复用现有 OPF spine 提取与 ComicInfo 元数据链路，无平行实现
- **EPUB 封面兜底增强** — `get_opf_guide_cover_href` 三来源：① guide `type="cover"` ② manifest `properties="cover-image"`（EPUB3）③ `<meta name="cover">` 对应 item href（EPUB2）；封面 href 解析修正为相对 OPF 目录（EPUB 的 OPF 常在 OEBPS/ 子目录）
- **EPUB 元数据补充** — 无 EXTH 头时 `--inspect` 改从 OPF `dc:` 字段读取标题/作者/语言/出版日期/出版社；`get_drm_flag` 对 EPUB 直接放行（ZIP 容器无 PalmDB DRM 字段，避免误报）
- **`--prefer` 对 EPUB 静默忽略** — EPUB 无 mobi7/mobi8 双目录，天然单目录
- **EPUB3 nav 目录识别** — `--inspect` 优先从 OPF manifest `properties="nav"` 定位 nav 文档（兜底 `*nav*.xhtml`），解析 `<nav epub:type="toc">` 内 `<a>` 标题（含多级嵌套）；与 EPUB2 `toc.ncx` 同时显示，纯 EPUB3 无 .ncx 也能出目录
- **ComicInfo 系列/卷号元数据优先读取** — 生成 ComicInfo 时 Series/Number 优先取自 OPF 元数据（`dc:series` / `dc:number`、EPUB3 `belongs-to-collection` / `group-position`、calibre 的 `meta[name=calibre:series/series_index]`），`dc:number` 自动剥离卷标记（`卷12` → `12`），无 OPF 元数据时才回退文件名推测
- **双页检测（`--double-page`）** — 默认开启（阈值 2.0）：检测宽/高 ≥ 阈值的横幅跨页大图，ComicInfo 写入 `<Manga>Yes</Manga>` 顶层标记 + 逐页 `Type="DoublePage"`；`--double-page auto` 等同默认；`--double-page 2.5` 调整阈值；`--double-page off`（或 `no`/`0`）关闭；非法值报错
- **ComicInfo 字段来源标注** — `--inspect` 预览块为 Series/Number 标注来源（`[setinfo]` / `[opf]` / `[inferred]`），一眼分辨字段是用户指定、OPF 元数据还是文件名推测；`--json` 输出新增 `series_source` / `number_source` / `cover_source` 字段（取值 `setinfo` / `opf` / `inferred` / `filename` 等），供 AI/管道判断字段可信度

#### 变更

- **`--unpack` 安全解压统一** — CBZ 与 EPUB 共用 `_safe_zip_extract`（zip-slip 防护），逻辑单一化
- **`--setinfo` 修改 CBZ 改流式复制** — `modify_cbz_comicinfo` 不再整包读入内存，改为双句柄边读边写（1MB 块），仅 `ComicInfo.xml` 读入内存；保留各条目原始压缩方式/时间戳/属性，原子替换与异常清理不变（大包修改内存占用由 O(整包) 降至 O(单条目)）
- **ComicInfo 优先级重排（setinfo > OPF 元数据 > 文件名推测）** — 之前 Series/Number 直接吃文件名推断结果（`infer_series_number`）；现在优先用户 `--setinfo` 指定，其次 OPF 元数据，最后才文件名推测；无系列名纯卷标记文件（如 `Vol.01.mobi`）只回卷号不回系列名
- **卷号推测正则补全** — `infer_series_number` 新增覆盖：`卷N` 前缀式、`vN`、`第N册`/`N册`、`巻N` 前缀式、法文 `tome N`、韩文 `권N`、泰文 `เล่ม N`、俄文 `Том N`、中文数字卷（`第一卷`/`卷二`）、小数卷（`Vol 7.5`）
- **CoverSource 从 Notes 移除** — 封面来源不再写入 ComicInfo 的 `Notes` 字段（避免非标准备注进入跨软件共享的 ComicInfo.xml）；改由 `--inspect` 封面行与 `--json` 的 `cover_source` 字段展示，ComicInfo 只保留内容字段

### [2.3.1] - 2026-08-19

#### 修复

- **转换分支原子替换加固** — 先对临时文件 validate_cbz 校验、通过后才 `os.replace` 覆盖目标；失败仅清理 tmp，旧 CBZ 保留；ComicInfo 生成失败不再删除已有目标 CBZ；Ctrl+C（KeyboardInterrupt）残留 `.tmp` 由 finally 兜底清理
- **`--setinfo` 未知占位符 warning** — 白名单外占位符输出 warning 后按原样写入（新增 i18n 四语言键）
- **sanitize 补充 ASCII 控制字符 + 去除尾部点/空格**
- **find_opf 多 OPF 命名优先级** — `content.opf` / `package.opf` 优先
- **维护性** — docstring 残留清理；`_strip_html` 改用 HTMLParser（移除死 import html）

#### 文档

- **`--help` 文案补充（zh-CN/zh-TW/en/ja 四语言）** — `--setinfo` 值内含 `Key=` 结构时用多次传入、开启时输入中的 `.cbz` 就地修改 ComicInfo.xml；`--json`/`--json-out` 仅转换/修改模式输出（dry-run/inspect/unpack 不输出）、进度条写 stderr 不混流但 `2>&1` 合并重定向会混入
- **README 使用说明同步** — setinfo / JSON 小节补充上述行为说明，参数表对应行同步更新

### [2.3.0] - 2026-08-19

#### 新增

- **JSON 结构化输出** — `--json` stdout 单行紧凑 JSON（供 AI / 管道 / 脚本读取，开启时屏蔽人类可读文本输出）；`--json-out [FILE]` 将结构化结果写入 JSON 文件（缩进格式，省略文件名自动生成时间戳文件，行为对齐 `--log`）；两者可共存，转换模式与 `--setinfo` 修改模式均支持

#### 修复（随 v2.2.1 中间修复合并发布）

- **转换分支原子替换** — CBZ 打包改为先写 `xxx.cbz.tmp` 临时文件、全部成功后再 `os.replace` 覆盖目标；移除打包前删除旧 CBZ 及失败分支的删除逻辑，异常仅清理半成品 tmp。消除 Ctrl+C / 中途崩溃残留残缺 CBZ、覆盖失败丢旧文件的数据丢失风险（与 CBZ 修改模式原有原子替换逻辑一致）
- **`--inspect` PageCount 非数字告警** — ComicInfo 的 PageCount 非数字值时由静默忽略改为输出 warning（新增 i18n 键 `inspect.pagecount_non_numeric`，四语言同步）
- **`--timeout` 文案补充** — 说明超时后底层解包线程可能后台残留；`--overwrite` 提示文案同步为「将覆盖旧文件」，与实际原子替换行为一致

### [2.2.0] - 2026-08-18

#### 新增

- **CBZ 修改模式** — 输入为已有 `.cbz` 且带 `--setinfo` 时直接修改其 ComicInfo.xml：读原 XML → 覆盖指定字段、未指定字段保留原值 → 临时文件 + 原子替换（`os.replace`）；纳入 `--dry-run` 预览 / 汇总统计 / `--log`
- **setinfo 白名单** — `--setinfo` 字段名需在 ComicInfo 标准字段白名单内（39 个简单字段，Pages 复杂结构排除），白名单外字段输出 warning 并忽略
- **源文件更新自动重转** — 断点续跑时比较源文件与目标 CBZ 的 mtime，源文件更新则自动重新转换
- **`--unpack` / `--setinfo` 支持 CBZ 输入** — 收集阶段在 `--unpack` 或 `--setinfo` 时也收集 `.cbz` 文件
- **`--prefer auto`（默认）** — 双目录 mobi 默认自动选择：优先 mobi8，mobi8 无图片自动回退 mobi7；明确指定 `mobi7`/`mobi8` 时该目录无图片自动回退另一份
- **Summary HTML 清理** — ComicInfo 的 Summary 字段自动去除 HTML 标签（纯文本落盘）
- **封面来源标记** — ComicInfo 的 Notes 字段追加 `CoverSource`（OPF guide / 文件名匹配）
- **CBZ 预处理** — `.cbz` 输入同样执行 0 字节 / `--min-size` 检查
- **`--inspect` PageCount 一致性检查** — 比对 CBZ 内 ComicInfo 的 PageCount 与实际图片数，不一致时提示

#### 变更

- **`--unpack` 路径安全** — cbz 解包增加 zip-slip 路径穿越防护（拒绝 `..` / 绝对路径条目），并输出解包汇总
- **多 OPF 提示** — 目录下存在多个 `.opf` 时输出 warning 并取第一个
- **损坏 CBZ 重转原因** — 断点续跑遇损坏 CBZ 自动重转时输出 `validate_cbz` 的具体失败原因
- **HTML 图片路径兼容** — 提取 `<img>` 时去除 src 中的 query / fragment（`?` / `#`）再拼本地路径
- **目录创建时机** — 目标 CBZ 已存在且将 SKIP 时不再提前创建输出目录
- **代码卫生** — `ebook_to_cbz` 返回类型注解补全三元组；`_auto_language` 末尾显式标注

### [2.1.0] - 2026-08-17

#### 新增

- **断点续跑（默认行为）** — 目标 CBZ 已存在且 `validate_cbz` 校验有效时直接 SKIP，损坏/无效自动重新转换；`--overwrite` 无条件覆盖
- **失败分类** — `ebook_to_cbz` 返回三元组 `(result, status, reason)`，失败原因分类 `timeout` / `drm` / `corrupt` / `no_images` / `comicinfo` / `verify` / `other`，主流程新增 `failed_reasons` 统计并在汇总输出
- **`--inspect` 支持 CBZ** — 合并进 `inspect_ebook`，CBZ 分支纯 zipfile 读取不解压；抽出 `image_dimensions_bytes(bytes)` 复用
- **`--inspect` 输出增强** — 封面行加分辨率+大小，格式统计加总文件数，Spine 前 5 列表每行加宽高
- **`--setinfo FIELD=VALUE`** — 覆盖/新增 ComicInfo 字段（可多次指定，优先级最高）；VALUE 支持固定值 / `%series` / `%number` / `%title`/ `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M`；智能拆分（逗号后紧跟字段名=才拆）；CBZ 修改模式直接重写 zip；`--inspect` 预览块同步应用
- **ComicInfo 并入同一次 zip 写入** — 删除 `write_comicinfo` 函数，Step4 with 块内 `zf.writestr`
- **`--log` 自动命名** — `nargs="?"` + `const="auto"`，auto 时生成 `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（当前目录）
- **`--unpack` 解包查看** — 只解压不转换，mobi 走 extract 保留完整结构，cbz 走 extractall；默认解到文件名同名目录，已存在自动加序号避让 `(2)(3)`

### [2.0.2] - 2026-08-17

#### 变更

- `infer_series_number` 支持括号后缀：文件名带 `(作者)` 等括号内容时不再阻断卷号推断
- 纯卷标记（`Vol.01` / `第 01 卷` / `01巻` 等）只返回卷号 `(None, number)`，不再返回 `(None, None)`，ComicInfo 可写入 Number
- `--flatten` 同名处理改为 SKIP/`--overwrite`：平铺输出根下同名文件不再自动编号重转 `(2).cbz`，未指定 `--overwrite` 时跳过（SKIP），指定时覆盖首选名；dry-run 与实跑保持一致
- 移除已无引用的 `unique_path` 函数

#### 修复

- 修复 PageCount 一致性：物理去重提前到 ComicInfo 生成之前，PageCount 与打包均用去重后实际写入数
- 修复 `run_with_timeout` 跨版本：except 同时捕获内置 `TimeoutError` 与 `concurrent.futures.TimeoutError`（Python 3.10 兼容）
- 修复 `infer_series_number` 点号失效：改用 `path.name` 手动去扩展名，`Sample Series Vol.01` 等点号卷号可正确推断
- LanguageISO 白名单 + alias：ISO 639-1 全量 184 个白名单校验，新增 `jp→ja` / `cn→zh` / `zhtw→zh` 等常见别名
- Year 严格日期解析：优先完整日期字段，范围/多值（`2001-2005`）返回 None
- `emit` warning 在 `--quiet` 下可见
- EXTH 循环变量 `t` 改名 `type_id`，避免遮蔽全局 `t()`
- 正则 img src 提取补 `unquote`，与 HtmlImgParser 兜底路径一致
- `--language` 参数容错：支持 `zh`/`cn`/`zhtw`/`jp` 等常见写法，新增 `_normalize_lang` 规范化（argparse 移除 choices 限制）

### [2.0.1] - 2026-08-17

#### 修复

- 修复 `infer_series_number` 对无系列名卷标记文件名（`Vol.01` / `Volume 01` / `01巻` 等）误推断系列名的问题，新增 `_is_volume_marker` 卷标记词过滤

### [2.0.0] - 2026-08-14

#### 新增

- 默认生成 ComicInfo.xml（写入 CBZ ZIP 根目录，UTF-8 含 XML 声明），新增 `--no-comicinfo` 关闭
- 新增 4 个函数：`build_comicinfo`（用 `xml.etree.ElementTree` 生成，禁止手工拼接字符串）、`write_comicinfo`、`normalize_language`（语言代码标准化为 ISO 639-1）、`infer_series_number`（高置信度推断 Series/Number，支持 `001`/`01`/`1`/`Vol.01`/`Vol 01`/`Volume 01`/`第 01 卷` 等形式，无法高置信度判断时返回 None，宁缺勿错）
- 字段映射：Title=OPF title→EXTH title→文件名 stem，Writer=OPF creator→EXTH author，Publisher=OPF publisher→EXTH publisher，Year=PublicationDate 年份，LanguageISO=电子书自身语言（不按文件名猜），PageCount=最终写入 CBZ 的实际图片数（必写），Series/Number=文件名高置信度推断，Summary=OPF description（读到才写）；无可靠来源的字段直接省略不生成空标签
- 流程插入：确定最终图片集合后构建 ComicInfo，创建 CBZ 时图片+ComicInfo.xml 一起写入；完整性校验新增 3 项（ComicInfo.xml 存在、可被标准 XML parser 解析、根节点为 ComicInfo）；ComicInfo 生成或验证失败=整个转换任务失败，禁止 `--delete` 删除源文件
- `--dry-run` 不创建 ComicInfo.xml，但输出一行提示 ComicInfo 是否启用
- `--inspect` 输出追加 ComicInfo 预览块（Title/Series/Number/Writer/Publisher/Year/LanguageISO/PageCount/Summary 有值才显示），推断字段明确标记 `[inferred]`
- i18n 四语言新增 6 键：`comicinfo.generating` / `comicinfo.created` / `comicinfo.disabled` / `comicinfo.invalid` / `comicinfo.inferred` / `help.no_comicinfo`

### [1.9.1] - 2026-08-14

#### 新增

- `--inspect-all` 单独使用（未配合 `--inspect`）时自动启用 `--inspect`，并输出 warning 提示（四语言新增 `warn.inspect_all_auto_enable` 键）
- `--inspect` 说明更新：位置参数为单个文件时直接检查该文件，为目录时随机抽查 1 个
- `--inspect-all` 说明更新：需配合 `--inspect` 使用，单独使用将自动启用 `--inspect`

### [1.9.0] - 2026-08-14

#### 破坏性变更（Breaking Change）

- `--output-dir DIR` 由「一律平铺到 DIR」改为「**默认保留相对输入的子目录结构**」（如 `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`）
- 迁移方式：旧命令 `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output` 需改为 `python manga-mobi2cbz.py ComicsLibrary --output-dir CBZ_Output --flatten` 才能恢复「平铺」行为

#### 新增

- `--flatten`：仅与 `--output-dir` 联用，将全部 CBZ 平铺到输出目录根下；平铺命名规则：文件直接在输入根下 → `stem`，位于子目录 → `父目录名 - stem`；非法文件名字符（`<>:"/\|?*`）替换为 `_`
- 平铺重名自动唯一化：`base.cbz` → `base (2).cbz` → `base (3).cbz` …，不静默覆盖、不跳过，编号时输出 info 提示
- 仅使用 `--flatten` 而无 `--output-dir` 报错退出（exit 2），文案多语言化
- 每次运行打印一次输出模式提示（保留结构 / 平铺），四语言表新增 `output.mode_preserve` / `output.mode_flatten` / `output.renamed_due_to_conflict` / `output.flatten_requires_dir` / `error.flatten_without_output_dir` / `rel_fallback` 等键
- 相对子目录路径计算失败（如跨盘符）时回退 `DIR/stem.cbz` 并输出 warning
- 单文件输入 + `--output-dir` 输出 `DIR/stem.cbz`（不套子目录）
- `--overwrite` 保留结构语义不变；平铺模式以唯一化避让为主，`--overwrite` 仍作用于最终选中的路径

#### 重构

- `target_cbz_path` 新增 `flatten` / `input_root` / `used_names` 参数；新增 `sanitize_filename_component` / `flat_base_name` / `unique_path` 独立函数
- dry-run 平铺唯一名按处理顺序维护已占用名集合，与正式运行一致

#### 修复与增强（并入 v1.9.0，不升号）

- `run_with_timeout` 返回值改为 `(timed_out, result)` 二元组：超时 → `(True, None)`，正常 → `(False, 函数返回值)`，消除“超时”与“正常返回 None”的歧义
- `--inspect` 超时分支追加提示「临时目录可能残留，请手动清理」（四语言新增 `inspect_mode.timeout_residue` 键）
- 打包阶段 `seen` 增加归一化路径判物理重复：同一物理文件重复出现时跳过不写入（重名不同文件仍序号前缀），输出去重计数（四语言新增 `convert.dedup_physical` 键）
- 新增 `HtmlImgParser`（HTMLParser 子类）兜底提取 `<img src>`：HTML 实体由 HTMLParser 自动解码 + `unquote` 处理 `%XX`，接入 OPF/spine 的 HTML 图片提取，正则未命中时启用，不破坏 ElementTree 主流程
- `--dry-run` 增加输出目录可写性检查（`--output-dir` 或各源文件所在目录），不可写时输出 warning（四语言新增 `dryrun.output_not_writable` 键）

### [1.8.0] - 2026-08-14

#### 新增

- 轻量多语言：`--language auto|zh-CN|zh-TW|ja|en`（默认 `auto` 按系统 locale 自动判定：简体归 zh-CN、繁体 zh-TW/zh-Hant 归 zh-TW、日文 ja/Japanese 归 ja、非 zh/ja 归 en）；全量输出文案与 `--help` 随语言翻译（`--help` 通过预解析 `--language` 后再构建 parser 实现），缺键回退 en→键名不抛异常；业务代码不写 `if lang` 分支，参数名/枚举/书籍 metadata/OPF/DRM/spine 等专有词不翻译；标签常量 `TAG_*` 全部移除改为 `t()` 键
- 支持 `.azw` / `.azw3` 输入：输入扩展名扩展为 `.mobi` / `.azw` / `.azw3`（大小写不敏感），三种格式统一复用 `extract → OPF/spine → 封面 → 对齐 → 打包 → 校验` 链路，无平行实现
- `--ext-priority EXTS`：同目录同名（仅扩展名不同）时保留哪种格式——逗号分隔、顺序即优先级从高到低，仅接受 `mobi`/`azw`/`azw3`，默认 `azw3`；优先级未覆盖的组回退兜底顺序 azw3→mobi→azw，并输出 warning；与 `--prefer`（双目录 mobi7/mobi8 选择）完全无关
- 同名扩展名去重：同目录同主文件名（分组键 `parent.resolve() + stem.lower()`）只保留一份，不同目录同名不去重；去重先于路径计算与进度计数，跳过原因随日志输出
- 魔数预检查扩展到三种格式：偏移 60 处统一校验 `BOOKMOBI` 魔数；扩展名正确但魔数错误（或 `.azw/.azw3` 魔数异常）的文件不再直接判损坏跳过，而是输出 warning 后仍尝试解包（`mobi.extract` 自带二次校验，解包失败正常计入失败列表）
- `--delete` 与 `--inspect` / `--inspect-all` 同步支持 `.mobi` / `.azw` / `.azw3` 三种格式
- 文件级进度条：`--progress` 强制显示、`--no-progress` 强制关闭；默认自动判断（stderr 为 TTY 且文件数≥2 时显示，非 TTY 默认关闭），两参同传时以最后出现的参数为准；`--quiet` 下进度条默认保留，`--no-progress` 时关闭；覆盖 convert / inspect / dry-run 三个模式；total 严格等于去重后最终列表长度，显示当前数/总数、百分比、ETA、平均耗时、当前文件名（截断 40 字符）；进度条写 stderr、不进 emit/`--log`；tqdm 为可选依赖，缺失时降级为简单文本进度不崩溃

#### 重构

- `collect_mobi_files` 更名为 `collect_ebook_files`（保留旧名别名 `collect_mobi_files` 兼容）；`precheck_mobi` → `precheck_ebook`、`mobi_to_cbz` → `ebook_to_cbz`、`inspect_mobi` → `inspect_ebook`
- 输入扩展名集合常量化 `SUPPORTED_INPUT_EXTENSIONS`；`PREFER_EXT_ORDER` 更名为 `KEEP_EXT_ORDER`
- docstring、CLI 帮助与运行日志文案统一为「电子书文件」（mobi 文件 → 电子书文件），帮助描述改为 `mobi/azw/azw3 漫画批量转 cbz`

#### 代码卫生与体验优化（并入 [1.8.0]）

- 删除重复的 `from concurrent.futures import ThreadPoolExecutor` 导入
- `LANGUAGES` 字典按功能分区补充中文注释（【预处理】【转换】【检查】【汇总】，含 help/progress/tag 等分区）
- `--language auto` 时 INFO 级打印「识别语种为 X」（`--quiet` 时抑制，走 `emit` + `t()`）
- 魔数校验降级：`precheck_ebook` 魔数失败由「判损坏跳过」改为 warning 提示 + 仍尝试解包（`extract` 自带二次校验，解包失败计入失败列表）
- `--ext-priority` 非法值报错文案多语言化（四语言表新增 `error.ext_priority_empty` / `error.ext_priority_invalid` 键）
- argparse 参数定义与主要函数输入参数补充中文注释（说明输入内容与输出内容）

### [1.7.0] - 2026-08-13

#### 新增

- `--compress LEVEL`：zip 压缩级别 0-9，`0`=不压缩（默认，图片本身已压缩），`1-9`=deflate 压缩，PNG 源可显著减小体积，级别越高越小但越慢，JPEG 源收益有限不建议开
- `--inspect` 检查模式：随机抽查 1 个 mobi（`--inspect-all` 全量），只解包读取内部信息不生成 CBZ，结束后自动清理临时目录；输出基础检查（魔数/大小/DRM 标记）、EXTH 元数据（标题/作者/语言/出版日期/出版社/ISBN，读到才显示）、双目录标记、OPF 与 spine 提取数、目录全部图片数、封面、图片格式分布、主流分辨率（主流高/宽 + 另一维范围）、压缩建议；疑似 DRM（无图）与解包超时单独计数
- `--inspect` 增强：封面检测改为 OPF guide `type="cover"` 官方引用优先（未命中回退文件名匹配）；spine 提取图片前 5 个文件名竖排预览；新增目录(NCX) 条目数 + 前 3 条标题预览；EXTH 元数据新增 ASIN(type113)、版权(type109)；DRM 双重判断（头部标记有→直接判有并跳过解包；无标记+解包图片 0→疑似；无标记+有图片→无），汇总行新增 DRM 标记计数

#### 重构

- 打包分支重构：`compress>0` 用 `ZIP_DEFLATED`+`compresslevel`，否则 `ZIP_STORED`，消除旧版 Python 在 STORED 下传 `compresslevel=None` 的弃用警告
- `--inspect` 双目录选择统一走 `select_mobi_dir` 公用函数（新增 prefer 参数由 `--prefer` 控制），不再手写判断；输出行缩进统一为 2 空格，修复 OPF 行缩进不一致

### [1.6.0] - 2026-08-13

#### 新增

- `--output-dir DIR`：CBZ 输出到指定目录（自动创建），不再强制与源电子书同目录；`--overwrite` 存在性判断同样基于输出目录
- 预处理过滤：0 字节、文件头校验失败（偏移 60 处无 `BOOKMOBI` 魔数，疑似损坏或非 mobi）的文件直接跳过，日志输出跳过文件完整路径与原因
- `--dry-run` 试运行模式：只扫描与预处理，打印每个文件的转换流程与目标输出路径，不实际解压打包、不创建输出目录、无任何磁盘写入，并同步打印预处理过滤列表（与真实运行保持一致）
- `--min-size BYTES`：过滤小于指定字节数的 mobi（不带数字默认 1000，`0` 关闭，不传则关闭大小过滤），兜住头部恰好完整但内容被截断的边缘损坏样本；预处理同时增加"无法读取文件（OSError）"的跳过原因分支
- 耗时统计：每个文件转换耗时实时输出，汇总底部输出总耗时（成功/失败/跳过均计入）
- 汇总新增一行式转换统计（成功/跳过/失败三类数量，含 0）：某类为 0 时原有明细行不打印，统计行保证三类数量始终可见

#### 重构

- 状态魔法字符串重构为 `ConvStatus` 枚举（`OK`/`SKIP`/`FAIL`），`mobi_to_cbz` 返回类型改为 `tuple[Path | None, ConvStatus]`，主循环分支与返回处统一使用枚举成员，避免拼写错误
- 输出标签提取为常量（`TAG_INFO`/`TAG_FAIL`/`TAG_ERROR`/`TAG_SKIP`/`TAG_OVERWRITE`/`TAG_CLEAN`/`TAG_SORT`/`TAG_DEDUP`/`TAG_DONE`/`TAG_VERIFY`/`TAG_VERIFY_FAIL`/`TAG_TIMEOUT`/`TAG_ELAPSED`/`TAG_FILE`/`TAG_PENDING`/`TAG_WILL_SKIP`/`TAG_DRYRUN`），统一管理方便后期统一修改输出样式
- 加重 `run_with_timeout` 线程限制注释：明确超时后 `mobi.extract` 工作线程会后台残留、持续占用内存/IO，批量大量损坏文件可能堆积僵尸线程；后续可改 `multiprocessing` 实现可终止子进程，但增加跨平台兼容复杂度，暂未采用
- 顶层全局异常捕获：`main()` 统一 `try/except`，参数解析/文件收集等主循环外阶段的未捕获异常与 Ctrl+C 经 `emit` 输出堆栈到控制台与日志（带时间戳），不再裸堆栈退出
- `--short-summary` 精简汇总：成功/跳过/预处理跳过文件只显示数量不列出路径（失败文件始终全路径列出），dry-run 不受影响，与 `--quiet` 互补

### [1.5.0] - 2026-08-13

#### 新增

- `--timeout` 单文件转换超时保护：默认 600 秒，损坏/加密/超大 mobi 导致底层 `mobi.extract()` 无限阻塞时自动跳过该文件并计入失败，不再卡死整批转换；`0` 表示不限制
- 路径大小写兼容：封面比对与目录对齐改用归一化小写路径，Windows 不区分大小写的文件系统下不会因大小写命名差异误判重复/遗漏
- 输出时间戳：所有输出（控制台与 `--log` 日志文件）自动追加 `[YYYY-MM-DD HH:MM:SS]` 前缀，方便定位每次转换的执行时刻

#### 变更

- 日志写入容错：`--log` 写入失败（非法字符/超长路径、磁盘满、只读分区、文件被独占等）时不再静默吞掉异常，改为捕获全部 `Exception` 并打印一次警告，避免用户误以为日志已保存
- Ctrl+C 中断兜底：批量转换中途按 Ctrl+C 不再直接抛异常退出，主循环捕获 `KeyboardInterrupt` 后强制输出当前已完成/失败的进度汇总
- 汇总补全跳过列表：`--overwrite` 未开启时因目标 cbz 已存在而跳过的文件计入"跳过文件"计数并列出完整路径
- `--overwrite` 覆盖重生成的标记仅保留单文件处理时的 `[覆盖]` 日志，不进最终汇总（`--log` 写入日志文件）
- 移除无效的外层 `TemporaryDirectory` 兜底：解压临时目录仍由 `extract_temp_paths` + `finally` 统一清理

### [1.4.0] - 2026-08-13

#### 新增

- 依赖检测前置到模块顶部，启动即校验
- DRM 加密识别提示：解压失败或未提取到任何图片时，明确提示可能为 DRM 加密的 Kindle 漫画，mobi 库无法解密，避免静默失败
- `--overwrite` 参数：目标 cbz 已存在时强制重新生成，更新漫画后无需手动删除旧 cbz
- `--quiet` 静默模式：只显示错误与最终汇总，批量转换时不再刷屏
- `--log FILE`：将全部输出追加写入指定日志文件
- 转换开始前列出待转换 mobi 文件完整路径，转换完成后列出输出 cbz 文件完整路径
- 转换完成后列出失败文件数量与完整路径（跳过已存在的不计为失败）

#### 修复

- 修复临时目录残留：`mobi.extract` 不支持 `output_dir` 参数，改为仅传输入文件并记录其生成的解压路径，finally 统一清理，正常 / Ctrl+C / 异常均不残留

### [1.3.0] - 2026-08-13

#### 新增

- 封面兜底：spine 提取后自动扫描文件名含 cover/front 的图片，封面已在列表中则以列表顺序为准，仅缺失时插入首位补齐
- 修复封面仅由 OPF metadata meta 定义、未被 spine 引用时导致的丢页（如 `cover00198.jpeg`）
- 目录对齐兜底：目录图片数与收集数不一致时，多出的图片默认按自然排序追加到 cbz 末尾；`--drop` 可改为放弃，处理结果会打印输出

### [1.2.0] - 2026-08-13

#### 新增

- OPF spine 顺序提取图片：解析 manifest 与 spine itemref，按真实阅读顺序排列
- `--version` 参数，支持 `python manga-mobi2cbz.py --version` 查看版本
- `select_mobi_dir` 目录选择逻辑，优先选定 mobi7/mobi8 目录再提取图片
- 排序兜底分级：spine 提取为空 / 未找到 OPF 时自动回退文件名自然排序

#### 变更

- 重名图片改用序号前缀（`{idx:04d}_`），保证顺序且不冲突
- 脚本更名为 `manga-mobi2cbz.py`

### [1.1.0] - 2026-08-13

#### 新增

- 版本号机制：`__version__` 与 `SCRIPT_NAME` 常量

### [1.0.0] - 2026-08-12

#### 新增

- 首个可用版本：递归收集 mobi、批量转 cbz、双目录去重、EOCD + testzip 完整性校验、失败清理半成品

## License

本项目使用 [GPL-3.0](./LICENSE) 许可。

### 第三方依赖许可

本工具运行时依赖 mobi 库（v0.4.1，Titusz Pan 维护版），其许可证为 GPL-3.0-only，公开分发请遵守 GPL-3.0 相关要求。
