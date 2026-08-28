# manga-mobi2cbz v3.5.0

发布日期：2026-08-28

## 概述

本版本在 v3.4.0 退出码语义基础上做细化与收尾：目标路径不存在、`--repack` 无可用目录等此前沿用旧码的场景补上明确语义并统一为 `2`，`--unpack` / `--inspect` 失败归为 `1`，转换中 Ctrl+C 退出 `130`（128+SIGINT），便于脚本化消费全链路判断；`--drop` / `--inspect` 过滤器新增 `-` 前缀排除（负向条件），与逗号 OR / 加号 AND 同一引擎统一解析。同时修正一批帮助文案自相矛盾与占位符误写。

## 新增

- **`-` 前缀排除** — `--drop` / `--inspect` 过滤器支持负向条件（如 `all,small=0.6,-gif`），逗号 OR / 加号 AND / `-` 前缀由同一表达式引擎统一解析
- **`--repack` 忽略 `--rename` 提示** — repack 模式输出名由解包目录名推断，`--rename` 被忽略时给出提示（不再静默）
- **`--repack` plan 标注推断输出名** — 处理清单每行标注 `解包目录名 → 输出.cbz`，推断来源一目了然

## 变更

- **退出码语义细化**：
  - 目标路径不存在 → `2`（原为 `1`，与参数用法错误同码，脚本化时更易识别为输入问题）
  - `--repack` 无可用解包目录 / 无 `_cbz` 目录 → `2`，且计入失败 1
  - `--unpack` 解包失败 → `1`
  - `--inspect` 异常 → `1`
  - 转换中 Ctrl+C → `130`（128+SIGINT，与常规 shell 约定一致）

## 修复

- `--drop-small` 无效值错误文案自相矛盾（同时提示的是「支持 auto/off/no/0」）→ 改为「支持 auto 或数值(0~1)」，与真实取值一致
- `--setinfo` 帮助与文件头示例中占位符 `%%` 误写 → 统一为单 `%`
- `--unpack` 目录撞名避让说明措辞 → 明确「默认 源名_扩展名，已存在时以 `(N)` 序号避让」
- `--inspect` 帮助补充 FILTER 语法说明（与 `--drop` 相同：逗号=OR、加号=AND、`-` 前缀排除）
- 四语 `help.setinfo` / `help.rename` 帮助文本占位符 `%%` 误写统一为单 `%`

## 维护

- 回归测试退出码预期同步更新（目标不存在 `1` → `2`）

## 安装

```bash
pip install mobi
# 或直接运行
python manga-mobi2cbz.py --help
```

## 许可

GPL-3.0-only（运行时依赖 mobi 库，同为 GPL-3.0-only）。

---

# manga-mobi2cbz v3.5.0 (English)

Release date: 2026-08-28

## Overview

This release refines and closes out the exit-code contract introduced in v3.4.0: scenarios that previously reused older codes now get explicit semantics and are normalized to `2` (missing target path, `--repack` with no usable directory), `--unpack` / `--inspect` failures map to `1`, and Ctrl+C during conversion exits `130` (128+SIGINT), giving scripts a full-chain verdict; `--drop` / `--inspect` filters gain `-` prefix exclusion (negative conditions), parsed by the same engine as comma OR / plus AND. A batch of contradictory help texts and placeholder typos are also fixed.

## New features

- **`-` prefix exclusion** — `--drop` / `--inspect` filters support negative conditions (e.g. `all,small=0.6,-gif`); comma OR / plus AND / `-` prefix are all parsed by the same expression engine
- **`--repack` ignores `--rename` with a hint** — in repack mode the output name is inferred from the unpack directory name; when `--rename` is ignored a hint is printed instead of silent ignoring
- **`--repack` plan annotates the inferred output name** — each line of the processing list shows `unpack dir → output.cbz`, making the inference source obvious

## Changes

- **Refined exit-code semantics**:
  - Target path does not exist → `2` (was `1`; same class as argument-usage errors, easier to recognize as an input problem in scripts)
  - `--repack` with no usable unpack directory / no `_cbz` directory → `2`, counted as 1 failure
  - `--unpack` extraction failure → `1`
  - `--inspect` exception → `1`
  - Ctrl+C during conversion → `130` (128+SIGINT, consistent with the usual shell convention)

## Fixes

- `--drop-small` invalid-value message was self-contradictory (also suggesting "off/no/0") → now "use auto or a number (0~1)", matching the actual accepted values
- `--setinfo` help and the file-header example used a double `%%` placeholder → unified to single `%`
- `--unpack` collision-avoidance wording → explicit "default 源名_扩展名, falls back to `(N)` suffix when the name is taken"
- `--inspect` help now documents FILTER syntax (same as `--drop`: comma=OR, plus=AND, `-` prefix excludes)
- `help.setinfo` / `help.rename` help texts in all four languages had a double `%%` placeholder typo → unified to single `%`

## Maintenance

- Regression-test exit-code expectation updated (missing target `1` → `2`)

## Installation

```bash
pip install mobi
# or run directly
python manga-mobi2cbz.py --help
```

## License

GPL-3.0-only (runtime dependency: mobi library, also GPL-3.0-only).
