**Languages:** [中文](README.md) | [English](README_en.md) | [日本語](README_ja.md)

# manga-mobi2cbz

一款专为Kindle漫画打造的批量转换CLI工具，一键将无DRM MOBI / AZW / AZW3 / EPUB 电子书导出标准CBZ漫画包。
原生遵循OPF Spine官方阅读顺序提取图片，内置封面自动修复、同卷多格式去重、批量超时防护、文件完整性校验、多语言自动输出等全套实用能力；附带 `--inspect` 探查模式，无需打包即可查看漫画元数据、分辨率、NCX目录与DRM状态，全平台通用，批量整理漫画库高效稳定。

> ⚠️ 仅支持已去除 DRM 的 Kindle 漫画，商店加密电子书无法解析。
> 
> **项目由来**：为处理漫画格式，每次转换都让AI生成脚本处理，为便于复用和避免脚本丢失，便上传到了GitHub。
> 后续使用中陆续遇到顺序错乱、封面丢失、批量中断等问题，经反复迭代，逐步演变为现在的形态。代码完全由AI生成，欢迎使用，若发现问题，也欢迎反馈。

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
- **输出重命名** — `--rename[=TEMPLATE]` 重命名输出的 CBZ 文件名（默认关闭）：无值 = 默认模板（系列名 + 自动标记前缀，前缀按类型自动选 `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`，连话 `話005-006` 标 `[Ch.5-6]`）；模板支持 `%series` / `%number` / `%volume` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 及 `%03number` 补零占位符；来源优先级：文件名推断 > 文件自带元数据（OPF / ComicInfo.xml）兜底，`--setinfo` 不参与；输入为已有 `.cbz` 时进入独立重命名模式（只改名不转换，可与其他模式叠加）；`%description` 不建议用于文件名（内容可能过长），可配合 `%subN_M` 截取片段；建议配合 `--dry-run` 先预览
- **颜色控制** — `--no-color` 禁用 ANSI 颜色输出（即使终端支持也不上色）；日志 / JSON / 管道输出本就不含颜色
- **撞名分类提示** — `--rename` 跳过时区分两类提示：目标文件已存在（建议加 `--overwrite`）与本批内部撞名（建议调整命名模板），dry-run 与非 dry-run 分支均生效，JSON `reason` 字段分别记为 `existing` / `conflict`；dry-run 预览中 `[将跳过]` 按类别着色（磁盘同名=黄、本批撞名=品红），实际执行汇总将跳过数分组统计（磁盘同名 / 本批撞名）
- **断点续跑** — 目标 CBZ 已存在且完整性校验有效时直接跳过（SKIP）；源文件比 CBZ 更新时自动重新转换；损坏/无效自动重新转换；`--overwrite` 无条件覆盖
- **失败分类** — 转换失败按原因分类统计（timeout / drm / corrupt / no_images / comicinfo / verify / other），汇总输出各类失败数量
- **检查模式支持 CBZ** — `--inspect` 可直接检查 `.cbz` 文件（纯 zipfile 读取不解压）；封面行加分辨率+大小、格式统计加总文件数、Spine 前 5 列表每行加宽高
- **只读图片清单** — `--list-images [FILTER]` 列出目标电子书内全部图片（序号 / 文件名 / 分辨率 / 大小 / 模式·色深 / 方向 / 目录 / 标记）+ 全量统计区块（格式 / 模式·色深 / 尺寸分布 / 双页横幅 / 动图 / 小图 / 异常明细），不转换、不写 CBZ、不生成 ComicInfo；FILTER 可选，支持条件表达式（格式 / `res` / `size` / 方向 / 模式 / 位深 / 标记，逗号 = OR、`+` = AND、`-` 前缀 = 排除）；EXIF Orientation≠1 的图片带 `[旋转N]` 标记（N=2~8，正常=1 不标）并计入 `[异常]` 汇总；方向筛选词无值=选出全部方向异常图（rotate=auto 将旋转）、带值精确匹配 EXIF Orientation（如 `方向=6`）；`--json-out` 带 `orientation` 字段（v3.6.0）
- **文件名通配筛选** — `name=` 匹配文件名时，值含 `*` / `?` 按 glob 通配处理（不区分大小写，仅 `*` 与 `?` 特殊，`[]` 按字面处理），否则保持子串包含匹配；`--list-images` / `--drop` / `--pages` 三个入口全部生效，如 `name=*_封面*`、`name=p00?`
- **图像处理管线** — `--img-edit` 对输出图片做旋转 / 镜像翻转 / 灰度化 / 格式转换 / 重编码质量控制 / 缩放 / 白边裁剪 / 剥离 EXIF 处理（可多次指定，值内 `+` 切分摊平）：`rotate[=auto|90|180|270]` 按 EXIF Orientation 烧录像素、删除方向字段后重编码（无参=auto，仅处理 Orientation≠1 的图），`flip=x|y|both` 镜像翻转（x=水平、y=垂直、both=两者），`grayscale` 灰度化（恒插在 flip 之后，输出 RGB 三通道等值），`format=jpeg|png|webp`（别名 jpg；目标格式，重编码后 cbz 内条目后缀同步改；透明转 JPEG 默认补白，可 `format=jpeg,black` 或 `#RRGGBB` 改色；JPEG/WebP 走 quality 保存、PNG 无损），`quality=1-100` 覆盖重编码质量（默认 95，越界报错），`scale=NNN%` 百分比相对缩放（保持页间比例，如 200%=放大 2 倍，1~1000）或 `scale=NNNw` 统一目标宽度像素（高度按原始比例，如 1200w，1~100000，两种语法二选一），`trim[=容差]` 自动白边裁剪（无参/auto=0.05，检测边缘统一背景色、带安全边界避免误切），`strip` 清空图片全部 EXIF 元数据；固定管线顺序 `rotate→flip→grayscale→format→quality→scale→trim→strip` 与书写顺序无关；三入口全开：mobi→cbz 转换输出前 / `--repack` 打包前 / 目标为已有 `.cbz` 时就地修正（CBZ 方向修正模式）；联动 `--dry-run` / `--json` / `--json-out` / `--log`
- **双页检测** — `--double-page` 识别跨页横幅（宽/高 ≥ 阈值，默认 2.0），开启时逐页写入 DoublePage 标记（不写 Manga 声明）；不带值 / `auto` 开启，可传数值调阈值，`off` / `no` / `0` 关闭
- **丢弃小图** — `--drop small[=比例]` 剔除面积明显偏小的图片（宽×高 < 面积中位数×比例，默认 0.5），丢弃后 PageCount 按实际图片数重算；不带值 / `auto` = 0.5，可传 0~1 数值调比例，`off` / `no` / `0` 关闭；旧 `--drop-small` 为隐藏别名（等价 `--drop small`）仍可用
- **ComicInfo 字段覆盖** — `--setinfo FIELD=VALUE` 覆盖/新增 ComicInfo 字段（优先级最高），VALUE 支持固定值 / `%series` / `%number` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 占位符，可多次指定；字段名需在 ComicInfo 标准字段白名单内，白名单外字段 warning 忽略；已有 CBZ 场景下 `%series`/`%number`/`%volume` 优先读取 ComicInfo 内显式 Series/Number/Volume，缺失才回退文件名推断；输入为已有 CBZ 时直接修改其 ComicInfo.xml（未指定字段保留原值）
- **日志自动命名** — `--log` 不带文件名时自动生成 `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（当前目录）
- **解包查看** — `--unpack` 只解压不转换，输出到各源文件所在目录的「源名_扩展名」子目录（如 vol.cbz → vol_cbz/，与源文件不撞名；已存在自动加序号避让），mobi 保留完整结构、cbz 直接解包（含 zip-slip 路径穿越防护）；`--unpack` / `--setinfo` 时也会收集 `.cbz` 输入
- **耗时统计** — 每个文件转换耗时实时输出，汇总底部显示总耗时
- **JSON 结构化输出** — `--json` stdout 输出 JSON（转换/修改模式为整体单行紧凑 JSON，检查模式为每文件一行精简 JSON，供 AI / 管道 / 脚本读取，开启时屏蔽人类文本输出）；`--json-out [FILE]` 将结构化结果写入 JSON 文件（缩进格式，省略文件名自动生成时间戳文件，行为对齐 `--log`）；两者可共存，转换 / `--setinfo` 修改 / `--inspect` 检查模式均支持

## 支持的图片格式

转换时识别并打包以下格式的图片：`.jpg` / `.jpeg` / `.png` / `.gif` / `.webp` / `.bmp` / `.tiff` / `.tif`

## 环境要求

- Python 3.10+
- 运行时依赖：`mobi`（必需）
- 可选依赖：`pillow`（使用 `--img-edit` 图像管线时需要）、`tqdm`（进度条，缺失时自动降级为文本进度）

## 安装

```bash
pip install mobi          # 必需
pip install pillow tqdm   # 可选：--img-edit 图像管线 / 进度条（缺失时降级为文本进度）
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

### 就地修正方向（方向异常页按 EXIF 自动旋转，CBZ 就地修正模式）

```bash
python manga-mobi2cbz.py "D:\ComicsLibrary\Vol.01.cbz" --img-edit rotate
```

`--img-edit` 图像处理管线同样作用于 mobi→cbz 转换输出前与 `--repack` 打包前；rotate 无参（auto）按 EXIF Orientation 自动旋转方向异常的图（v3.6.0）。

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
| `--drop [EXPR]` | 统一丢弃入口（`nargs='?'`，可重复指定 = OR 并集）：无值 = `extra` 丢弃全部多余图片（默认追加到 cbz 末尾）；带值按条件丢弃——格式词 / 条件词（`res` / `size` / 方向 / 模式 / 位深 / 标记：`double` / `thumbnail` / `animated` / `cover` 等，方向类 `landscape`/`portrait`/`square` 横向/纵向/方形）/ `small[=比例]` 小图；多条件逗号 = OR、`+` = AND、`-` 前缀 = 排除，如 `--drop gif,extra`、`--drop small=0.4`、`--drop 封面+超大页`；`off` / `no` / `0` 关闭；执行顺序：多余图丢弃 → 去重 → 条件过滤 → 小图丢弃；处理结果逐条列出被丢弃图片文件名，`--short-summary` 下只显示数量；旧 `--drop-extra` / `--drop-small` 并入本参数（隐藏别名仍可用） |
| `--overwrite` | 目标 cbz 已存在时强制重新生成（默认跳过） |
| `--ext-priority EXTS` | 同目录同名（仅扩展名不同）时保留哪种格式：逗号分隔、顺序即优先级从高到低，仅接受 mobi/azw/azw3/epub，默认 azw3；优先级未覆盖时回退兜底顺序 azw3→epub→mobi→azw；与 `--prefer`（双目录选择）无关 |
| `--timeout` | 单文件转换超时秒数，超时自动跳过并计入失败（默认 600，`0` 表示不限制） |
| `--min-size BYTES` | 过滤小于指定字节的电子书；不带数字默认 1000，`0` 关闭，不传则关闭大小过滤 |
| `--output-dir DIR` | CBZ 输出到指定目录（自动创建），默认保留相对输入的子目录结构（如 `Sample Series/001.mobi` → `DIR/Sample Series/001.cbz`）；加 `--flatten` 可平铺到目录根下 |
| `--flatten` | 仅与 `--output-dir` 联用：所有 CBZ 平铺到输出目录根下，同名文件未指定 `--overwrite` 时跳过（SKIP），指定时覆盖首选名；单独使用（无 `--output-dir`）将报错退出 |
| `--progress` | 进度条显示策略：`auto` 在 TTY 且文件数≥2 且未用 `--json`/`--json-out` 时显示；`on` 强制显示；`off` 强制关闭（默认 `off` 不显示）；进度条写 stderr，不进 `--log` 日志 |
| `--no-progress` | 强制关闭进度条（等价 `--progress off`，兼容旧命令） |
| `--dry-run` | 试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录 |
| `--rename[=TEMPLATE]` | 重命名输出 CBZ 文件名（可选模板，默认关闭）：无值 = 默认模板（系列名 + 自动标记前缀，前缀按类型自动选 `[Vol.x]` / `[Ch.x]` / `[Vol.x][Ch.x]` / `[x]`，连话 `話005-006` 标 `[Ch.5-6]`）；模板支持 `%series` / `%number` / `%volume` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 及 `%03number` 补零占位符；来源优先级：文件名推断 > 文件自带元数据（OPF / ComicInfo.xml）兜底，`--setinfo` 不参与；输入为已有 `.cbz` 时进入独立重命名模式（只改名不转换，可与其他模式叠加）；跳过时区分两类提示（磁盘同名建议 `--overwrite` / 本批撞名建议调模板），JSON `reason` 分别记 `existing` / `conflict`；dry-run 预览中 `[将跳过]` 按撞名类别着色（磁盘同名=黄、本批撞名=品红，仅 TTY 且未 `--no-color` 时生效），实际执行汇总将跳过数拆分为「磁盘同名 N / 本批撞名 M」并分组列出；`%description` 不建议用于文件名（内容可能过长），可配合 `%subN_M` 截取片段；建议配合 `--dry-run` 先预览 |
| `--no-color` | 禁用 ANSI 颜色输出（即使终端支持也不上色）；日志 / JSON / 管道输出本就不含颜色 |
| `--quiet` | 静默模式，只显示错误与最终汇总 |
| `--debug` | 调试模式：向 stderr 输出 debug 级日志（默认静默，仅指定时输出；与 `--quiet` 同给时 debug 仍输出） |
| `--short-summary` | 精简汇总：成功/跳过文件只显示数量不列出路径（失败文件始终全路径列出） |
| `--compress LEVEL` | zip 压缩级别 0-9：`0`=不压缩（默认，图片本身已压缩），`1-9`=deflate 压缩（PNG 源有收益，级别越高越小但越慢） |
| `--inspect [MODE][,FILTER]` | 检查模式：`sample` 随机抽查 1 个（默认），`all` 全量检查；可附过滤器（如 `all,small=0.6`），命中条件的图片输出数量 + 文件名清单（含尺寸）；位置参数为单个文件时直接检查该文件，只解包读取内部信息（元数据/结构/图片/分辨率/DRM 双重判断/NCX 目录），不生成 CBZ，结束自动清理临时目录；图片预览仅列前 5 张，图数 > 5 时末尾追加省略号行（英文 `...`，如 `...（共 N 张）`）；目录(NCX) / nav 预览截断统一为英文 `...`；书级摘要新增「方向异常 N 张（rotate=auto 将旋转）」输出行，`--json-out` 带出 `rotate_count` 字段，过滤支持方向筛选词（如 `all,方向`）（v3.6.0） |
| `--inspect-all` | 检查全部电子书（等价 `--inspect all`，兼容旧命令） |
| `--no-comicinfo` | 不生成 ComicInfo.xml（默认生成：向 CBZ 根目录写入 Title / Series / Number / Writer / Publisher / Year / LanguageISO / PageCount / Summary 漫画元数据） |
| `--setinfo FIELD=VALUE` | 覆盖/新增 ComicInfo 字段（可多次指定，优先级最高）：`FIELD` 为 ComicInfo 字段名（需在 ComicInfo 标准字段白名单内——39 个简单字段，复杂的 `Pages` 除外——白名单外 warning 忽略），`VALUE` 支持固定值 / `%series` / `%number` / `%title` / `%writer` / `%publisher` / `%date` / `%language` / `%description` / `%filename` / `%leftN` / `%rightN` / `%subN_M` 占位符（`%subN_M`=第 N 字符起 M 个，1-based；整段恰为单个已知占位符且对应值缺失时该字段不写入）；占位符可与固定文本混用（如 `%writer·重制`、`第%number话`），混用时缺失值渲染为空串；智能拆分：仅当逗号后紧跟"字段名="时才拆分，否则逗号视为值的一部分（如 `Summary=Vol. 1, First Edition` 不拆分）；值内含 `Key=` 结构请用多次 `--setinfo` 传入；`Manga` 默认不写入，需显式 `--setinfo Manga=Unknown\\|No\\|Yes\\|YesAndRightToLeft`（限官方 v2.0 枚举）；另支持 `CommunityRating`（0-5）/ `MainCharacterOrTeam` / `Review` 三个官方字段；已有 CBZ 场景下 `%series`/`%number`/`%volume` 优先读取 ComicInfo 内显式 Series/Number/Volume，缺失才回退文件名推断；开启 `--setinfo` 时输入目录中混有的已有 `.cbz` 会就地修改其 ComicInfo.xml（未指定字段保留原值），其余文件照常转换 |
| `--unpack` | 解包查看：只解压不转换，输出到各源文件所在目录的「源名_扩展名」子目录（如 vol.cbz → vol_cbz/，与源文件不撞名；已存在自动加序号避让；`--output-dir DIR` 可指定解包输出目录，未指定时默认各源文件所在目录，v3.6.0）；mobi 走 extract 保留完整结构，cbz 走 extractall（含 zip-slip 路径穿越防护）；`--unpack` / `--setinfo` 时也会收集 `.cbz` 输入 |
| `--repack` | 重新打包模式：把已解包的 `_cbz` 解包目录（目录名以 `_cbz` 结尾，如 `vol_cbz/`）重新打包回 CBZ，输出名还原为源文件名（`vol_cbz` → `vol.cbz`）；支持单个目录或父目录批量，执行前先打印待处理清单（每行标注 `解包目录名 → 输出.cbz`）；目录内 ComicInfo.xml 有则原样带回、无则生成基础版，可 `--setinfo` 叠加覆盖、`--no-comicinfo` 关闭；已存在默认跳过、`--overwrite` 覆盖；`--rename` 不适用于本模式 |
| `--double-page VALUE` | 双页检测：不传或 `auto` 开启（阈值 2.0，检测宽/高 ≥ 阈值的横幅跨页大图，ComicInfo 写入逐页 `Type="DoublePage"`，`Manga` 不再自动声明）；传数值（如 `2.5`）开启并调整阈值；`off` / `no` / `0` 关闭；非法值报错 |
| `--drop small[=比例]` | 丢弃小图：转换时剔除面积明显偏小的图片（宽×高 < 面积中位数×比例 判为小图，如封面缩略图 / 版权页）；`small` 无参 / `auto` 用默认比例 0.5，可传 `0~1` 数值（如 `--drop small=0.4`）调比例；`off` / `no` / `0` 关闭（默认关闭，不改变现有行为）；丢弃后 ComicInfo `PageCount` 按实际剩余图数重算，汇总 / `--log` / `--json` 新增"丢弃小图"计数（`--json` 输出 `dropped_small` 字段）并逐条列出被丢弃文件名（`--short-summary` 下只显示数量）；`--inspect` 预览会提示"开启 --drop small 时将丢弃 N 张"；横幅双页（宽不小）不会被误删；仅转换模式生效；旧 `--drop-small` 等价 `--drop small`（隐藏别名仍可用） |
| `--img-edit [EDIT]` | 图像处理管线（可多次指定，值内 `+` 切分摊平）：`rotate[=auto\|90\|180\|270]` 按 EXIF Orientation 烧录像素后重编码（无参=auto，仅处理 Orientation≠1 的图）、`flip=x\|y\|both` 镜像翻转、`grayscale` 灰度化（固定紧随 flip 后）、`format=jpeg\|png\|webp` 格式转换（透明转 JPEG 默认补白，可 `format=jpeg,black` 或 `#RRGGBB` 改色）、`quality=1-100` 重编码质量（默认 95）、`scale=NNN%` 或 `scale=NNNw` 缩放、`trim[=容差]` 白边裁剪（无参/auto=0.05）、`strip` 剥离 EXIF；固定顺序 `rotate→flip→grayscale→format→quality→scale→trim→strip` 与书写顺序无关；三入口：mobi→cbz 转换输出前 / `--repack` 打包前 / 已有 `.cbz` 就地修正；联动 `--dry-run` / `--json` / `--json-out` / `--log` |
| `--pages PAGES` | 指定页处理（可多次指定，值内逗号切分免引号）：只处理指定页码的图片，页码从 1 起（第 1 页 = 卷内第 1 张图）。支持单页 `5`｜闭区间 `1-3`｜开区间 `7-*`（*=最后 1 页），可逗号混用（如 `1-3,5,7-*`）；越界页码忽略并逐页提示；全部越界/空命中报错退出；与 `--img-edit` 组合仅选中页走管线、与 `--drop` 按 AND 共存（先锁页再过滤）、与 `--unpack` / `--repack` 只解/打包选中页（v3.6.0）；页面也可按筛选词选择——`name=` 的值含 `*` / `?` 时按 glob 匹配文件名（如 `name=*_封面*`、`name=p00?`），其余筛选词与 `--drop` 共用词表 |
| `--list-images [FILTER]` | 只读图片清单（`nargs='?'`）：列出目标电子书内全部图片（序号 / 文件名 / 分辨率 / 大小 / 模式·色深 / 方向 / 目录 / 标记）+ 全量统计区块（格式 / 模式·色深 / 尺寸分布 / 双页横幅 / 动图 / 小图 / 异常明细），不转换、不写 CBZ、不生成 ComicInfo、不落盘；与 `--inspect` 完全独立。无值 = 全部列出；带值 = FILTER 筛选表达式（与 `--drop` 同源引擎：格式 / `extra`（不在 spine 的多余图）/ `res` / `size` / 方向 / 模式 / 位深 / 标记 / `small[=比例]` 条件词，另支持方向类 `landscape`/`portrait`/`square`（横向/纵向/方形），逗号 = OR、`+` = AND，`-` 前缀排除，如 `jpeg,size>1MB`、`-webp`），筛选只影响清单行，统计恒全量。EXIF Orientation≠1 的图片带 `[旋转N]` 标记（N=2~8，正常=1 不标）并计入 `[异常]` 汇总，新增方向筛选词（同义词 `orient`/`orientation`/`direction`/`方向`/`方向异常`）：无值=选出全部方向异常图（rotate=auto 将旋转）、带值精确匹配 EXIF Orientation（如 `方向=6`）；`--json-out` 图片记录新增 `orientation` 字段（v3.6.0）。CBZ 直读 zip 不落盘（无目录列 / 无转换态标记）；配 `--json` 每文件一行精简 JSON，配 `--quiet` 抑制明细只剩计数 |
| `--log FILE` | 将全部输出追加写入指定日志文件；不带文件名时自动生成 `manga-mobi2cbz_YYYYMMDD_HHMMSS.log`（当前目录） |
| `--json` | stdout 输出 JSON（供 AI / 管道 / 脚本读取），开启时屏蔽人类可读文本输出（进度条 / emit 提示 / 汇总）；转换/修改模式为整体单行紧凑 JSON，检查（`--inspect`）模式为每文件一行精简 JSON（status/series/number/source/page_count/drm，status 取值 ok/drm/invalid/noimg/timeout/fail）；试运行（`--dry-run`）输出带 `dry_run` 标记的 JSON（status 取值 will_skip/pending），unpack 模式不输出；进度条写 stderr 不混流，但 `2>&1` 合并重定向会混入进度条 |
| `--json-out FILE` | 将结构化结果写入 JSON 文件（缩进格式）；不带文件名时自动生成时间戳文件（当前目录），带文件名写入指定路径，行为对齐 `--log`；与 `--json` 可共存；转换/修改模式写入文件级结果，检查（`--inspect`）模式写入全量（含 spine/toc 与 summary） |
| `--version` | 显示版本号 |

## 参数与模式生效矩阵

部分参数并非在所有模式下生效，未生效的会静默忽略（不报错也不警告），使用时以本矩阵为准：

| 参数  | mobi→cbz 转换 | `--unpack` 解包 | `--list-images` 清单 | `--repack` 重打包 | CBZ 就地修正 |
| --- | --- | --- | --- | --- | --- |
| `--img-edit` | ✅ 转换输出前应用管线 | ⏭ 忽略 | ⏭ 忽略 | ✅ 打包写图前应用管线 | ✅ 就地重编码 |
| `--drop` | ✅ 剔除小图/过滤 | ⏭ 忽略 | ⏭ 忽略（可用 FILTER 筛选词做只读过滤，不影响文件） | ⏭ 忽略 | ⏭ 忽略 |
| `--pages` | ✅ 仅处理选中页 | ✅ 只保留选中页图片 | ⏭ 忽略 | ✅ 只打包选中页 | ✅ 仅选中页走管线 |
| `--double-page` | ✅ 写入 DoublePage 标记 | ⏭ 忽略 | ⏭ 忽略（统计口径仍按宽高比展示） | ✅ ComicInfo 回带时保留原标记 | ⏭ 忽略 |
| `--rename` | ✅ 输出改名 | ⏭ 忽略 | ⏭ 忽略 | ⏭ 不适用 | ✅ 就地改名 |
| `--setinfo` | ✅ ComicInfo 覆盖 | ⏭ 忽略 | ⏭ 忽略 | ✅ 覆盖/生成 ComicInfo | ✅ 就地修改 ComicInfo |
| `--no-comicinfo` | ✅ 不生成 | ⏭ 忽略 | ⏭ 忽略 | ✅ 不带回 ComicInfo | ⏭ 忽略 |
| `--delete` | ✅ 成功后删源 | ⏭ 忽略 | ⏭ 忽略 | ⏭ 不适用 | ⏭ 不适用（就地修正天然无源文件） |

> 注：`--double-page` / `--rename` / `--setinfo` / `--no-comicinfo` / `--delete` 各行按代码实际行为整理；`--unpack` 对已有 `.cbz` / `.epub` 输入同样生效（纯 zip 解包），`--pages` 在解包后按自然排序编号只保留选中页图片。

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

更新日志见 [CHANGELOG.md](CHANGELOG.md)。

## License

本项目使用 [GPL-3.0](./LICENSE) 许可。

### 第三方依赖许可

本工具运行时依赖 mobi 库（v0.4.1，Titusz Pan 维护版），其许可证为 GPL-3.0-only，公开分发请遵守 GPL-3.0 相关要求。