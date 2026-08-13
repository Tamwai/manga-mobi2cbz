manga-mobi2cbz

将 Mobi 格式的漫画批量转换为 CBZ 格式，专为漫画阅读优化。

## 功能特点

- **批量转换** — 支持单个文件或整个目录递归转换
- **OPF spine 排序** — 优先按 OPF spine 顺序提取图片，保证真实阅读顺序；无 OPF 时兜底按文件名自然排序
- **封面兜底** — 自动扫描文件名含 cover/front 的图片；封面已在 spine 列表中则以列表顺序为准，仅缺失时插入首位补齐
- **目录对齐兜底** — 目录图片数与收集数不一致时，多出的图片默认按自然排序追加到 cbz 末尾；`--drop-extra` 可改为放弃，处理结果会打印输出
- **双目录去重** — 自动识别 mobi7/mobi8 双目录，默认保留 mobi8（画质可能更好），可切换
- **自然排序** — 按页码自然排序，避免 `10.jpg` 排在 `2.jpg` 前面
- **完整性校验** — 转换后自动校验 CBZ 文件，损坏则删除并提示
- **无压缩打包** — 图片已是压缩格式，ZIP 仅存储不压缩，速度快、体积小
- **可选删除原文件** — `--delete` 参数转换成功后自动删除原始 mobi
- **强制覆盖** — `--overwrite` 参数对已存在的 cbz 强制重新生成，更新漫画后无需手动删旧文件
- **静默模式** — `--quiet` 批量转换只显示错误与汇总，不再刷屏；`--log FILE` 可将全部输出追加写入日志文件
- **DRM 加密识别** — 遇到 DRM 加密的 Kindle 漫画时明确提示无法解密，避免静默失败

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

### 批量转换整个目录（递归搜索所有 .mobi）

```bash
python manga-mobi2cbz.py "D:\Manga"
```

### 转换成功后删除原始 mobi

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

### 静默模式 + 输出写入日志

```bash
python manga-mobi2cbz.py "D:\Manga" --quiet --log convert.log
```

### 查看版本号

```bash
python manga-mobi2cbz.py --version
```

## 参数说明

| 参数  | 说明  |
| --- | --- |
| `target` | mobi 文件路径或包含 mobi 的目录（必填） |
| `--delete` | 转换成功后删除原始 mobi 文件（默认不删除） |
| `--prefer` | 双目录 mobi 时保留哪份：`mobi7` 或 `mobi8`（默认 `mobi8`） |
| `--drop-extra` | 目录中有未被收集的多余图片时放弃追加（默认追加到 cbz 末尾） |
| `--overwrite` | 目标 cbz 已存在时强制重新生成（默认跳过） |
| `--quiet` | 静默模式，只显示错误与最终汇总 |
| `--log FILE` | 将全部输出追加写入指定日志文件 |
| `--version` | 显示版本号 |

## 输出

- 转换后的 `.cbz` 文件与原 `.mobi` 文件在同一目录
- 已存在的 `.cbz` 默认自动跳过，不会覆盖；加 `--overwrite` 可强制重新生成
- 转换失败的文件会打印错误信息，不影响其他文件继续转换

## 已知限制

- **DRM 加密的 mobi 不兼容** — 底层 mobi 库无法解密 Kindle 商店购买的 DRM 加密漫画，此类文件会明确提示"可能为 DRM 加密"并跳过，不会静默产生空 cbz。请先去除 DRM 后再转换
- **不生成 ComicInfo.xml** — 脚本只负责打包图片，转换产物不含 ComicInfo.xml 元数据（系列、作者、标签等）；如需元数据请另行注入
- **不支持 `.azw` / `.azw3`** — 目前仅支持 `.mobi` 格式

## 常见问题

**Q: 转换后 CBZ 里的图片顺序乱了？**
A: 优先按 OPF spine 顺序（EPUB 标准阅读顺序）提取图片，绝大多数情况下顺序正确；若源文件无 OPF 或 spine 提取为空，会兜底按文件名自然排序。如果仍有问题，可能是原 mobi 内部图片命名不规范，请检查源文件。

**Q: 为什么 CBZ 里少了封面？**
A: 部分 mobi 的封面只由 OPF metadata 的 cover meta 指向、未被 spine 引用，按 spine 提取时会漏掉。脚本会自动扫描文件名含 cover/front 的图片，缺失时插入首位补齐；若封面已在 spine 列表中则保持原顺序。若封面文件名不含上述关键字，可能仍会遗漏，可改名后重转。

**Q: 为什么有些 mobi 转换后体积很小？**
A: 双目录 mobi（mobi7+mobi8）默认只保留 mobi8 一份，避免内容重复导致体积翻倍。如需保留 mobi7 请加 `--prefer mobi7`。

**Q: 支持 .azw / .azw3 吗？**
A: 目前仅支持 `.mobi` 格式。

## 更新日志

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

- 修复临时目录残留：`mobi.extract` 不支持 `output_dir` 参数，改为仅传输入文件并记录其生成的解压路径，finally 统一清理；外层以 `TemporaryDirectory` 兜底，正常 / Ctrl+C / 异常均不残留

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

[MIT
