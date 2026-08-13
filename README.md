# manga-mobi2cbz


将 Mobi 格式的漫画批量转换为 CBZ 格式，专为漫画阅读优化。

## 功能特点

- **批量转换** — 支持单个文件或整个目录递归转换
- **双目录去重** — 自动识别 mobi7/mobi8 双目录，默认保留 mobi8（画质更好），可切换
- **自然排序** — 按页码自然排序，避免 `10.jpg` 排在 `2.jpg` 前面
- **完整性校验** — 转换后自动校验 CBZ 文件，损坏则删除并提示
- **无压缩打包** — 图片已是压缩格式，ZIP 仅存储不压缩，速度快、体积小
- **可选删除原文件** — `--delete` 参数转换成功后自动删除原始 mobi

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
python mobi2cbz.py "D:\漫画\第一卷.mobi"
```

### 批量转换整个目录（递归搜索所有 .mobi）

```bash
python mobi2cbz.py "D:\漫画"
```

### 转换成功后删除原始 mobi

```bash
python mobi2cbz.py "D:\漫画" --delete
```

### 双目录 mobi 时保留 mobi7 版本

```bash
python mobi2cbz.py "D:\漫画\第一卷.mobi" --prefer mobi7
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `target` | mobi 文件路径或包含 mobi 的目录（必填） |
| `--delete` | 转换成功后删除原始 mobi 文件（默认不删除） |
| `--prefer mobi7\|mobi8` | 双目录 mobi 时保留哪份，默认 `mobi8` |

## 输出

- 转换后的 `.cbz` 文件与原 `.mobi` 文件在同一目录
- 已存在的 `.cbz` 会自动跳过，不会覆盖
- 转换失败的文件会打印错误信息，不影响其他文件继续转换

## 常见问题

**Q: 转换后 CBZ 里的图片顺序乱了？**
A: 已使用自然排序处理页码。如果仍有问题，可能是原 mobi 内部图片命名不规范，请检查源文件。

**Q: 为什么有些 mobi 转换后体积很小？**
A: 双目录 mobi（mobi7+mobi8）默认只保留 mobi8 一份，避免内容重复导致体积翻倍。如需保留 mobi7 请加 `--prefer mobi7`。

**Q: 支持 .azw / .azw3 吗？**
A: 目前仅支持 `.mobi` 格式。
