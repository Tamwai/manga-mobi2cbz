#!/usr/bin/env python3
"""
manga-mobi2cbz — 将 mobi 漫画文件批量转换为 cbz 格式

用法:
    python manga-mobi2cbz.py <目录或文件路径> [--delete] [--prefer mobi7|mobi8]

示例:
    # 转换整个文件夹（递归搜索所有 .mobi）
    python mobi2cbz.py "D:\\漫画\\"

    # 转换单个文件
    python mobi2cbz.py "D:\\漫画\\第一卷.mobi"

    # 转换后自动删除原始 mobi
    python mobi2cbz.py "D:\\漫画\\" --delete

    # 双目录 mobi 时保留 mobi7
    python mobi2cbz.py "D:\\漫画\\第一卷.mobi" --prefer mobi7

参数:
    --delete         转换成功后删除原始 mobi 文件
    --prefer         双目录 mobi（mobi7/mobi8）时保留哪份，默认 mobi8

依赖: pip install mobi
要求: Python 3.10+
"""

__version__ = "1.1.0"

SCRIPT_NAME = "manga-mobi2cbz"
import os
import re
import sys
import shutil
import zipfile
import argparse
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif"}
EOCD_SIGNATURE = b"\x50\x4b\x05\x06"  # End of Central Directory 签名


def natural_key(p: Path) -> list:
    """自然排序键：让 2.jpg 排在 10.jpg 前面"""
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r"(\d+)", p.name)]


def validate_cbz(cbz_path: Path) -> tuple[bool, str]:
    """校验 cbz 文件完整性：检查 EOCD 记录存在且所有条目可正常读取"""
    try:
        data = cbz_path.read_bytes()[-70000:]  # EOCD 在文件末尾，读尾部足够
        if EOCD_SIGNATURE not in data:
            return False, "缺少 EOCD 记录（文件不完整，可能被中断）"
        with zipfile.ZipFile(str(cbz_path)) as zf:
            bad = zf.testzip()
            if bad is not None:
                return False, f"条目损坏: {bad}"
            count = len(zf.namelist())
            return True, f"校验通过（{count} 个条目）"
    except zipfile.BadZipFile as e:
        return False, f"BadZipFile: {e}"
    except Exception as e:
        return False, f"校验异常: {e}"


def collect_mobi_files(target: Path) -> list[Path]:
    """收集所有待转换的 mobi 文件，按路径排序保证处理顺序可预测"""
    if target.is_file():
        if target.suffix.lower() == ".mobi":
            return [target]
        return []
    mobi_files = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.lower().endswith(".mobi"):
                mobi_files.append(Path(root) / f)
    return sorted(mobi_files)


def mobi_to_cbz(mobi_path: Path, delete_original: bool = False, prefer: str = "mobi8") -> Path | None:
    """将单个 mobi 文件转换为 cbz

    prefer: 双目录 mobi（mobi7/mobi8）时保留哪份，默认 "mobi8"
    """
    try:
        import mobi
    except ImportError:
        print("  [错误] 缺少依赖，请先运行: pip install mobi")
        sys.exit(1)

    cbz_path = mobi_path.with_suffix(".cbz")
    if cbz_path.exists():
        print(f"  [跳过] 目标已存在: {cbz_path.name}")
        return None

    tempdir = None
    try:
        # Step 1: 解压 mobi
        tempdir, _ = mobi.extract(str(mobi_path))

        # Step 2: 收集所有图片
        images = []
        for root, dirs, files in os.walk(tempdir):
            for f in files:
                ext = Path(f).suffix.lower()
                if ext in IMAGE_EXTENSIONS:
                    images.append(Path(root) / f)

        # 双目录 mobi（mobi7/mobi8）：默认保留 mobi8 一份，避免重复内容导致体积翻倍/重名冲突
        # 可通过 --prefer 参数改为保留 mobi7
        mobi7_images = [p for p in images if "mobi7" in p.parts]
        mobi8_images = [p for p in images if "mobi8" in p.parts]
        if mobi7_images and mobi8_images:
            if prefer == "mobi7":
                images = mobi7_images
                print(f"  [去重] 检测到双目录，按参数保留 mobi7 图片（{len(images)} 张）")
            else:
                images = mobi8_images
                print(f"  [去重] 检测到双目录，默认保留 mobi8 图片（{len(images)} 张）")
        elif mobi8_images:
            images = mobi8_images
            print(f"  [去重] 仅检测到 mobi8 目录，保留 mobi8 图片（{len(images)} 张）")
        elif mobi7_images:
            images = mobi7_images
            print(f"  [去重] 仅检测到 mobi7 目录，保留 mobi7 图片（{len(images)} 张）")

        if not images:
            print(f"  [失败] 未找到图片: {mobi_path.name}")
            return None

        # 自然排序，保证页码顺序正确（2.jpg 在 10.jpg 前面）
        images.sort(key=natural_key)

        # Step 3: 打包为 cbz (ZIP 无压缩，因为图片已经压缩过了)
        seen = {}
        with zipfile.ZipFile(str(cbz_path), "w", zipfile.ZIP_STORED) as zf:
            for img in images:
                if img.name in seen:
                    # 重名：以相对路径为条目名，保留两份
                    arcname = img.relative_to(tempdir).as_posix()
                else:
                    arcname = img.name
                    seen[img.name] = arcname
                zf.write(str(img), arcname)

        size_mb = cbz_path.stat().st_size / (1024 * 1024)
        print(f"  [完成] {cbz_path.name} ({len(images)} 张图片, {size_mb:.1f} MB)")

        # 完整性校验
        ok, msg = validate_cbz(cbz_path)
        if not ok:
            cbz_path.unlink(missing_ok=True)
            print(f"  [校验失败] {cbz_path.name}: {msg}，已删除坏文件")
            return None
        print(f"  [校验] {msg}")

        # Step 4: 可选删除原始 mobi
        if delete_original:
            mobi_path.unlink()
            print(f"  [清理] 已删除原始文件: {mobi_path.name}")

        return cbz_path

    except Exception as e:
        # 转换失败时清理半成品 cbz
        if cbz_path.exists():
            cbz_path.unlink(missing_ok=True)
        print(f"  [错误] {mobi_path.name}: {e}")
        return None
    finally:
        if tempdir and os.path.exists(tempdir):
            shutil.rmtree(tempdir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="mobi 漫画批量转 cbz")
    parser.add_argument(
        "--version", action="version", version=f"{SCRIPT_NAME} {__version__}"
    )
    parser.add_argument("target", help="mobi 文件路径或包含 mobi 的目录")
    parser.add_argument(
        "--delete", action="store_true", help="转换成功后删除原始 mobi 文件"
    )
    parser.add_argument(
        "--prefer",
        choices=["mobi7", "mobi8"],
        default="mobi8",
        help="双目录 mobi（mobi7/mobi8）时保留哪份，默认 mobi8",
    )
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"路径不存在: {args.target}")
        sys.exit(1)

    mobi_files = collect_mobi_files(target)
    if not mobi_files:
        print(f"未找到 .mobi 文件: {args.target}")
        sys.exit(0)

    print(f"找到 {len(mobi_files)} 个 mobi 文件，开始转换...\n")

    success = 0
    for mf in mobi_files:
        result = mobi_to_cbz(mf, delete_original=args.delete, prefer=args.prefer)
        if result:
            success += 1

    print(f"\n转换完成: {success}/{len(mobi_files)} 成功")


if __name__ == "__main__":
    main()
