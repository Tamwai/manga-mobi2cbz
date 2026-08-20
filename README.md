**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md)

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
- **目录对齐兜底** — 目录图片数与收集数不一致时，多出的图片默认按自然排序追加到 cbz 末尾；`--drop-extra` 可改为放弃，处理结果会打印输出
- **双目录去重** — 自动识别 mobi7/mobi8 双目录，默认 `auto`：优先保留 mobi8（画质可能更好），mobi8 无图片时自动回退 mobi7；`--prefer mobi7|mobi8` 可强制指定，指定目录无图片时自动回退另一份
- **轻量多语言** — `--language auto|zh-CN|zh-TW|ja|en` 切换输出语言（默认 `auto` 按系统 locale 自动判定：简体中文归 zh-CN、繁体中文归 zh-TW、日文归 ja、其余归 en）；全量输出文案与 `--help` 随语言翻译，参数名/枚举/专有词不翻译
- **同名扩展名去重** — 同目录下仅扩展名不同（如 `Vol1.mobi` + `Vol1.azw3`）时只保留一份，`--ext-priority` 控制保留优先级（默认 azw3）
- **自然排序** — 按页码自然排序，避免 `10.jpg` 排在 `2.jpg` 前面
- **完整性校验** — 转换后自动校验 CBZ 文件，损坏则删除并提示
- **ComicInfo.xml 元数据** — 默认在 CBZ 根目录生成 ComicInfo.xml（UTF-8，含 XML 声明），写入 Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary 漫画元数据；Series/Number 由文件名高置信度推断（支持 `001` / `01` / `1` / `Vol.01` / `Vol 01` / `Volume 01` / `第 01 卷` 等形式），无系列名的卷标记（如 `Vol.01` / `01巻`）不推断，无法高置信度判断时省略（宁缺勿错）；无可靠来源的字段不生成空标签；`--no-comicinfo` 关闭生成
- **无压缩打包** — 图片已是压缩格式，ZIP 默认仅存储不压缩，速度快、体积小
- **可选压缩** — `--compress LEVEL` 启用 deflate 压缩（1-9），PNG 源漫画可显著减小体积，级别越高越小但越慢；JPEG 源收益有限，不建议开启（默认 `0` 不压缩）
- **检查模式** — `--inspect` 随机抽查 1 个电子书（`--inspect-all` 全量），只解包读取内部信息不生成 CBZ：基础检查（魔数/大小/DRM 双重判断）、EXTH 元数据（标题/作者/语言/出版日期/出版社/ISBN/ASIN/版权，读到才显示）、双目录标记、OPF 与 spine 提取数（前 5 文件名竖排预览）、目录(NCX) 条目数与预览、目录全部图片数、封面（OPF guide 官方引用优先，未命中回退文件名匹配）、图片格式分布、主流分辨率（主流高/宽 + 另一维范围）、压缩建议；DRM 头部标记有→直接判有并跳过解包，无标记+图片 0→疑似，无标记+有图片→无；结束后自动清理临时目录
- **可选删除原文件** — `--delete` 参数转换成功后自动删除原始电子书
- **强制覆盖** — `--overwrite` 参数对已存在的 cbz 强制重新生成，更新漫画后无需手动删旧文件
- **单文件超时保护** — `--timeout` 参数限制单个文件转换时长，损坏/加密/超大电子书导致底层解包无限阻塞时自动跳过并计入失败，不再卡死整批转换（默认 600 秒，`0` 表示不限制）
- **静默模式** — `--quiet` 批量转换只显示错误与汇总，不再刷屏；`--log FILE` 可将全部输出追加写入日志文件
- **精简汇总** — `--short-summary` 成功/跳过/预处理跳过文件只显示数量不列出路径（失败文件始终全路径列出），与 `--quiet` 互补，适合大批量目录
- **DRM 加密识别** — 遇到 DRM 加密的 Kindle 漫画时明确提示无法解密，避免静默失败
- **路径大小写兼容** — 封面比对与目录对齐使用归一化小写路径，Windows 不区分大小写的文件系统下不会因大小写命名差异误判重复/遗漏
- **输出时间戳** — 每条输出自动追加 `[YYYY-MM-DD HH:MM:SS]` 前缀，控制台与日志文件一致，方便定位每次转换的执行时刻
- **自定义输出目录** — `--output-dir DIR` 将 CBZ 输出到指定目录（自动创建），默认保留相对输入的子目录结构（如 `One Piece/001.mobi` → `DIR/One Piece/001.cbz`）；加 `--flatten` 平铺到目录根下，同名文件未指定 `--overwrite` 时跳过（SKIP）
- **预处理过滤** — 0 字节、文件头损坏（偏移 60 处无 `BOOKMOBI` 魔数）的电子书在预处理阶段直接跳过，日志输出跳过文件完整路径与原因
- **大小下限过滤** — `--min-size BYTES` 过滤小于指定字节数的电子书（不带数字默认 1000，`0` 关闭，不传则关闭大小过滤），兜住头部恰好完整但内容被截断的边缘损坏样本
- **试运行模式** — `--dry-run` 只扫描与打印转换流程，不实际解压打包，适合先确认转换结果
- **断点续跑** — 目标 CBZ 已存在且完整性校验有效时直接跳过（SKIP）；源文件比 CBZ 更新时自动重新转换；损坏/无效自动重新转换；`--overwrite` 无条件覆盖
- **失败分类** — 转换失败按原因分类统计（timeout / drm / corrupt / no_images / comicinfo / verify / other），汇总输出各类失败数量
- **检查模式支持 CBZ** — `--inspect` 可直接检查 `.cbz` 文件（纯 zipfile 读取不解压）；封面行加分辨率+大小、格式统计加总文件数、Spine 前 5 列表每行加宽高
- **ComicInfo 字段覆盖** — `--setinfo FIELD=VALUE` 覆盖/新增 ComicInfo 字段（优先级最高），VALUE 支持固定值 / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN` 占位符，可多次指定；字段名需在 ComicInfo 标准字段白名单内，白名单外字段 warning 忽略；输入为已有 CBZ 时直接修改其 ComicInfo.xml（未指定字段保留原值）
- **日志自动命名** — `--log` 不带文件名时自动生成 `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（当前目录）
- **解包查看** — `--unpack` 只解压不转换，输出到源文件同名子目录（已存在自动加序号避让），mobi 保留完整结构、cbz 直接解包（含 zip-slip 路径穿越防护）；`--unpack` / `--setinfo` 时也会收集 `.cbz` 输入
- **耗时统计** — 每个文件转换耗时实时输出，汇总底部显示总耗时
- **JSON 结构化输出** — `--json` stdout 单行紧凑 JSON（供 AI / 管道 / 脚本读取，开启时屏蔽人类文本输出）；`--json-out [FILE]` 将结构化结果写入 JSON 文件（缩进格式，省略文件名自动生成时间戳文件，行为对齐 `--log`）；两者可共存，转换模式与 `--setinfo` 修改模式均支持

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
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi"
```

### 批量转换整个目录（递归搜索所有 .mobi / .azw / .azw3 / .epub）

```bash
python manga-mobi2cbz.py "D:\Manga"
```

### 转换成功后删除原始电子书

```bash
python manga-mobi2cbz.py "D:\Manga" --delete
```

### 双目录 mobi 时保留 mobi7 版本

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --prefer mobi7
```

### 目录中有未被收集的多余图片时放弃追加

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --drop-extra
```

### 已存在 cbz 时强制重新生成

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --overwrite
```

### 限制单文件转换超时（防止损坏文件卡死批量任务）

```bash
python manga-mobi2cbz.py "D:\Manga" --timeout 300
```

### 输出到自定义目录（默认保留相对子目录结构）

```bash
python manga-mobi2cbz.py "D:\Manga" --output-dir "E:\CBZ"
```

### 平铺输出（所有 CBZ 直接放到输出目录根下）

```bash
python manga-mobi2cbz.py "D:\Manga" --output-dir "E:\CBZ" --flatten
```

### 试运行：只扫描并打印转换流程，不实际转换

```bash
python manga-mobi2cbz.py "D:\Manga" --dry-run
```

### 静默模式 + 输出写入日志

```bash
python manga-mobi2cbz.py "D:\Manga" --quiet --log convert.log
```

### 精简汇总（大批量目录，成功/跳过只看数量）

```bash
python manga-mobi2cbz.py "D:\Manga" --quiet --short-summary --log convert.log
```

### 开启 zip 压缩（PNG 源漫画可显著减小体积）

```bash
python manga-mobi2cbz.py "D:\Manga" --compress 9
```

### 检查模式：随机抽查 1 个电子书内部信息（元数据/结构/图片/分辨率/DRM/NCX 目录）

```bash
python manga-mobi2cbz.py "D:\Manga" --inspect
```

### 检查全部电子书内部信息

```bash
python manga-mobi2cbz.py "D:\Manga" --inspect --inspect-all
```

### 覆盖/新增 ComicInfo 字段（可多次指定，优先级最高）

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --setinfo "Title=天是紅河岸" --setinfo "Number=%number" --setinfo "Summary=hello, world"
```

> 说明：`--setinfo` 只在逗号后紧跟「字段名=」时才拆分，若值本身含 `Key=...` 结构，请拆成多次 `--setinfo` 传入以免误拆分。输入目录若混有已有 `.cbz` 与 `.mobi`，开启 `--setinfo` 时 `.cbz` 会被就地修改其 `ComicInfo.xml`（未指定字段保留原值），其余文件照常转换。

### 解包查看（只解压不转换，输出到源文件同名子目录）

```bash
python manga-mobi2cbz.py "D:\Manga\Vol1.mobi" --unpack
```

### JSON 结构化输出（stdout 单行 / 写入文件）

```bash
python manga-mobi2cbz.py "D:\Manga" --json
python manga-mobi2cbz.py "D:\Manga" --json-out
python manga-mobi2cbz.py "D:\Manga" --json --json-out result.json
```

> 说明：`--json` / `--json-out` 仅在「转换」或「CBZ 修改」执行后输出结构化结果；`--dry-run`、`--inspect`、`--unpack` 模式不输出。进度条与人类可读提示写 stderr、JSON 写 stdout 天然分流；若用 `2>&1` 合并重定向会把进度条混入 JSON 流，建议同时加 `--no-progress`。

### 查看版本号

```bash
python manga-mobi2cbz.py --version
```

## 参数说明

| 参数                    | 说明                                                                                                                                                                               |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `target`              | 电子书文件路径或包含电子书（.mobi/.azw/.azw3/.epub）的目录（必填）                                                                                                                                           |
| `--language LANG`     | 输出语言：`auto` 按系统 locale 自动选择（zh 前缀→中文，zh-TW/zh-Hant→繁体中文，ja/Japanese→日文，否则→英文），或指定 `zh-CN`/`zh-TW`/`ja`/`en`（默认 `auto`）；兼容常见写法：`zh`/`cn`→zh-CN，`zhtw`/`tw`→zh-TW，`jp`→ja，`eng`→en |
| `--delete`            | 转换成功后删除原始电子书文件（默认不删除）                                                                                                                                                            |
| `--prefer`            | 双目录 mobi 时保留哪份：`auto` / `mobi7` / `mobi8`（默认 `auto`）；`auto` 优先 mobi8、mobi8 无图片自动回退 mobi7；明确指定 `mobi7`/`mobi8` 时该目录无图片自动回退另一份                                                        |
| `--drop-extra`        | 目录中有未被收集的多余图片时放弃追加（默认追加到 cbz 末尾）                                                                                                                                                 |
| `--overwrite`         | 目标 cbz 已存在时强制重新生成（默认跳过）                                                                                                                                                          |
| `--ext-priority EXTS` | 同目录同名（仅扩展名不同）时保留哪种格式：逗号分隔、顺序即优先级从高到低，仅接受 mobi/azw/azw3，默认 azw3；优先级未覆盖时回退兜底顺序 azw3→mobi→azw；与 `--prefer`（双目录选择）无关                                                                 |
| `--timeout`           | 单文件转换超时秒数，超时自动跳过并计入失败（默认 600，`0` 表示不限制）                                                                                                                                          |
| `--min-size BYTES`    | 过滤小于指定字节的电子书；不带数字默认 1000，`0` 关闭，不传则关闭大小过滤                                                                                                                                        |
| `--output-dir DIR`    | CBZ 输出到指定目录（自动创建），默认保留相对输入的子目录结构（如 `One Piece/001.mobi` → `DIR/One Piece/001.cbz`）；加 `--flatten` 可平铺到目录根下                                                                        |
| `--flatten`           | 仅与 `--output-dir` 联用：所有 CBZ 平铺到输出目录根下，同名文件未指定 `--overwrite` 时跳过（SKIP），指定时覆盖首选名；单独使用（无 `--output-dir`）将报错退出                                                                       |
| `--progress`          | 强制显示文件级进度条（默认 TTY 且文件数≥2 时自动显示；与 `--no-progress` 同传时以最后出现的参数为准；`--quiet` 下默认保留；进度条写 stderr，不进 `--log` 日志）                                                                        |
| `--no-progress`       | 强制关闭进度条（即使 TTY 且文件数≥2）                                                                                                                                                           |
| `--dry-run`           | 试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录                                                                                                                                                 |
| `--quiet`             | 静默模式，只显示错误与最终汇总                                                                                                                                                                  |
| `--short-summary`     | 精简汇总：成功/跳过文件只显示数量不列出路径（失败文件始终全路径列出）                                                                                                                                              |
| `--compress LEVEL`    | zip 压缩级别 0-9：`0`=不压缩（默认，图片本身已压缩），`1-9`=deflate 压缩（PNG 源有收益，级别越高越小但越慢）                                                                                                            |
| `--inspect`           | 检查模式：位置参数为单个文件时直接检查该文件，为目录时随机抽查 1 个，只解包读取内部信息（元数据/结构/图片/分辨率/DRM 双重判断/NCX 目录），不生成 CBZ，结束自动清理临时目录                                                                                  |
| `--inspect-all`       | 检查全部电子书（需配合 `--inspect` 使用，单独使用将自动启用 `--inspect`）                                                                                                                                |
| `--no-comicinfo`      | 不生成 ComicInfo.xml（默认生成：向 CBZ 根目录写入 Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary 漫画元数据）                                                |
| `--setinfo FIELD=VALUE` | 覆盖/新增 ComicInfo 字段（可多次指定，优先级最高）：`FIELD` 为 ComicInfo 字段名（需在 ComicInfo 标准字段白名单内，白名单外 warning 忽略），`VALUE` 支持固定值 / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN` 占位符（对应值缺失时该字段不写入）；智能拆分：仅当逗号后紧跟"字段名="时才拆分，否则逗号视为值的一部分（如 `Summary=hello, world` 不拆分）；值内含 `Key=` 结构请用多次 `--setinfo` 传入；开启 `--setinfo` 时输入目录中混有的已有 `.cbz` 会就地修改其 ComicInfo.xml（未指定字段保留原值），其余文件照常转换 |
| `--unpack`            | 解包查看：只解压不转换，输出到各源文件所在目录的同名子目录（已存在自动加序号避让）；mobi 走 extract 保留完整结构，cbz 走 extractall（含 zip-slip 路径穿越防护）；`--unpack` / `--setinfo` 时也会收集 `.cbz` 输入 |
| `--double-page VALUE` | 双页检测：不传或 `auto` 开启（阈值 2.0，检测宽/高 ≥ 阈值的横幅跨页大图，ComicInfo 写入 `<Manga>Yes</Manga>` + 逐页 `Type="DoublePage"`）；传数值（如 `2.5`）开启并调整阈值；`off` / `no` / `0` 关闭；非法值报错 |
| `--log FILE`          | 将全部输出追加写入指定日志文件；不带文件名时自动生成 `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（当前目录）                                                                                                  |
| `--json`              | stdout 输出单行紧凑 JSON（供 AI / 管道 / 脚本读取），开启时屏蔽人类可读文本输出（进度条 / emit 提示 / 汇总）；仅转换/修改模式输出（dry-run/inspect/unpack 不输出）；进度条写 stderr 不混流，但 `2>&1` 合并重定向会混入进度条 |
| `--json-out FILE`     | 将结构化结果写入 JSON 文件（缩进格式）；不带文件名时自动生成时间戳文件（当前目录），带文件名写入指定路径，行为对齐 `--log`；与 `--json` 可共存；同 `--json` 仅转换/修改模式写入                                                                                  |
| `--version`           | 显示版本号                                                                                                                                                                            |

## 输出

- 默认转换后的 `.cbz` 文件与原电子书文件在同一目录；指定 `--output-dir` 时输出到该目录（自动创建），默认保留相对输入的子目录结构，加 `--flatten` 可平铺到输出目录根下（同名文件未指定 `--overwrite` 时跳过）
- 已存在的 `.cbz` 默认自动跳过，不会覆盖；加 `--overwrite` 可强制重新生成
- 0 字节 / 文件头损坏的电子书在预处理阶段直接跳过，日志输出完整路径与原因
- 每个文件转换耗时实时输出，汇总底部显示总耗时
- 转换失败的文件会打印错误信息，不影响其他文件继续转换

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
A: v1.9.0 起 `--output-dir` 默认保留相对输入的子目录结构（旧版一律平铺，属破坏性变更）。需要平铺时加 `--flatten`，旧命令 `python manga-mobi2cbz.py Manga --output-dir CBZ` 改为 `python manga-mobi2cbz.py Manga --output-dir CBZ --flatten` 即可恢复旧行为。

**Q: 支持 .azw / .azw3 吗？**
A: 支持。v1.8.0 起输入扩展名扩展为 `.mobi` / `.azw` / `.azw3`，三种格式统一走同一转换链路；同目录同名不同扩展名时默认保留 azw3，可用 `--ext-priority` 调整。

**Q: 支持 EPUB 吗？**
A: 支持。v2.4.0 起输入扩展名扩展为 `.mobi` / `.azw` / `.azw3` / `.epub`。EPUB 本质为 ZIP 容器，直接走 zipfile 安全解包并复用 OPF spine 提取链路；封面自动识别支持 EPUB2（`<meta name="cover">`）与 EPUB3（`properties="cover-image"`）两种约定；无 EXTH 头时元数据从 OPF `dc:` 字段读取；`--prefer` 对 EPUB 静默忽略。

## 更新日志

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
- **`--setinfo FIELD=VALUE`** — 覆盖/新增 ComicInfo 字段（可多次指定，优先级最高）；VALUE 支持固定值 / `%series` / `%number` / `%title` / `%filename` / `%leftN` / `%rightN`；智能拆分（逗号后紧跟字段名=才拆）；CBZ 修改模式直接重写 zip；`--inspect` 预览块同步应用
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
- 修复 `infer_series_number` 点号失效：改用 `path.name` 手动去扩展名，`One Piece Vol.01` 等点号卷号可正确推断
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

- `--output-dir DIR` 由「一律平铺到 DIR」改为「**默认保留相对输入的子目录结构**」（如 `One Piece/001.mobi` → `DIR/One Piece/001.cbz`）
- 迁移方式：旧命令 `python manga-mobi2cbz.py Manga --output-dir CBZ` 需改为 `python manga-mobi2cbz.py Manga --output-dir CBZ --flatten` 才能恢复「平铺」行为

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
- 目录对齐兜底：目录图片数与收集数不一致时，多出的图片默认按自然排序追加到 cbz 末尾；`--drop-extra` 可改为放弃，处理结果会打印输出

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

[MIT](./LICENSE)
