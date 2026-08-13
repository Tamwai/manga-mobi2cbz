#!/usr/bin/env python3
"""
manga-mobi2cbz — 将 mobi 漫画文件批量转换为 cbz 格式（OPF spine 排序 + 封面兜底增强版）

用法:
    python manga-mobi2cbz.py <目录或文件路径> [--delete] [--prefer mobi7|mobi8] [--drop-extra] [--overwrite] [--timeout SECONDS] [--quiet] [--log FILE]

示例:
    # 转换整个文件夹（递归搜索所有 .mobi）
    python manga-mobi2cbz.py "D:\\Manga\\"

    # 转换单个文件
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi"

    # 转换后自动删除原始 mobi
    python manga-mobi2cbz.py "D:\\Manga" --delete

    # 双目录 mobi 时保留 mobi7
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi" --prefer mobi7

    # 目录中有未被收集的多余图片时放弃追加（默认追加到 cbz 末尾）
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi" --drop-extra

    # 已存在 cbz 时强制重新生成（覆盖旧文件）
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi" --overwrite

    # 单文件转换超过 300 秒自动跳过（防止损坏/加密 mobi 卡死批量任务）
    python manga-mobi2cbz.py "D:\\Manga" --timeout 300

    # 静默模式批量转换，只显示错误与汇总；完整输出写入日志文件
    python manga-mobi2cbz.py "D:\\Manga" --quiet --log "D:\\Manga\\convert.log"

参数:
    --delete         转换成功后删除原始 mobi 文件
    --prefer         双目录 mobi（mobi7/mobi8）时保留哪份，默认 mobi8
    --drop-extra     目录中有未被收集的多余图片时放弃追加，默认追加到末尾
    --overwrite      目标 cbz 已存在时强制重新生成（默认跳过）
    --timeout SECONDS 单文件转换超时秒数，超时自动跳过并计入失败（默认 600，0 表示不限制）
    --quiet          静默模式：只显示错误与最终汇总（日志文件不受影响）
    --log FILE       将全部输出追加写入指定日志文件
    --version        显示版本号

依赖: pip install mobi
要求: Python 3.10+

更新日志:
    v1.5.0 (2026-08-13)
        - 新增单文件超时保护：--timeout 秒数（默认 600），损坏/加密/超大
          mobi 导致 mobi.extract 无限阻塞时自动跳过该文件并计入失败，
          不再卡死整批转换；超时线程无法强制终止，卡死场景会残留一个
          后台线程，但主流程可继续处理后续文件（0 表示不限制）
        - 修复图片路径大小写兼容：ensure_cover_first 封面比对与
          align_images_with_dir 目录对齐改用归一化小写路径，Windows
          不区分大小写场景下不再因大小写命名差异误判重复/遗漏
        - 所有输出自动追加时间戳前缀 [YYYY-MM-DD HH:MM:SS]，
          控制台与日志文件均带时间，方便定位每次转换的执行时刻
        - 日志写入容错：--log 写入失败（非法字符/超长路径、磁盘满、
          只读分区、文件被独占等）时捕获全部 Exception 并打印一次警告，
          避免用户误以为日志已保存
        - Ctrl+C 中断兜底：批量转换中途按 Ctrl+C 不再直接抛异常退出，
          主循环捕获 KeyboardInterrupt 后强制输出当前已完成/失败的进度汇总
        - 汇总补全跳过列表：--overwrite 未开启时因目标 cbz 已存在而跳过的
          文件计入 "跳过文件" 计数并列出完整路径
        - --overwrite 覆盖重生成的标记仅保留单文件处理时的 [覆盖] 日志，
          不进最终汇总（--log 写入日志文件）
        - 移除无效的外层 TemporaryDirectory 兜底：解压临时目录由
          extract_temp_paths + finally 统一清理

    v1.4.0 (2026-08-13)
        - 修复临时目录残留：mobi.extract 不支持 output_dir 参数，改为
          仅传输入文件并记录其生成的解压路径，finally 统一清理，
          正常 / Ctrl+C / 异常均不残留
        - 依赖检测前置到模块顶部，启动即校验
        - 新增 DRM 加密识别提示：解压失败（异常含 drm/encrypt 等关键词）
          或解压后未提取到任何图片时，明确提示可能为 DRM 加密的 Kindle
          漫画，mobi 库无法解密，避免静默失败
        - 新增 --overwrite 参数：目标 cbz 已存在时强制重新生成，
          更新漫画后无需手动删除旧 cbz
        - 新增 --quiet 静默模式：只显示错误与最终汇总，
          批量转换时不再刷屏；--log FILE 将全部输出追加写入日志文件
        - 转换开始前列出待转换 mobi 文件完整路径，
          转换完成后列出输出 cbz 文件完整路径
        - 转换完成后列出失败文件数量与完整路径（跳过已存在的不计为失败）

    v1.3.0 (2026-08-13)
        - 新增封面兜底：spine 提取后扫描文件名含 cover/front 的图片；
          封面已在列表中则以列表顺序为准，仅缺失时插入首位，
          修复封面仅由 OPF metadata meta 定义、未在 spine 中引用时导致的丢页
        - 封面关键字兼容 cover 与 front 两种命名
        - 新增目录对齐兜底：目录图片数与收集数不一致时，
          多出的图片默认按自然排序追加到 cbz 末尾，--drop-extra 可改为放弃，
          处理结果会打印输出

    v1.2.0 (2026-08-13)
        - 新增 OPF spine 顺序提取图片，按真实阅读顺序排列
        - 重名图片改用序号前缀（{idx:04d}_），保证顺序且不冲突
        - 新增 select_mobi_dir 目录选择逻辑
        - 新增 --version 参数

    v1.1.0 (2026-08-13)
        - 脚本更名为 manga-mobi2cbz
        - 新增 __version__ 与 SCRIPT_NAME 常量

    v1.0.0 (2026-08-12)
        - 首个可用版本：递归收集 mobi、批量转 cbz、双目录去重、
          EOCD + testzip 完整性校验、失败清理半成品
"""

__version__ = "1.5.0"

SCRIPT_NAME = "manga-mobi2cbz"

import os
import re
import sys
import shutil
import zipfile
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 全局前置依赖检测，启动即校验，无需等到循环文件
try:
    import mobi
except ImportError:
    print("【致命错误】缺少核心依赖 mobi，请执行安装命令：")
    print("    pip install mobi")
    sys.exit(1)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif"}
EOCD_SIGNATURE = b"\x50\x4b\x05\x06"  # End of Central Directory 签名
OPF_NS = {"opf": "http://www.idpf.org/2007/opf"}


def norm_path(p: Path) -> str:
    """路径归一化：resolve 后转小写，兼容 Windows 不区分大小写的文件系统，
    避免同名仅大小写差异的文件在对比时被误判为不同/重复。"""
    return str(p.resolve()).lower()


def run_with_timeout(func, timeout: float, *args, **kwargs):
    """在单线程池中执行 func，超过 timeout 秒返回 None（调用方按超时处理）。

    timeout <= 0 时不限制，直接在当前线程执行。
    注意：Python 无法强制终止阻塞线程，超时后该线程可能继续在后台运行；
    若 mobi.extract 永久卡死会残留一个后台线程，但主流程可继续处理后续
    文件，不会卡死整批转换。"""
    if timeout <= 0:
        return func(*args, **kwargs)
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(func, *args, **kwargs)
    try:
        return future.result(timeout=timeout)
    except TimeoutError:
        return None
    finally:
        # wait=False：不等待可能永久阻塞的工作线程
        executor.shutdown(wait=False)

# 全局输出控制：--quiet 抑制 info 输出，--log 将输出同时写入文件
_quiet_mode = False
_log_path = None
_log_write_failed = False


def emit(msg: str, level: str = "info") -> None:
    """统一输出入口。

    level=info: 常规信息，--quiet 时隐藏（仍写入日志文件）
    level=summary/error: 汇总与错误，--quiet 时也显示
    设置 --log 后所有级别均写入日志文件。
    每条输出自动追加 [YYYY-MM-DD HH:MM:SS] 时间戳前缀，
    控制台与日志文件保持一致。
    日志写入失败（非法路径 / 磁盘满 / 文件独占等）时打印一次警告，
    避免用户误以为日志已正常保存。
    """
    global _log_write_failed
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if msg.startswith("\n"):
        # 前导换行移到时间戳之前，避免出现孤立的空时间戳行
        line = "\n" + f"[{ts}] " + msg.lstrip("\n")
    else:
        line = f"[{ts}] {msg}"
    if _log_path:
        try:
            with open(_log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            if not _log_write_failed:
                _log_write_failed = True
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 【警告】日志写入失败（{e}），日志文件: {_log_path}，后续日志不再写入")
    if not _quiet_mode or level in ("summary", "error"):
        print(line)


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


def find_opf(base_dir: Path) -> Path | None:
    """在目录下递归查找 .opf 文件"""
    for p in base_dir.rglob("*.opf"):
        return p
    return None


def extract_images_from_html(html_path: Path) -> list[Path]:
    """从 HTML 文件中提取所有 <img> 引用的本地图片路径"""
    try:
        content = html_path.read_text(encoding="utf-8", errors="ignore")
        srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        base_dir = html_path.parent
        result = []
        for src in srcs:
            if src.startswith(("data:", "http://", "https://", "//")):
                continue
            img_path = (base_dir / src).resolve()
            if img_path.exists() and img_path.suffix.lower() in IMAGE_EXTENSIONS:
                result.append(img_path)
        return result
    except Exception:
        return []


def extract_images_by_spine(opf_path: Path) -> list[Path] | None:
    """按 OPF spine 顺序提取图片。成功返回图片路径列表，失败返回 None"""
    try:
        tree = ET.parse(opf_path)
        root = tree.getroot()

        # 解析 manifest: id -> href
        manifest = {}
        for item in root.findall(".//opf:manifest/opf:item", OPF_NS):
            item_id = item.get("id")
            href = item.get("href")
            if item_id and href:
                manifest[item_id] = href

        # 解析 spine 顺序（这才是权威阅读顺序）
        spine_ids = []
        for itemref in root.findall(".//opf:spine/opf:itemref", OPF_NS):
            idref = itemref.get("idref")
            if idref:
                spine_ids.append(idref)

        if not spine_ids:
            return None

        opf_dir = opf_path.parent
        images = []
        for sid in spine_ids:
            href = manifest.get(sid)
            if not href:
                continue
            html_path = (opf_dir / href).resolve()
            if not html_path.exists():
                continue
            imgs = extract_images_from_html(html_path)
            images.extend(imgs)

        return images if images else None
    except Exception:
        return None


COVER_KEYWORDS = ("cover", "front")


def ensure_cover_first(images: list[Path], base_dir: Path) -> list[Path]:
    """确保封面图片不被遗漏。

    扫描目录下文件名含 cover/front 的图片（如 cover00198.jpeg、
    front.jpeg）：
    - 封面已在 spine 提取列表中：保持列表顺序不变，以列表为准
    - 封面不在列表中：插入首位补齐
    没有候选封面时原样返回。
    """
    cover_candidates = []
    for p in base_dir.rglob("*"):
        if (
            p.is_file()
            and p.suffix.lower() in IMAGE_EXTENSIONS
            and any(k in p.name.lower() for k in COVER_KEYWORDS)
        ):
            cover_candidates.append(p)
    if not cover_candidates:
        return images
    cover_candidates.sort(key=natural_key)
    cover = cover_candidates[0]
    if any(norm_path(p) == norm_path(cover) for p in images):
        return images
    images.insert(0, cover)
    return images


def count_images_in_dir(base_dir: Path) -> int:
    """统计目录下所有图片数量（含子目录）"""
    count = 0
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if Path(f).suffix.lower() in IMAGE_EXTENSIONS:
                count += 1
    return count


def align_images_with_dir(images: list[Path], base_dir: Path, drop_extra: bool) -> tuple[list[Path], str | None]:
    """目录对齐兜底：把目录中存在但未被收集的图片补齐到末尾。

    返回 (处理后的图片列表, 处理说明文本或 None)：
    - 无多余图片：原样返回，说明为 None
    - 有多余图片且 drop_extra=False：追加到末尾并返回说明
    - 有多余图片且 drop_extra=True：放弃追加并返回说明
    """
    collected = {norm_path(p) for p in images}
    extras = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in IMAGE_EXTENSIONS and norm_path(p) not in collected:
                extras.append(p)
    extras.sort(key=natural_key)
    if not extras:
        return images, None
    if drop_extra:
        return images, f"[提示] 目录中 {len(extras)} 张图片未被收集，已按 --drop-extra 放弃"
    return images + extras, f"[提示] 目录中 {len(extras)} 张图片未被收集，已追加到末尾"


def collect_images_fallback(base_dir: Path) -> list[Path]:
    """兜底方案：直接扫描目录下所有图片，按自然排序"""
    images = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                images.append(Path(root) / f)
    images.sort(key=natural_key)
    return images


def select_mobi_dir(tempdir: Path, prefer: str) -> Path:
    """根据 prefer 参数选择 mobi7 或 mobi8 目录；如果只有一份则返回那一份"""
    mobi7_dir = tempdir / "mobi7"
    mobi8_dir = tempdir / "mobi8"

    has7 = mobi7_dir.is_dir()
    has8 = mobi8_dir.is_dir()

    if has7 and has8:
        chosen = mobi7_dir if prefer == "mobi7" else mobi8_dir
        emit(f"  [去重] 检测到双目录，保留 {'mobi7' if prefer == 'mobi7' else 'mobi8'}")
        return chosen
    if has8:
        return mobi8_dir
    if has7:
        return mobi7_dir
    # 都没有子目录，直接用 tempdir
    return tempdir


def mobi_to_cbz(mobi_path: Path, delete_original: bool = False, prefer: str = "mobi8", drop_extra: bool = False, overwrite: bool = False) -> tuple[Path | None, str]:
    """将单个 mobi 文件转换为 cbz

    prefer: 双目录 mobi（mobi7/mobi8）时保留哪份，默认 "mobi8"
    drop_extra: 目录中有未被收集的多余图片时放弃追加，默认追加到末尾
    overwrite: 目标 cbz 已存在时强制重新生成（默认跳过）

    返回 (结果, 状态)：状态为 "ok" / "skip" / "fail"，
    - "ok": 转换成功，结果为 cbz 路径
    - "skip": 目标已存在且未指定 --overwrite，结果为 None
    - "fail": 转换失败，结果为 None
    """
    cbz_path = mobi_path.with_suffix(".cbz")
    if cbz_path.exists() and not overwrite:
        emit(f"  [跳过] 目标已存在: {cbz_path.name}")
        return None, "skip"
    if cbz_path.exists():
        cbz_path.unlink()
        emit(f"  [覆盖] 已删除旧文件，重新生成: {cbz_path.name}")

    extract_temp_paths = []  # 记录mobi库自动生成的临时文件夹

    try:
        # mobi.extract 不支持 output_dir，仅传输入文件
        tempdir_raw, _ = mobi.extract(str(mobi_path))
        tempdir = Path(tempdir_raw)
        extract_temp_paths.append(tempdir)

        # Step 2: 选择目录（mobi7/mobi8 去重）
        base_dir = select_mobi_dir(tempdir, prefer)

        # Step 3: 优先按 OPF spine 顺序提取图片，兜底按文件名排序
        opf_path = find_opf(base_dir)
        if opf_path:
            images = extract_images_by_spine(opf_path)
            if images:
                emit(f"  [排序] 按 OPF spine 顺序（{len(images)} 张图片）")
            else:
                images = collect_images_fallback(base_dir)
                emit(f"  [排序] spine 提取为空，兜底按文件名排序（{len(images)} 张）")
        else:
            images = collect_images_fallback(base_dir)
            emit(f"  [排序] 未找到 OPF，兜底按文件名排序（{len(images)} 张）")

        if not images:
            emit(f"  [失败] 未找到图片: {mobi_path.name}", level="error")
            emit("  [提示] 可能为 DRM 加密的 Kindle 漫画，mobi 库无法解密，请先去除 DRM 后再转换", level="error")
            return None, "fail"

        # 确保封面在第一位（兼容 cover/front 命名，封面可能未被 spine 引用）
        images = ensure_cover_first(images, base_dir)

        # 目录对齐兜底：目录图片数 vs 收集数不一致时，多出的图片追加到末尾
        total_in_dir = count_images_in_dir(base_dir)
        images, align_msg = align_images_with_dir(images, base_dir, drop_extra)
        if align_msg:
            emit(f"  {align_msg}")
        elif total_in_dir != len(images):
            emit(f"  [提示] 目录共 {total_in_dir} 张图片，收集 {len(images)} 张，数量不一致")

        # Step 4: 打包为 cbz (ZIP 无压缩，因为图片已经压缩过了)
        seen = {}
        with zipfile.ZipFile(str(cbz_path), "w", zipfile.ZIP_STORED) as zf:
            for idx, img in enumerate(images, 1):
                if img.name in seen:
                    # 重名：用序号前缀 + 原文件名，保证顺序且不冲突
                    arcname = f"{idx:04d}_{img.name}"
                else:
                    arcname = img.name
                    seen[img.name] = arcname
                zf.write(str(img), arcname)

        size_mb = cbz_path.stat().st_size / (1024 * 1024)
        emit(f"  [完成] {cbz_path.name} ({len(images)} 张图片, {size_mb:.1f} MB)")

        # 完整性校验
        ok, msg = validate_cbz(cbz_path)
        if not ok:
            cbz_path.unlink(missing_ok=True)
            emit(f"  [校验失败] {cbz_path.name}: {msg}，已删除坏文件", level="error")
            return None, "fail"
        emit(f"  [校验] {msg}")

        # Step 5: 可选删除原始 mobi
        if delete_original:
            mobi_path.unlink()
            emit(f"  [清理] 已删除原始文件: {mobi_path.name}")

        return cbz_path, "ok"
    except Exception as e:
        # 转换失败仅清理半成品cbz
        if cbz_path.exists():
            cbz_path.unlink(missing_ok=True)
        emit(f"  [错误] {mobi_path.name}: {e}", level="error")
        err = str(e).lower()
        if any(k in err for k in ("drm", "encrypt", "decrypt", "protected", "kfx")):
            emit("  [提示] 该文件可能为 DRM 加密的 Kindle 漫画，mobi 库无法解密，请先去除 DRM 后再转换", level="error")
        return None, "fail"
    finally:
        # 无论正常/异常，强制删除 mobi 解压出来的临时目录，解决 Ctrl+C 残留
        for p in extract_temp_paths:
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)


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
    parser.add_argument(
        "--drop-extra",
        action="store_true",
        help="目录中有未被收集的多余图片时放弃追加（默认追加到 cbz 末尾）",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="目标 cbz 已存在时强制重新生成（默认跳过）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        metavar="SECONDS",
        help="单文件转换超时秒数，超时自动跳过并计入失败（默认 600，0 表示不限制）",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式：只显示错误与最终汇总（日志文件不受影响）",
    )
    parser.add_argument(
        "--log",
        metavar="FILE",
        help="将全部输出追加写入指定日志文件",
    )
    args = parser.parse_args()

    global _quiet_mode, _log_path
    _quiet_mode = args.quiet
    _log_path = args.log

    target = Path(args.target)
    if not target.exists():
        emit(f"路径不存在: {args.target}", level="error")
        sys.exit(1)

    mobi_files = collect_mobi_files(target)
    if not mobi_files:
        emit(f"未找到 .mobi 文件: {args.target}", level="error")
        sys.exit(0)

    emit(f"找到 {len(mobi_files)} 个 mobi 文件，开始转换...\n")
    for mf in mobi_files:
        emit(f"  [文件] {mf}")
    emit("")

    success = 0
    success_cbzs = []
    skipped_files = []
    failed_files = []
    interrupted = False
    try:
        for mf in mobi_files:
            converted = run_with_timeout(
                mobi_to_cbz, args.timeout,
                mf, delete_original=args.delete, prefer=args.prefer,
                drop_extra=args.drop_extra, overwrite=args.overwrite,
            )
            if converted is None:
                emit(f"  [超时] {mf.name}: 转换超过 {args.timeout} 秒，已跳过（计入失败）", level="error")
                failed_files.append(mf)
                continue
            result, status = converted
            if status == "ok":
                success += 1
                success_cbzs.append(result)
            elif status == "skip":
                skipped_files.append(mf)
            elif status == "fail":
                failed_files.append(mf)
    except KeyboardInterrupt:
        # Ctrl+C：中断主循环，但仍输出已完成部分的汇总（临时目录由 mobi_to_cbz 的 finally 清理）
        interrupted = True
        emit("\n检测到 Ctrl+C，中断转换，输出当前进度汇总：", level="summary")

    emit(f"\n转换完成: {success}/{len(mobi_files)} 成功", level="summary")
    if interrupted:
        emit("（任务被中断，以上为已处理部分的汇总，剩余文件未处理）", level="summary")
    if success_cbzs:
        emit("输出文件:")
        for cbz in success_cbzs:
            emit(f"  {cbz}")
    if skipped_files:
        emit(f"跳过文件（目标 cbz 已存在）: {len(skipped_files)} 个", level="summary")
        for mf in skipped_files:
            emit(f"  {mf}", level="summary")
    if failed_files:
        emit(f"失败文件: {len(failed_files)} 个", level="summary")
        for mf in failed_files:
            emit(f"  {mf}", level="summary")


if __name__ == "__main__":
    main()
