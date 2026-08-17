#!/usr/bin/env python3
"""
manga-mobi2cbz — 将 mobi/azw/azw3 电子书漫画文件批量转换为 cbz 格式（OPF spine 排序 + 封面兜底增强版）

用法:
    python manga-mobi2cbz.py <目录或文件路径> [--language auto|zh-CN|zh-TW|ja|en] [--delete] [--prefer mobi7|mobi8] [--ext-priority EXTS] [--drop-extra] [--overwrite] [--timeout SECONDS] [--output-dir DIR] [--flatten] [--dry-run] [--progress|--no-progress] [--quiet] [--short-summary] [--compress LEVEL] [--inspect] [--inspect-all] [--no-comicinfo] [--log FILE]

示例:
    # 转换整个文件夹（递归搜索所有 .mobi/.azw/.azw3）
    python manga-mobi2cbz.py "D:\\Manga\\"

    # 转换单个文件
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi"

    # 转换后自动删除原始电子书
    python manga-mobi2cbz.py "D:\\Manga" --delete

    # 双目录 mobi 时保留 mobi7
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi" --prefer mobi7

    # 目录中有未被收集的多余图片时放弃追加（默认追加到 cbz 末尾）
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi" --drop-extra

    # 已存在 cbz 时强制重新生成（覆盖旧文件）
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi" --overwrite

    # 单文件转换超过 300 秒自动跳过（防止损坏/加密电子书卡死批量任务）
    python manga-mobi2cbz.py "D:\\Manga" --timeout 300

    # CBZ 输出到自定义目录（默认保留相对输入的子目录结构，如 One Piece/001.mobi → E:\CBZ\One Piece\001.cbz）
    python manga-mobi2cbz.py "D:\\Manga" --output-dir "E:\\CBZ"

    # 平铺输出：所有 CBZ 直接放到输出目录根下（重名自动编号）
    python manga-mobi2cbz.py "D:\\Manga" --output-dir "E:\\CBZ" --flatten

    # 试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录
    python manga-mobi2cbz.py "D:\\Manga" --dry-run

    # 强制显示文件级进度条（批量转换时默认在 TTY 下自动显示）
    python manga-mobi2cbz.py "D:\\Manga" --progress

    # 静默模式批量转换，只显示错误与汇总；完整输出写入日志文件
    python manga-mobi2cbz.py "D:\\Manga" --quiet --log "D:\\Manga\\convert.log"

    # 以 deflate 压缩级别 9 打包（PNG 源收益明显，JPEG 源没必要）
    python manga-mobi2cbz.py "D:\\Manga" --compress 9

    # 检查模式：目录随机抽查 1 个 / 单文件直接检查（元数据/结构/图片/分辨率/DRM），不生成 CBZ
    python manga-mobi2cbz.py "D:\\Manga" --inspect

    # 检查全部电子书内部信息（--inspect-all 单独使用也会自动启用 --inspect）
    python manga-mobi2cbz.py "D:\\Manga" --inspect --inspect-all

参数:
    --language LANG  输出语言：auto 按系统语言自动选择（zh 前缀→中文，
                     zh-TW/zh-Hant→繁体中文，ja/Japanese→日文，
                     否则→英文），或指定 zh-CN/zh-TW/ja/en
    --delete         转换成功后删除原始电子书文件
    --prefer         双目录 mobi（mobi7/mobi8）时保留哪份，默认 mobi8
    --ext-priority EXTS 同目录同名（仅扩展名不同）时保留哪种格式，
                     逗号分隔、顺序即优先级从高到低，仅接受
                     mobi/azw/azw3，默认 azw3；优先级未覆盖时
                     回退兜底顺序 azw3→mobi→azw；与 --prefer（双目录）无关
    --drop-extra     目录中有未被收集的多余图片时放弃追加，默认追加到末尾
    --overwrite      目标 cbz 已存在时强制重新生成（默认跳过）
    --timeout SECONDS 单文件转换超时秒数，超时自动跳过并计入失败（默认 600，0 表示不限制）
    --min-size BYTES  过滤小于指定字节的电子书（不带数字默认 1000，0 关闭，不传则关闭）
    --output-dir DIR CBZ 输出到指定目录（自动创建），默认保留相对输入的
                     子目录结构（如 One Piece/001.mobi → DIR/One Piece/001.cbz），
                     需要平铺时加 --flatten
    --flatten       仅与 --output-dir 联用：所有 CBZ 平铺到输出目录根下，
                     重名自动编号 base.cbz → base (2).cbz → …；
                     单独使用（无 --output-dir）将报错退出
    --dry-run        试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录
    --progress       强制显示文件级进度条（默认 TTY 且文件数≥2 时自动显示；
                     与 --no-progress 同传时以最后出现的参数为准）
    --no-progress    强制关闭进度条（即使 TTY 且文件数≥2）
    --quiet          静默模式：只显示错误与最终汇总（日志文件不受影响）
    --short-summary  精简汇总：成功/跳过文件只显示数量不列出路径，失败始终全路径
    --compress LEVEL zip 压缩级别 0-9：0=不压缩（默认，图片本身已压缩），
                     1-9=deflate 压缩（PNG 源有收益，级别越高越小但越慢）
    --inspect       检查模式：位置参数为单个文件时直接检查该文件，
                     为目录时随机抽查 1 个，只解包读取内部信息
                     （元数据/结构/图片/分辨率/DRM），不生成 CBZ，
                     结束自动清理临时目录
    --inspect-all   检查全部电子书（需配合 --inspect 使用，
                     单独使用将自动启用 --inspect）
    --no-comicinfo  不生成 ComicInfo.xml（默认生成：向 CBZ 根目录写入
                     Title/Series/Number/Writer/Publisher/Year/
                     LanguageISO/PageCount/Summary 等漫画元数据）
    --log FILE       将全部输出追加写入指定日志文件
    --version        显示版本号

依赖: pip install mobi
要求: Python 3.10+

更新日志:
    v2.0.1 (2026-08-17)
        - 修复 infer_series_number 对无系列名卷标记文件名
          （Vol.01 / Volume 01 / 01巻 等）误推断系列名的问题，
          新增 _is_volume_marker 卷标记词过滤
    v2.0.0 (2026-08-14)
        - 新增 ComicInfo.xml 生成（默认启用，--no-comicinfo 关闭）：
          写入 CBZ ZIP 根目录，UTF-8 含 XML 声明
        - 新增函数 build_comicinfo / write_comicinfo /
          normalize_language / infer_series_number
        - 字段映射：Title=OPF title→EXTH title→文件名 stem；
          Writer=OPF creator→EXTH author；Publisher=OPF publisher→
          EXTH publisher；Year=PublicationDate 年份；LanguageISO=电子书
          自身语言（ISO 639-1 标准化，不按文件名猜）；PageCount=最终写入
          CBZ 的实际图片数（必写）；Series/Number=文件名高置信度推断
          （支持 001/01/1/Vol.01/Vol 01/Volume 01/第 01 卷 等，无法
          高置信度判断时省略，宁缺勿错）；Summary=OPF description
        - 无可靠来源的字段省略，不生成空标签
        - 完整性校验新增 3 项：ComicInfo.xml 存在、可被标准 XML parser
          解析、根节点为 ComicInfo；生成/验证失败=整个转换任务失败，
          禁止 --delete 删除源文件
        - --dry-run 不创建 ComicInfo.xml，输出一行提示启用状态
        - --inspect 追加 ComicInfo 预览块，推断字段标记 [inferred]
        - i18n 四语言新增 6 键：comicinfo.generating / comicinfo.created
          / comicinfo.disabled / comicinfo.invalid / comicinfo.inferred /
          help.no_comicinfo；README 三语同步
        - 修复 infer_series_number 对无系列名卷标记文件的误推断：
          "Vol.01" / "Volume 01" / "01巻" 等不再被推断出系列名，
          统一返回 (None, None)（新增 _is_volume_marker 卷标记词过滤，
          宁缺勿错）；"One Piece Vol.01" 等正常推断不受影响

    v1.9.1 (2026-08-14)
        - --inspect-all 单独使用（未配合 --inspect）时自动启用
          --inspect 并输出 warning 提示（四语言新增键
          warn.inspect_all_auto_enable，中文「注意: --inspect-all 已自动启用 --inspect」）
        - --inspect / --inspect-all 说明文案更新：位置参数为单个文件
          时直接检查该文件、为目录时随机抽查 1 个；--inspect-all 单独
          使用将自动启用 --inspect；README 三语参数表同步

    v1.9.0 (2026-08-14)
        - [Breaking] --output-dir 默认保留相对输入的子目录结构（旧版一律平铺）
          * 迁移方式：旧命令 ... --output-dir DIR 改为
            ... --output-dir DIR --flatten 即可恢复旧行为
        - 新增 --flatten：与 --output-dir 联用时平铺到输出目录根下；
          重名自动唯一化 base.cbz → base (2).cbz → …，不静默覆盖、不跳过
        - 仅使用 --flatten 而无 --output-dir 将报错退出（exit 2）
        - 输出根目录存在同名文件时：保留结构模式仍按 SKIP/--overwrite
          语义处理；平铺模式以自动编号避让为主
        - run_with_timeout 返回值改为 (timed_out, result) 二元组：超时
          → (True, None)，正常 → (False, 函数返回值)，消除 None 歧义
        - --inspect 超时提示追加“临时目录可能残留，请手动清理”
        - 打包阶段 seen 增加归一化路径判物理重复：同一物理文件重复出现
          时跳过不写入（重名不同文件仍序号前缀），输出去重计数
        - 新增 HtmlImgParser（HTMLParser 子类）兜底提取 <img src>：
          HTML 实体由 HTMLParser 自动解码 + unquote 处理 %XX，
          接入 OPF/spine 的 HTML 图片提取，正则未命中时启用
        - --dry-run 增加输出目录可写性检查（--output-dir 或源目录），
          不可写时输出 warning 提示

    v1.8.0 (2026-08-14)
        - 新增轻量多语言支持：--language auto|zh-CN|zh-TW|ja|en（默认
          auto 按系统 locale 自动判定：简体中文归 zh-CN、繁体中文归
          zh-TW、日文（ja/Japanese）归 ja、其余归 en）；全量输出文案与
          --help 随语言翻译，缺键回退 en→键名不抛异常；业务代码不写
          if lang 分支，参数名/枚举/书籍 metadata/OPF/DRM/spine 等
          专有词不翻译
        - 新增 AZW / AZW3 输入支持：输入扩展名扩展为 .mobi/.azw/.azw3，
          统一走 extract → OPF/spine → 封面 → 打包 → 校验链路
        - 新增 --ext-priority EXTS：同目录同主文件名（仅扩展名不同）时
          保留哪种格式，逗号分隔、顺序即优先级从高到低，仅接受
          mobi/azw/azw3，默认 azw3；优先级未覆盖时回退兜底顺序
          azw3→mobi→azw 并输出提示；与 --prefer（双目录选择）无关
        - 收集/预检查/去重/转换/检查函数统一支持三种格式：
          collect_ebook_files / precheck_ebook / dedupe_ebook_files /
          ebook_to_cbz / inspect_ebook；三种格式统一偏移 60 BOOKMOBI
          魔数校验，不命中时输出 warning 并仍尝试解包（降级策略，
          mobi.extract 自带二次校验，解包失败计入失败列表）
        - --delete 与 --inspect/--inspect-all 同步支持三种格式；
          文案统一：mobi 文件 → 电子书文件
        - 新增文件级进度条：--progress/--no-progress 开关（同传时以最后
          出现的参数为准）；默认 TTY 且文件数≥2 自动显示；--quiet 下
          进度条保留；写 stderr、不进 emit/--log；tqdm 为可选依赖，
          缺失时降级为简单文本进度不崩溃；覆盖转换/试运行/检查（全量）
          三种模式；显示 当前/总数、百分比、ETA、平均耗时、当前文件名
          （截断 40 字符）；Ctrl+C/超时正常 close 并输出汇总
        - 代码卫生与体验优化（并入 v1.8.0）：
          - 删除重复的 from concurrent.futures import ThreadPoolExecutor
          - LANGUAGES 字典按功能分区补充中文注释（【预处理】【转换】
            【检查】【汇总】，含 help/progress/tag 等分区）
          - --language auto 时 INFO 级打印"识别语种为 X"（quiet 时抑制）
          - 魔数校验降级：precheck 魔数失败由"判损坏跳过"改为 warning
            提示 + 仍尝试解包（extract 自带二次校验）
          - --ext-priority 非法值报错文案多语言化（四语言表新增
            error.ext_priority_empty / error.ext_priority_invalid 键）
          - argparse 参数定义与主要函数输入参数补充中文注释

    v1.7.0 (2026-08-13)
        - 新增 --inspect 检查模式：随机抽查 1 个 mobi（--inspect-all 全量），
          只解包读取内部信息不生成 CBZ，结束后自动清理临时目录；
          输出基础检查（魔数/大小/DRM）、EXTH 元数据（标题/作者/语言/
          出版日期/出版社/ISBN，读到才显示）、双目录标记、OPF 与 spine
          提取数、目录全部图片数、封面、图片格式分布、主流分辨率（主流
          高/宽 + 另一维范围）、压缩建议；疑似 DRM（无图）与解包超时单独计数
        - --inspect 增强（并入 v1.7.0 发版）：
          - 封面检测：OPF guide type=cover 官方引用优先于文件名扫描，
            未命中回退文件名匹配（cover/front）
          - spine 提取图片前 5 个文件名竖排预览，便于排查阅读顺序
          - 新增目录(NCX)解析：toc.ncx 条目数 + 前 3 条标题预览
          - EXTH 元数据新增 ASIN(type113)、版权(type109) 字段
          - DRM 双重判断：头部标记有→直接判有并跳过解包；无标记+
            解包图片0→疑似；无标记+有图片→无，汇总行新增 DRM标记 计数
          - 双目录选择统一走 select_mobi_dir 公用函数，新增 prefer
            参数由 --prefer 控制 mobi7/mobi8，不再手写判断
          - 输出行缩进统一为 2 空格，修复 OPF 行缩进不一致
        - 打包分支重构：compress>0 用 ZIP_DEFLATED+compresslevel，
          否则 ZIP_STORED，消除旧版 Python 在 STORED 下传
          compresslevel=None 的弃用警告
        - 新增 --compress LEVEL：zip 压缩级别 0-9，0=不压缩（默认，
          图片本身已压缩），1-9=deflate 压缩，PNG 源可显著减小体积，
          级别越高越小但越慢，JPEG 源收益有限不建议开

    v1.6.0 (2026-08-13)
        - 新增 --output-dir DIR：CBZ 输出到指定目录（自动创建），
          不再强制与源 mobi 同目录；--overwrite 存在性判断同样基于输出目录
        - 新增预处理过滤：0 字节、文件头校验失败（偏移 60 处无 BOOKMOBI
          魔数，疑似损坏或非 mobi）的文件直接跳过，不再进入转换，
          日志输出跳过文件完整路径与原因
        - 新增 --dry-run 试运行：只扫描与预处理，打印每个文件的
          转换流程与目标输出路径，不实际解压打包、不创建输出目录、
          无任何磁盘写入，并同步打印预处理过滤列表（与真实运行
          保持一致），适合先确认结果
        - 新增 --min-size BYTES：过滤小于指定字节数的 mobi（不带数字
          默认 1000，0 关闭，不传则关闭大小过滤），兜住头部恰好完整
          但内容被截断的边缘损坏样本；同时预处理增加"无法读取文件
          （OSError）"的跳过原因分支
        - 新增耗时统计：每个文件转换耗时实时输出，汇总底部输出
          总耗时（成功/失败/跳过均计入）
        - 状态魔法字符串重构为 ConvStatus 枚举（OK/SKIP/FAIL），
          mobi_to_cbz 返回类型改为 tuple[Path | None, ConvStatus]，
          主循环分支与返回处统一使用枚举成员，避免拼写错误
        - 输出标签提取为常量（TAG_INFO/TAG_FAIL/TAG_ERROR/TAG_SKIP/
          TAG_OVERWRITE/TAG_CLEAN/TAG_SORT/TAG_DEDUP/TAG_DONE/
          TAG_VERIFY/TAG_VERIFY_FAIL/TAG_TIMEOUT/TAG_ELAPSED/
          TAG_FILE/TAG_PENDING/TAG_WILL_SKIP/TAG_DRYRUN），
          统一管理方便后期统一修改输出样式
        - 加重 run_with_timeout 线程限制注释：明确超时后 mobi.extract
          工作线程会后台残留、持续占用内存/IO，批量大量损坏文件可能
          堆积僵尸线程；后续可改 multiprocessing 实现可终止子进程，
          但增加跨平台兼容复杂度，暂未采用
        - 顶层全局异常捕获：main() 统一 try/except，参数解析/文件收集
          等主循环外阶段的未捕获异常与 Ctrl+C 经 emit 输出堆栈到
          控制台与日志（带时间戳），不再裸堆栈退出
        - 新增 --short-summary：汇总精简模式，成功/跳过/预处理跳过文件
          只显示数量不逐条列出路径（失败文件始终全路径列出），dry-run
          不受影响，与 --quiet 互补，适合大批量目录
        - 汇总新增一行式转换统计（成功/跳过/失败三类数量，含 0），
          某类为 0 时原有明细行不打印，统计行保证三类数量始终可见

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

__version__ = "2.0.1"

SCRIPT_NAME = "manga-mobi2cbz"

import locale
import os
import re
import sys
import time
import random
import struct
import shutil
import zipfile
import argparse
import traceback
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote
from enum import Enum
from pathlib import Path
from datetime import datetime
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

# =========================
# 多语言（轻量 i18n：zh-CN / zh-TW / en，单文件内完成）
# 业务只引用消息键 t("key", **kwargs)，不写 if lang == 分支；
# 参数名、内部枚举、书籍 metadata、OPF/DRM/spine 等专有词不翻译。
# =========================

LANGUAGES = {
    "zh-CN": {
        "error.missing_dependency": "【致命错误】缺少核心依赖 mobi，请执行安装命令：",
        "error.log_write_failed": "【警告】日志写入失败（{err}），日志文件: {path}，后续日志不再写入",
        "error.ext_priority_empty": "--ext-priority 不能为空",
        "error.ext_priority_invalid": "--ext-priority 仅接受 mobi/azw/azw3，收到: {p}",
        # ---- --help 文案 ----
        "help.description": "mobi/azw/azw3 漫画批量转 cbz",
        "help.language": "输出语言：auto 按系统语言自动选择（zh 前缀→中文，zh-TW/zh-Hant→繁体中文，ja/Japanese→日文，否则→英文），或指定 zh-CN/zh-TW/ja/en",
        "help.target": "电子书文件路径或包含电子书（.mobi/.azw/.azw3）的目录",
        "help.delete": "转换成功后删除原始电子书文件",
        "help.prefer": "双目录 mobi（mobi7/mobi8）时保留哪份，默认 mobi8",
        "help.ext_priority": "同目录同名（仅扩展名不同）时保留哪种格式：逗号分隔、顺序即优先级从高到低，仅接受 mobi/azw/azw3，默认 azw3；优先级未覆盖时回退兜底顺序 azw3→mobi→azw；与 --prefer（双目录选择）无关",
        "help.drop_extra": "目录中有未被收集的多余图片时放弃追加（默认追加到 cbz 末尾）",
        "help.overwrite": "目标 cbz 已存在时强制重新生成（默认跳过）",
        "help.timeout": "单文件转换超时秒数，超时自动跳过并计入失败（默认 600，0 表示不限制）",
        "help.min_size": "过滤小于指定字节的电子书；不带数字默认1000字节，0关闭大小过滤，不传则关闭",
        "help.output_dir": "CBZ 输出到指定目录（自动创建），默认保留相对输入的子目录结构（如 One Piece/001.mobi → DIR/One Piece/001.cbz），加 --flatten 可平铺到目录根下",
    "help.flatten": "仅与 --output-dir 联用：所有 CBZ 平铺到输出目录根下，重名自动编号 (2)(3)…；单独使用将报错退出",
        "help.dry_run": "试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录",
        "help.progress": "强制显示文件级进度条（默认 TTY 且文件数≥2 时自动显示；与 --no-progress 同传时以最后出现的参数为准）",
        "help.no_progress": "强制关闭进度条（即使 TTY 且文件数≥2）",
        "help.quiet": "静默模式：只显示错误与最终汇总（日志文件不受影响）",
        "help.short_summary": "精简汇总：成功/跳过文件只显示数量不列出路径，失败文件始终全路径列出",
        "help.compress": "zip 压缩级别 0-9：0=不压缩（默认，图片本身已压缩），1-9=deflate 压缩（PNG 源有收益，级别越高越小但越慢）",
        "help.inspect": "检查模式：位置参数为单个文件时直接检查该文件，为目录时随机抽查 1 个，只解包读取内部信息（元数据/结构/图片/分辨率/DRM），不生成 CBZ，结束自动清理临时目录",
        "help.inspect_all": "检查全部电子书（需配合 --inspect 使用，单独使用将自动启用 --inspect）",
        "warn.inspect_all_auto_enable": "注意: --inspect-all 已自动启用 --inspect",
        "help.no_comicinfo": "不生成 ComicInfo.xml（默认生成：向 CBZ 根目录写入漫画元数据）",
        "comicinfo.generating": "生成 ComicInfo.xml",
        "comicinfo.created": "已写入 ComicInfo.xml",
        "comicinfo.disabled": "ComicInfo.xml 已禁用（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml 无效或生成失败: {err}",
        "comicinfo.inferred": "推断",
        "help.log": "将全部输出追加写入指定日志文件",
        # ---- 输出标签 ----
        "tag.info": "[提示]",
        "tag.fail": "[失败]",
        "tag.error": "[错误]",
        "tag.skip": "[跳过]",
        "skip_entry": "[跳过] {path}（{reason}）",
        "tag.overwrite": "[覆盖]",
        "tag.clean": "[清理]",
        "tag.sort": "[排序]",
        "tag.dedup": "[去重]",
        "tag.done": "[完成]",
        "tag.verify": "[校验]",
        "tag.verify_fail": "[校验失败]",
        "tag.timeout": "[超时]",
        "tag.elapsed": "[耗时]",
        "tag.file": "[文件]",
        "tag.pending": "[待转换]",
        "tag.will_skip": "[将跳过]",
        "tag.dryrun": "[试运行]",
        # ---- 进度条 ----
        "progress.desc.convert": "转换中",
        "progress.desc.dry_run": "试运行",
        "progress.desc.inspect": "检查中",
        "progress.done": "{desc}: [{n}/{total}] 完成",
        # ---- 去重 ----
        "dedupe.fallback": "  [去重] 同名扩展名优先级 [{priority}] 未覆盖该组，回退兜底顺序: {order}",
        "dedupe.reason": "同目录同名，按 --ext-priority {priority} 保留 {name}",
        "dedupe.both_dirs": "  [去重] 检测到双目录，保留 {dir}",
        # ---- 目录对齐 ----
        "align.drop": "  [提示] 目录中 {count} 张图片未被收集，已按 --drop-extra 放弃",
        "align.append": "  [提示] 目录中 {count} 张图片未被收集，已追加到末尾",
        # ---- 【转换】转换流程 ----
        "convert.skip_exists": "  [跳过] 目标已存在: {name}",
        "convert.overwrite": "  [覆盖] 已删除旧文件，重新生成: {name}",
        "convert.spine": "  [排序] 按 OPF spine 顺序（{count} 张图片）",
        "convert.spine_empty": "  [排序] spine 提取为空，兜底按文件名排序（{count} 张）",
        "convert.dedup_physical": "  [去重] 跳过 {count} 个物理重复文件（同一文件重复出现，未写入 CBZ）",
        "convert.no_opf": "  [排序] 未找到 OPF，兜底按文件名排序（{count} 张）",
        "convert.no_images": "  [失败] 未找到图片: {name}",
        "convert.drm_hint": "  [提示] 可能为 DRM 加密的 Kindle 漫画，mobi 库无法解密，请先去除 DRM 后再转换",
        "convert.count_mismatch": "  [提示] 目录共 {total} 张图片，收集 {collected} 张，数量不一致",
        "convert.done": "  [完成] {name} ({count} 张图片, {size} MB)",
        "convert.verify_fail": "  [校验失败] {name}: {msg}，已删除坏文件",
        "convert.verify_ok": "  [校验] {msg}",
        "convert.deleted_original": "  [清理] 已删除原始文件: {name}",
        "convert.error": "  [错误] {name}: {err}",
        "convert.error_drm_hint": "  [提示] 该文件可能为 DRM 加密的 Kindle 漫画，mobi 库无法解密，请先去除 DRM 后再转换",
        # ---- 【检查】校验（CBZ 完整性）----
        "verify.no_eocd": "缺少 EOCD 记录（文件不完整，可能被中断）",
        "verify.bad_entry": "条目损坏: {name}",
        "verify.ok": "校验通过（{count} 个条目）",
        "verify.badzip": "BadZipFile: {err}",
        "verify.exception": "校验异常: {err}",
        # ---- 【预处理】预处理检查（大小/0字节/魔数）----
        "precheck.small": "文件{size}字节，低于最小限制{min}字节",
        "precheck.zero": "文件大小为 0 字节",
        "precheck.too_small": "文件过小（<68 字节），疑似损坏或非电子书文件",
        "precheck.magic": "文件头校验失败（偏移 60 处无 BOOKMOBI 魔数），疑似损坏或非电子书文件",
        "precheck.magic_warning": "  [警告] {name}: 文件头校验失败（偏移 60 处无 BOOKMOBI 魔数），仍尝试解包，解包失败将计入失败列表",
        "precheck.oserror": "无法读取文件（{err}）",
        # ---- 【检查】inspect 检查 ----
        "inspect.file_line": "[文件] {name} ({size} MB)",
        "inspect.base_invalid_magic": " 基础: 魔数非法（偏移 60 处无 BOOKMOBI） | --min-size 不会过滤",
        "inspect.base_reason": " 基础: {reason}",
        "inspect.invalid_hint": " 提示: 疑似损坏或非电子书文件，跳过解包",
        "inspect.base_magic_ok": "魔数合法",
        "inspect.drm_marked": "DRM: 有(头部标记)",
        "inspect.drm_unmarked": "DRM: 头部标记无",
        "inspect.below_min_size": "低于 --min-size({min})",
        "inspect.min_size_not_filter": "--min-size 不会过滤",
        "inspect.base_line": " 基础: {parts}",
        "inspect.drm_hint": " 提示: 头部已标记 DRM 加密，跳过解包，转换会失败需先去除 DRM",
        "inspect.meta_title": "标题 {value}",
        "inspect.meta_author": "作者 {value}",
        "inspect.meta_language": "语言 {value}",
        "inspect.meta_publish_date": "出版日期 {value}",
        "inspect.meta_publisher": "出版社 {value}",
        "inspect.meta_isbn": "ISBN {value}",
        "inspect.meta_asin": "ASIN {value}",
        "inspect.meta_copyright": "版权 {value}",
        "inspect.meta_line": " 元数据: {parts}",
        "inspect.both_dirs": "  双目录标记: mobi7={mobi7} mobi8={mobi8}",
        "inspect.opf_exists": "  OPF文件: 存在",
        "inspect.opf_missing": "  OPF文件: 不存在",
        "inspect.spine_count": "  Spine提取图片: {count} 张",
        "inspect.ncx_count": "  目录(NCX): {count} 个条目 | 预览: {preview}",
        "inspect.ncx_missing": "  目录(NCX): 未找到或解析失败",
        "inspect.dir_images": "  目录全部图片: {count} 张",
        "inspect.drm_suspected": "  DRM: 疑似(头部标记无但图片0张)",
        "inspect.cover_missing": "  封面文件未找到",
        "inspect.fmt_none": "  图片格式统计: 无图片可统计",
        "inspect.drm_bad_hint": "  提示: 疑似 DRM 加密或内容损坏，转换会失败，需先去除 DRM",
        "inspect.drm_none": "  DRM: 无(头部标记无+图片{count}张)",
        "inspect.cover_src_guide": "OPF guide 官方引用",
        "inspect.cover_src_filename": "文件名匹配",
        "inspect.cover_found": "  封面文件已找到: {name}（{src}）",
        "inspect.fmt_stats": "  图片格式统计: {parts}",
        "inspect.res_main_h": "主流高 {height} ({count}张, {pct}%)",
        "inspect.res_w_range": "宽 {min}~{max}",
        "inspect.res_main_w": "主流宽 {width} ({count}张, {pct}%)",
        "inspect.res_h_range": "高 {min}~{max}",
        "inspect.res_line": "  分辨率: {parts}",
        "inspect.adv_png": "  建议: PNG 为主，建议 --compress 6~9，可显著减小体积",
        "inspect.adv_jpeg": "  建议: JPEG 为主，--compress 收益有限，不建议开启",
        "inspect.adv_mixed": "  建议: 混合格式，可试 --compress 6 对比体积",
        "inspect.unpack_fail": " 提示: 解包失败（{err}）",
        # ---- 【检查】inspect 模式 ----
        "inspect_mode.precheck_header": "预处理跳过 {count} 个文件（魔数非法/过小，不进入检查）：",
        "inspect_mode.none": "无有效电子书文件可检查（全部被预处理过滤）",
        "inspect_mode.all": "检查全部 {count} 个有效电子书文件...\n",
        "inspect_mode.random": "随机抽查 1/{total} 个文件...\n",
        "inspect_mode.timeout": "  [超时] {name}: 检查超过 {seconds} 秒，已跳过（计入失败）",
        "inspect_mode.timeout_residue": "  [提示] 检查超时，解压临时目录可能残留，请手动清理",
        "inspect_mode.ctrl_c": "\n检测到 Ctrl+C，中断检查，输出当前进度汇总：",
        "inspect_mode.random_note": "[检查] 抽查 1/{total}（随机），全部查看请加 --inspect-all",
        "inspect_mode.summary": "[检查] 检查完成: 共 {total} 个, 正常 {ok}, 魔数非法 {invalid}, DRM标记 {drm}, 疑似DRM/无图 {noimg}, 解包超时 {timeout}, 共耗时 {elapsed}s",
        # ---- 【汇总】主入口 ----
        "main.ctrl_c": "[提示] 用户中断（Ctrl+C），程序退出",
        "main.crash": "程序崩溃，堆栈信息如下：",
        # ---- 【汇总】运行主流程（汇总统计）----
        "run.auto_language": "已自动识别语种为 {lang}",
        "run.path_not_found": "路径不存在: {path}",
        "run.no_ebooks": "未找到电子书文件（.mobi/.azw/.azw3）: {path}",
        "run.precheck_header": "预处理跳过 {count} 个文件：",
        "run.none_convertible": "无有效电子书文件可转换（全部被预处理过滤或同名去重）",
        "run.found": "找到 {total} 个有效电子书文件（预处理过滤 {pre} 个，同名去重 {dedup} 个）\n",
        "run.dryrun_banner": "[试运行] --dry-run 模式：仅扫描与打印流程，不实际解压打包、不创建输出目录",
        "dryrun.output_not_writable": "  [警告] 输出目录不可写: {path}，正式转换将失败",
        "run.plan_output_dir": "计划输出目录: {path}（仅正式转换时自动创建）",
        "run.dryrun_precheck": "试运行预处理跳过 {count} 个文件：",
        "run.dryrun_end": "试运行结束，未产生任何输出文件与文件夹",
        "run.start": "开始转换 {count} 个文件...\n",
        "run.timeout": "  [超时] {name}: 转换超过 {seconds} 秒，已跳过（计入失败）",
        "run.elapsed": "  [耗时] {name}: {seconds} 秒",
        "run.ctrl_c": "\n检测到 Ctrl+C，中断转换，输出当前进度汇总：",
        "run.done": "\n转换完成: {success}/{total} 成功",
        "run.interrupted_note": "（任务被中断，以上为已处理部分的汇总，剩余文件未处理）",
        "run.stats": "转换统计: 成功 {success} 个, 跳过 {skip} 个, 失败 {fail} 个",
        "run.output_short": "输出文件: {count} 个（精简汇总，不列出路径）",
        "run.output_header": "输出文件:",
        "run.skipped_header": "跳过文件（目标 cbz 已存在）: {count} 个",
        "run.failed_header": "失败文件: {count} 个",
        "run.total_elapsed": "总耗时: {seconds} 秒",
    "output.mode_preserve": "输出模式: 保留相对子目录结构 -> {dir}",
    "output.mode_flatten": "输出模式: 平铺（--flatten）-> {dir}",
    "output.renamed_due_to_conflict": "  [提示] 目标 {name} 已存在，已自动重命名为 {new}",
    "output.flatten_requires_dir": "--flatten 需配合 --output-dir 使用，请同时指定输出目录",
    "error.flatten_without_output_dir": "--flatten 必须与 --output-dir 一起使用（无 --output-dir 时无法平铺）",
    "rel_fallback": "  [警告] 无法计算 {name} 的相对子目录路径（可能跨盘符），回退输出到输出目录根下: {path}",
    },
    "zh-TW": {
        "error.missing_dependency": "【致命錯誤】缺少核心依賴 mobi，請執行安裝命令：",
        "error.log_write_failed": "【警告】日誌寫入失敗（{err}），日誌檔案: {path}，後續日誌不再寫入",
        "error.ext_priority_empty": "--ext-priority 不能為空",
        "error.ext_priority_invalid": "--ext-priority 僅接受 mobi/azw/azw3，收到: {p}",
        # ---- --help 文案 ----
        "help.description": "mobi/azw/azw3 漫畫批量轉 cbz",
        "help.language": "輸出語言：auto 按系統語言自動選擇（zh 前綴→中文，zh-TW/zh-Hant→繁體中文，ja/Japanese→日文，否則→英文），或指定 zh-CN/zh-TW/ja/en",
        "help.target": "電子書檔案路徑或包含電子書（.mobi/.azw/.azw3）的目錄",
        "help.delete": "轉換成功後刪除原始電子書檔案",
        "help.prefer": "雙目錄 mobi（mobi7/mobi8）時保留哪份，預設 mobi8",
        "help.ext_priority": "同目錄同名（僅副檔名不同）時保留哪種格式：逗號分隔、順序即優先級從高到低，僅接受 mobi/azw/azw3，預設 azw3；優先級未覆蓋時回退兜底順序 azw3→mobi→azw；與 --prefer（雙目錄選擇）無關",
        "help.drop_extra": "目錄中有未被收集的多餘圖片時放棄追加（預設追加到 cbz 末尾）",
        "help.overwrite": "目標 cbz 已存在時強制重新生成（預設跳過）",
        "help.timeout": "單檔轉換逾時秒數，逾時自動跳過並計入失敗（預設 600，0 表示不限制）",
        "help.min_size": "過濾小於指定位元組的電子書；不帶數字預設1000位元組，0關閉大小過濾，不傳則關閉",
        "help.output_dir": "CBZ 輸出到指定目錄（自動建立），預設保留相對輸入的子目錄結構（如 One Piece/001.mobi → DIR/One Piece/001.cbz），加 --flatten 可平鋪到目錄根下",
    "help.flatten": "僅與 --output-dir 聯用：所有 CBZ 平鋪到輸出目錄根下，重名自動編號 (2)(3)…；單獨使用將報錯退出",
        "help.dry_run": "試運行：只掃描檔案並列印轉換流程，不實際解壓打包、不建立輸出目錄",
        "help.progress": "強制顯示檔案級進度條（預設 TTY 且檔案數≥2 時自動顯示；與 --no-progress 同傳時以最後出現的參數為準）",
        "help.no_progress": "強制關閉進度條（即使 TTY 且檔案數≥2）",
        "help.quiet": "靜默模式：只顯示錯誤與最終彙總（日誌檔案不受影響）",
        "help.short_summary": "精簡彙總：成功/跳過檔案只顯示數量不列出路徑，失敗檔案始終全路徑列出",
        "help.compress": "zip 壓縮級別 0-9：0=不壓縮（預設，圖片本身已壓縮），1-9=deflate 壓縮（PNG 來源有收益，級別越高越小但越慢）",
        "help.inspect": "檢查模式：位置參數為單一檔案時直接檢查該檔案，為目錄時隨機抽查 1 個，只解包讀取內部資訊（中繼資料/結構/圖片/解析度/DRM），不生成 CBZ，結束自動清理臨時目錄",
        "help.inspect_all": "檢查全部電子書（需配合 --inspect 使用，單獨使用將自動啟用 --inspect）",
        "warn.inspect_all_auto_enable": "注意: --inspect-all 已自動啟用 --inspect",
        "help.no_comicinfo": "不生成 ComicInfo.xml（預設生成：向 CBZ 根目錄寫入漫畫元資料）",
        "comicinfo.generating": "生成 ComicInfo.xml",
        "comicinfo.created": "已寫入 ComicInfo.xml",
        "comicinfo.disabled": "ComicInfo.xml 已停用（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml 無效或生成失敗: {err}",
        "comicinfo.inferred": "推斷",
        "help.log": "將全部輸出追加寫入指定日誌檔案",
        # ---- 输出标签 ----
        "tag.info": "[提示]",
        "tag.fail": "[失敗]",
        "tag.error": "[錯誤]",
        "tag.skip": "[跳過]",
        "skip_entry": "[跳過] {path}（{reason}）",
        "tag.overwrite": "[覆寫]",
        "tag.clean": "[清理]",
        "tag.sort": "[排序]",
        "tag.dedup": "[去重]",
        "tag.done": "[完成]",
        "tag.verify": "[校驗]",
        "tag.verify_fail": "[校驗失敗]",
        "tag.timeout": "[逾時]",
        "tag.elapsed": "[耗時]",
        "tag.file": "[檔案]",
        "tag.pending": "[待轉換]",
        "tag.will_skip": "[將跳過]",
        "tag.dryrun": "[試運行]",
        # ---- 进度条 ----
        "progress.desc.convert": "轉換中",
        "progress.desc.dry_run": "試運行",
        "progress.desc.inspect": "檢查中",
        "progress.done": "{desc}: [{n}/{total}] 完成",
        # ---- 去重 ----
        "dedupe.fallback": "  [去重] 同名副檔名優先級 [{priority}] 未覆蓋該組，回退兜底順序: {order}",
        "dedupe.reason": "同目錄同名，按 --ext-priority {priority} 保留 {name}",
        "dedupe.both_dirs": "  [去重] 偵測到雙目錄，保留 {dir}",
        # ---- 目录对齐 ----
        "align.drop": "  [提示] 目錄中 {count} 張圖片未被收集，已按 --drop-extra 放棄",
        "align.append": "  [提示] 目錄中 {count} 張圖片未被收集，已追加到末尾",
        # ---- 【转换】转换流程 ----
        "convert.skip_exists": "  [跳過] 目標已存在: {name}",
        "convert.overwrite": "  [覆寫] 已刪除舊檔，重新生成: {name}",
        "convert.spine": "  [排序] 按 OPF spine 順序（{count} 張圖片）",
        "convert.spine_empty": "  [排序] spine 提取為空，兜底按檔名排序（{count} 張）",
        "convert.dedup_physical": "  [去重] 跳過 {count} 個物理重複檔案（同一檔案重複出現，未寫入 CBZ）",
        "convert.no_opf": "  [排序] 未找到 OPF，兜底按檔名排序（{count} 張）",
        "convert.no_images": "  [失敗] 未找到圖片: {name}",
        "convert.drm_hint": "  [提示] 可能為 DRM 加密的 Kindle 漫畫，mobi 函式庫無法解密，請先去除 DRM 後再轉換",
        "convert.count_mismatch": "  [提示] 目錄共 {total} 張圖片，收集 {collected} 張，數量不一致",
        "convert.done": "  [完成] {name} ({count} 張圖片, {size} MB)",
        "convert.verify_fail": "  [校驗失敗] {name}: {msg}，已刪除壞檔",
        "convert.verify_ok": "  [校驗] {msg}",
        "convert.deleted_original": "  [清理] 已刪除原始檔案: {name}",
        "convert.error": "  [錯誤] {name}: {err}",
        "convert.error_drm_hint": "  [提示] 該檔案可能為 DRM 加密的 Kindle 漫畫，mobi 函式庫無法解密，請先去除 DRM 後再轉換",
        # ---- 【检查】校验（CBZ 完整性）----
        "verify.no_eocd": "缺少 EOCD 記錄（檔案不完整，可能被中斷）",
        "verify.bad_entry": "條目損壞: {name}",
        "verify.ok": "校驗通過（{count} 個條目）",
        "verify.badzip": "BadZipFile: {err}",
        "verify.exception": "校驗異常: {err}",
        # ---- 【预处理】预处理检查（大小/0字节/魔数）----
        "precheck.small": "檔案{size}位元組，低於最小限制{min}位元組",
        "precheck.zero": "檔案大小為 0 位元組",
        "precheck.too_small": "檔案過小（<68 位元組），疑似損壞或非電子書檔案",
        "precheck.magic": "檔頭校驗失敗（偏移 60 處無 BOOKMOBI 魔數），疑似損壞或非電子書檔案",
        "precheck.magic_warning": "  [警告] {name}: 檔頭校驗失敗（偏移 60 處無 BOOKMOBI 魔數），仍嘗試解包，解包失敗將計入失敗清單",
        "precheck.oserror": "無法讀取檔案（{err}）",
        # ---- 【检查】inspect 检查 ----
        "inspect.file_line": "[檔案] {name} ({size} MB)",
        "inspect.base_invalid_magic": "  基礎: 魔數非法（偏移 60 處無 BOOKMOBI） | --min-size 不會過濾",
        "inspect.base_reason": "  基礎: {reason}",
        "inspect.invalid_hint": "  提示: 疑似損壞或非電子書檔案，跳過解包",
        "inspect.base_magic_ok": "魔數合法",
        "inspect.drm_marked": "DRM: 有(檔頭標記)",
        "inspect.drm_unmarked": "DRM: 檔頭標記無",
        "inspect.below_min_size": "低於 --min-size({min})",
        "inspect.min_size_not_filter": "--min-size 不會過濾",
        "inspect.base_line": "  基礎: {parts}",
        "inspect.drm_hint": "  提示: 檔頭已標記 DRM 加密，跳過解包，轉換會失敗需先去除 DRM",
        "inspect.meta_title": "標題 {value}",
        "inspect.meta_author": "作者 {value}",
        "inspect.meta_language": "語言 {value}",
        "inspect.meta_publish_date": "出版日期 {value}",
        "inspect.meta_publisher": "出版社 {value}",
        "inspect.meta_isbn": "ISBN {value}",
        "inspect.meta_asin": "ASIN {value}",
        "inspect.meta_copyright": "版權 {value}",
        "inspect.meta_line": "  中繼資料: {parts}",
        "inspect.both_dirs": "  雙目錄標記: mobi7={mobi7} mobi8={mobi8}",
        "inspect.opf_exists": "  OPF檔案: 存在",
        "inspect.opf_missing": "  OPF檔案: 不存在",
        "inspect.spine_count": "  Spine 提取圖片: {count} 張",
        "inspect.ncx_count": "  目錄(NCX): {count} 個條目 | 預覽: {preview}",
        "inspect.ncx_missing": "  目錄(NCX): 未找到或解析失敗",
        "inspect.dir_images": "  目錄全部圖片: {count} 張",
        "inspect.drm_suspected": "  DRM: 疑似(檔頭標記無但圖片0張)",
        "inspect.cover_missing": "  封面檔案未找到",
        "inspect.fmt_none": "  圖片格式統計: 無圖片可統計",
        "inspect.drm_bad_hint": "  提示: 疑似 DRM 加密或內容損壞，轉換會失敗，需先去除 DRM",
        "inspect.drm_none": "  DRM: 無(檔頭標記無+圖片{count}張)",
        "inspect.cover_src_guide": "OPF guide 官方引用",
        "inspect.cover_src_filename": "檔名匹配",
        "inspect.cover_found": "  封面檔案已找到: {name}（{src}）",
        "inspect.fmt_stats": "  圖片格式統計: {parts}",
        "inspect.res_main_h": "主流高 {height} ({count}張, {pct}%)",
        "inspect.res_w_range": "寬 {min}~{max}",
        "inspect.res_main_w": "主流寬 {width} ({count}張, {pct}%)",
        "inspect.res_h_range": "高 {min}~{max}",
        "inspect.res_line": "  解析度: {parts}",
        "inspect.adv_png": "  建議: PNG 為主，建議 --compress 6~9，可顯著減小體積",
        "inspect.adv_jpeg": "  建議: JPEG 為主，--compress 收益有限，不建議開啟",
        "inspect.adv_mixed": "  建議: 混合格式，可試 --compress 6 對比體積",
        "inspect.unpack_fail": "  提示: 解包失敗（{err}）",
        "inspect_mode.precheck_header": "預處理跳過 {count} 個檔案（魔數非法/過小，不進入檢查）：",
        # ---- 【检查】inspect 模式 ----
        "inspect_mode.none": "無有效電子書檔案可檢查（全部被預處理過濾）",
        "inspect_mode.all": "檢查全部 {count} 個有效電子書檔案...\n",
        "inspect_mode.random": "隨機抽查 1/{total} 個檔案...\n",
        "inspect_mode.timeout": "  [逾時] {name}: 檢查超過 {seconds} 秒，已跳過（計入失敗）",
        "inspect_mode.timeout_residue": "  [提示] 檢查逾時，解壓臨時目錄可能殘留，請手動清理",
        "inspect_mode.ctrl_c": "\n偵測到 Ctrl+C，中斷檢查，輸出目前進度彙總：",
        "inspect_mode.random_note": "[檢查] 抽查 1/{total}（隨機），全部查看請加 --inspect-all",
        "inspect_mode.summary": "[檢查] 檢查完成: 共 {total} 個, 正常 {ok}, 魔數非法 {invalid}, DRM標記 {drm}, 疑似DRM/無圖 {noimg}, 解包逾時 {timeout}, 共耗時 {elapsed}s",
        # ---- 【汇总】主入口 ----
        "main.ctrl_c": "[提示] 使用者中斷（Ctrl+C），程式退出",
        "main.crash": "程式崩潰，堆疊資訊如下：",
        "run.auto_language": "已自動辨識語種為 {lang}",
        # ---- 【汇总】运行主流程（汇总统计）----
        "run.path_not_found": "路徑不存在: {path}",
        "run.no_ebooks": "未找到電子書檔案（.mobi/.azw/.azw3）: {path}",
        "run.precheck_header": "預處理跳過 {count} 個檔案：",
        "run.none_convertible": "無有效電子書檔案可轉換（全部被預處理過濾或同名去重）",
        "run.found": "找到 {total} 個有效電子書檔案（預處理過濾 {pre} 個，同名去重 {dedup} 個）\n",
        "run.dryrun_banner": "[試運行] --dry-run 模式：僅掃描與列印流程，不實際解壓打包、不建立輸出目錄",
        "dryrun.output_not_writable": "  [警告] 輸出目錄不可寫: {path}，正式轉換將失敗",
        "run.plan_output_dir": "計畫輸出目錄: {path}（僅正式轉換時自動建立）",
        "run.dryrun_precheck": "試運行預處理跳過 {count} 個檔案：",
        "run.dryrun_end": "試運行結束，未產生任何輸出檔案與資料夾",
        "run.start": "開始轉換 {count} 個檔案...\n",
        "run.timeout": "  [逾時] {name}: 轉換超過 {seconds} 秒，已跳過（計入失敗）",
        "run.elapsed": "  [耗時] {name}: {seconds} 秒",
        "run.ctrl_c": "\n偵測到 Ctrl+C，中斷轉換，輸出目前進度彙總：",
        "run.done": "\n轉換完成: {success}/{total} 成功",
        "run.interrupted_note": "（任務被中斷，以上為已處理部分的彙總，剩餘檔案未處理）",
        "run.stats": "轉換統計: 成功 {success} 個, 跳過 {skip} 個, 失敗 {fail} 個",
        "run.output_short": "輸出檔案: {count} 個（精簡彙總，不列出路徑）",
        "run.output_header": "輸出檔案:",
        "run.skipped_header": "跳過檔案（目標 cbz 已存在）: {count} 個",
        "run.failed_header": "失敗檔案: {count} 個",
        "run.total_elapsed": "總耗時: {seconds} 秒",
    "output.mode_preserve": "輸出模式: 保留相對子目錄結構 -> {dir}",
    "output.mode_flatten": "輸出模式: 平鋪（--flatten）-> {dir}",
    "output.renamed_due_to_conflict": "  [提示] 目標 {name} 已存在，已自動重新命名為 {new}",
    "output.flatten_requires_dir": "--flatten 需配合 --output-dir 使用，請同時指定輸出目錄",
    "error.flatten_without_output_dir": "--flatten 必須與 --output-dir 一起使用（無 --output-dir 時無法平鋪）",
    "rel_fallback": "  [警告] 無法計算 {name} 的相對子目錄路徑（可能跨磁碟），回退輸出到輸出目錄根下: {path}",
    },
    "en": {
        "error.missing_dependency": "[Fatal Error] Missing required dependency mobi. Install with:",
        "error.log_write_failed": "[Warning] Failed to write log ({err}), log file: {path}, further log entries will be skipped",
        "error.ext_priority_empty": "--ext-priority must not be empty",
        "error.ext_priority_invalid": "--ext-priority accepts only mobi/azw/azw3, got: {p}",
        # ---- --help 文案 ----
        "help.description": "Batch convert mobi/azw/azw3 ebooks to cbz",
        "help.language": "Output language: auto picks by system locale (zh prefix->Chinese, zh-TW/zh-Hant->Traditional Chinese, ja/Japanese->Japanese, otherwise->English), or choose zh-CN/zh-TW/ja/en explicitly",
        "help.target": "Path to an ebook file or a directory containing ebooks (.mobi/.azw/.azw3)",
        "help.delete": "Delete the original ebook file after successful conversion",
        "help.prefer": "Which directory to keep when both mobi7/mobi8 exist, default mobi8",
        "help.ext_priority": "When same-name files differ only by extension in the same directory, which format to keep: comma-separated, order is priority high->low, only mobi/azw/azw3 accepted, default azw3; falls back to azw3->mobi->azw when not covered; unrelated to --prefer (mobi7/mobi8 selection)",
        "help.drop_extra": "Drop extra images not collected from the directory (default: append them to the end of the cbz)",
        "help.overwrite": "Force regenerate when the target cbz already exists (default: skip)",
        "help.timeout": "Per-file conversion timeout in seconds; on timeout the file is skipped and counted as failed (default 600, 0 = no limit)",
        "help.min_size": "Filter out ebooks smaller than the given bytes; without a number defaults to 1000 bytes, 0 disables size filtering, omitted disables it",
        "help.output_dir": "Output CBZ to the given directory (auto-created); by default keeps the relative subdirectory structure of the input (e.g. One Piece/001.mobi -> DIR/One Piece/001.cbz), add --flatten to flatten into the root",
    "help.flatten": "Only with --output-dir: flatten all CBZ into the root of the output directory, auto-renaming conflicts as (2)(3)...; using it alone exits with an error",
        "help.dry_run": "Dry run: only scan files and print the conversion flow, without extracting, packing or creating output directories",
        "help.progress": "Force per-file progress bar (auto when TTY and >=2 files; when combined with --no-progress the last one wins)",
        "help.no_progress": "Force-disable the progress bar (even when TTY and >=2 files)",
        "help.quiet": "Quiet mode: only show errors and the final summary (log file unaffected)",
        "help.short_summary": "Compact summary: list counts instead of paths for succeeded/skipped files; failed files always show full paths",
        "help.compress": "zip compression level 0-9: 0=none (default, images already compressed), 1-9=deflate (helps for PNG sources, higher is smaller but slower)",
        "help.inspect": "Inspect mode: inspect the file directly when the positional argument is a single file, or randomly sample 1 ebook when it is a directory; unpack only to read internal info (metadata/structure/images/resolution/DRM) without generating CBZ, then auto-clean temp dirs",
        "help.inspect_all": "Inspect all ebooks (requires --inspect; using it alone will auto-enable --inspect)",
        "warn.inspect_all_auto_enable": "Note: --inspect-all automatically enabled --inspect",
        "help.no_comicinfo": "Do not generate ComicInfo.xml (default: write comic metadata into CBZ root)",
        "comicinfo.generating": "Generating ComicInfo.xml",
        "comicinfo.created": "ComicInfo.xml written",
        "comicinfo.disabled": "ComicInfo.xml disabled (--no-comicinfo)",
        "comicinfo.invalid": "ComicInfo.xml invalid or generation failed: {err}",
        "comicinfo.inferred": "inferred",
        "help.log": "Append all output to the given log file",
        # ---- 输出标签 ----
        "tag.info": "[Info]",
        "tag.fail": "[Failed]",
        "tag.error": "[Error]",
        "tag.skip": "[Skip]",
        "skip_entry": "[Skip] {path} ({reason})",
        "tag.overwrite": "[Overwrite]",
        "tag.clean": "[Clean]",
        "tag.sort": "[Sort]",
        "tag.dedup": "[Dedup]",
        "tag.done": "[Done]",
        "tag.verify": "[Verify]",
        "tag.verify_fail": "[Verify Failed]",
        "tag.timeout": "[Timeout]",
        "tag.elapsed": "[Elapsed]",
        "tag.file": "[File]",
        "tag.pending": "[Pending]",
        "tag.will_skip": "[Will Skip]",
        "tag.dryrun": "[Dry Run]",
        # ---- 进度条 ----
        "progress.desc.convert": "Converting",
        "progress.desc.dry_run": "Dry run",
        "progress.desc.inspect": "Inspecting",
        "progress.done": "{desc}: [{n}/{total}] done",
        # ---- 去重 ----
        "dedupe.fallback": "  [Dedup] Priority [{priority}] did not cover this group, falling back to default order: {order}",
        "dedupe.reason": "Same name in same directory, kept {name} per --ext-priority {priority}",
        "dedupe.both_dirs": "  [Dedup] Both directories detected, keeping {dir}",
        # ---- 目录对齐 ----
        "align.drop": "  [Info] {count} images in the directory were not collected, dropped per --drop-extra",
        "align.append": "  [Info] {count} images in the directory were not collected, appended to the end",
        # ---- 【转换】转换流程 ----
        "convert.skip_exists": "  [Skip] Target already exists: {name}",
        "convert.overwrite": "  [Overwrite] Deleted old file, regenerating: {name}",
        "convert.spine": "  [Sort] Using OPF spine order ({count} images)",
        "convert.spine_empty": "  [Sort] spine extraction empty, fell back to filename order ({count} images)",
        "convert.dedup_physical": "  [Dedup] Skipped {count} physically duplicate file(s) (same file appeared more than once, not written to CBZ)",
        "convert.no_opf": "  [Sort] No OPF found, fell back to filename order ({count} images)",
        "convert.no_images": "  [Failed] No images found: {name}",
        "convert.drm_hint": "  [Info] Possibly a DRM-protected Kindle comic; the mobi library cannot decrypt it. Remove DRM first and retry",
        "convert.count_mismatch": "  [Info] Directory has {total} images but {collected} were collected; count mismatch",
        "convert.done": "  [Done] {name} ({count} images, {size} MB)",
        "convert.verify_fail": "  [Verify Failed] {name}: {msg}; corrupted file deleted",
        "convert.verify_ok": "  [Verify] {msg}",
        "convert.deleted_original": "  [Clean] Deleted original file: {name}",
        "convert.error": "  [Error] {name}: {err}",
        "convert.error_drm_hint": "  [Info] This file may be a DRM-protected Kindle comic; the mobi library cannot decrypt it. Remove DRM first and retry",
        # ---- 【检查】校验（CBZ 完整性）----
        "verify.no_eocd": "Missing EOCD record (file incomplete, possibly interrupted)",
        "verify.bad_entry": "Corrupted entry: {name}",
        "verify.ok": "Verification passed ({count} entries)",
        "verify.badzip": "BadZipFile: {err}",
        "verify.exception": "Verification error: {err}",
        # ---- 【预处理】预处理检查（大小/0字节/魔数）----
        "precheck.small": "{size} bytes, below the minimum of {min} bytes",
        "precheck.zero": "File size is 0 bytes",
        "precheck.too_small": "File too small (<68 bytes), possibly corrupted or not an ebook",
        "precheck.magic": "Header check failed (no BOOKMOBI magic at offset 60), possibly corrupted or not an ebook",
        "precheck.magic_warning": "  [Warning] {name}: header check failed (no BOOKMOBI magic at offset 60), still attempting extraction; will count as failure if it fails",
        "precheck.oserror": "Cannot read file ({err})",
        # ---- 【检查】inspect 检查 ----
        "inspect.file_line": "[File] {name} ({size} MB)",
        "inspect.base_invalid_magic": "  Base: invalid magic (no BOOKMOBI at offset 60) | --min-size does not filter",
        "inspect.base_reason": "  Base: {reason}",
        "inspect.invalid_hint": "  Hint: possibly corrupted or not an ebook, skipping extraction",
        "inspect.base_magic_ok": "magic OK",
        "inspect.drm_marked": "DRM: yes (header flag)",
        "inspect.drm_unmarked": "DRM: no header flag",
        "inspect.below_min_size": "below --min-size({min})",
        "inspect.min_size_not_filter": "--min-size does not filter",
        "inspect.base_line": "  Base: {parts}",
        "inspect.drm_hint": "  Hint: header marks DRM encryption, skipping extraction; conversion would fail, remove DRM first",
        "inspect.meta_title": "Title {value}",
        "inspect.meta_author": "Author {value}",
        "inspect.meta_language": "Language {value}",
        "inspect.meta_publish_date": "Publish date {value}",
        "inspect.meta_publisher": "Publisher {value}",
        "inspect.meta_isbn": "ISBN {value}",
        "inspect.meta_asin": "ASIN {value}",
        "inspect.meta_copyright": "Copyright {value}",
        "inspect.meta_line": "  Metadata: {parts}",
        "inspect.both_dirs": "  Both-dir flags: mobi7={mobi7} mobi8={mobi8}",
        "inspect.opf_exists": "  OPF file: exists",
        "inspect.opf_missing": "  OPF file: missing",
        "inspect.spine_count": "  Spine images: {count}",
        "inspect.ncx_count": "  TOC (NCX): {count} entries | preview: {preview}",
        "inspect.ncx_missing": "  TOC (NCX): not found or parse failed",
        "inspect.dir_images": "  All images in directory: {count}",
        "inspect.drm_suspected": "  DRM: suspected (no header flag but 0 images)",
        "inspect.cover_missing": "  Cover image not found",
        "inspect.fmt_none": "  Image format stats: no images to count",
        "inspect.drm_bad_hint": "  Hint: suspected DRM encryption or corrupted content; conversion would fail, remove DRM first",
        "inspect.drm_none": "  DRM: none (no header flag, {count} images)",
        "inspect.cover_src_guide": "OPF guide reference",
        "inspect.cover_src_filename": "filename match",
        "inspect.cover_found": "  Cover image found: {name} ({src})",
        "inspect.fmt_stats": "  Image format stats: {parts}",
        "inspect.res_main_h": "main height {height} ({count} images, {pct}%)",
        "inspect.res_w_range": "width {min}~{max}",
        "inspect.res_main_w": "main width {width} ({count} images, {pct}%)",
        "inspect.res_h_range": "height {min}~{max}",
        "inspect.res_line": "  Resolution: {parts}",
        "inspect.adv_png": "  Advice: PNG-dominant, use --compress 6~9 to shrink significantly",
        "inspect.adv_jpeg": "  Advice: JPEG-dominant, --compress gains little, not recommended",
        "inspect.adv_mixed": "  Advice: mixed formats, try --compress 6 to compare sizes",
        "inspect.unpack_fail": "  Hint: extraction failed ({err})",
        "inspect_mode.precheck_header": "Precheck skipped {count} files (invalid magic/too small, not inspected):",
        # ---- 【检查】inspect 模式 ----
        "inspect_mode.none": "No valid ebook files to inspect (all filtered by precheck)",
        "inspect_mode.all": "Inspecting all {count} valid ebook files...\n",
        "inspect_mode.random": "Randomly inspecting 1/{total} file(s)...\n",
        "inspect_mode.timeout": "  [Timeout] {name}: inspection exceeded {seconds}s, skipped (counted as failed)",
        "inspect_mode.timeout_residue": "  [Hint] Inspection timed out; the extracted temp directory may be left behind, please clean it up manually",
        "inspect_mode.ctrl_c": "\nCtrl+C detected, inspection interrupted; showing current progress summary:",
        "inspect_mode.random_note": "[Inspect] Sampled 1/{total} (random); add --inspect-all to check all",
        "inspect_mode.summary": "[Inspect] Done: {total} files, ok {ok}, invalid magic {invalid}, DRM-flagged {drm}, suspected DRM/no image {noimg}, extraction timeout {timeout}, total {elapsed}s",
        # ---- 【汇总】主入口 ----
        "main.ctrl_c": "[Info] Interrupted by user (Ctrl+C), exiting",
        "main.crash": "Program crashed, stack trace:",
        "run.auto_language": "Auto-detected language: {lang}",
        # ---- 【汇总】运行主流程（汇总统计）----
        "run.path_not_found": "Path does not exist: {path}",
        "run.no_ebooks": "No ebook files (.mobi/.azw/.azw3) found: {path}",
        "run.precheck_header": "Precheck skipped {count} files:",
        "run.none_convertible": "No valid ebook files to convert (all filtered by precheck or dedup)",
        "run.found": "Found {total} valid ebook files (precheck filtered {pre}, dedup removed {dedup})\n",
        "run.dryrun_banner": "[Dry Run] --dry-run mode: scan and print flow only; no extraction, packing or output directories",
        "dryrun.output_not_writable": "  [Warning] Output directory is not writable: {path}; real conversion will fail",
        "run.plan_output_dir": "Planned output dir: {path} (auto-created only in real runs)",
        "run.dryrun_precheck": "Dry-run precheck skipped {count} files:",
        "run.dryrun_end": "Dry run finished, no output files or folders were created",
        "run.start": "Converting {count} files...\n",
        "run.timeout": "  [Timeout] {name}: conversion exceeded {seconds}s, skipped (counted as failed)",
        "run.elapsed": "  [Elapsed] {name}: {seconds} s",
        "run.ctrl_c": "\nCtrl+C detected, conversion interrupted; showing current progress summary:",
        "run.done": "\nConversion complete: {success}/{total} succeeded",
        "run.interrupted_note": "(Task interrupted; summary above covers processed files only, the rest were not handled)",
        "run.stats": "Statistics: {success} succeeded, {skip} skipped, {fail} failed",
        "run.output_short": "Output files: {count} (compact summary, paths omitted)",
        "run.output_header": "Output files:",
        "run.skipped_header": "Skipped files (target cbz exists): {count}",
        "run.failed_header": "Failed files: {count}",
        "run.total_elapsed": "Total time: {seconds} s",
    "output.mode_preserve": "Output mode: preserving relative subdirectories -> {dir}",
    "output.mode_flatten": "Output mode: flatten (--flatten) -> {dir}",
    "output.renamed_due_to_conflict": "  [Info] Target {name} already exists, renamed to {new}",
    "output.flatten_requires_dir": "--flatten requires --output-dir; please specify an output directory too",
    "error.flatten_without_output_dir": "--flatten must be used together with --output-dir (cannot flatten without an output directory)",
    "rel_fallback": "  [Warning] Cannot compute relative subdirectory path for {name} (possibly crossing drives), falling back to the root of the output directory: {path}",
    },
    "ja": {
        "error.missing_dependency": '【致命的エラー】必須依存ライブラリ mobi がありません。インストールを実行してください：',
        "error.log_write_failed": '【警告】ログの書き込みに失敗しました（{err}）、ログファイル: {path}、以降のログは書き込みません',
        "error.ext_priority_empty": "--ext-priority を空にすることはできません",
        "error.ext_priority_invalid": "--ext-priority は mobi/azw/azw3 のみ受け付けます。受信: {p}",
        # ---- --help 文案 ----
        "help.description": 'mobi/azw/azw3 漫画を一括で cbz に変換',
        "help.language": '出力言語：auto はシステム言語で自動判定（zh プレフィックス→中国語、zh-TW/zh-Hant→繁体字中国語、ja/Japanese→日本語、それ以外→英語）、または zh-CN/zh-TW/ja/en を指定',
        "help.target": '電子書籍ファイルのパス、または電子書籍（.mobi/.azw/.azw3）を含むディレクトリ',
        "help.delete": '変換成功後に元の電子書籍ファイルを削除',
        "help.prefer": '二重ディレクトリ mobi（mobi7/mobi8）がある場合にどちらを残すか、デフォルトは mobi8',
        "help.ext_priority": '同じディレクトリで同名（拡張子のみ異なる）の場合にどの形式を残すか：カンマ区切り、順序が優先度（高→低）、mobi/azw/azw3 のみ指定可能、デフォルト azw3；優先度がカバーしない場合は azw3→mobi→azw にフォールバック；--prefer（二重ディレクトリ選択）とは無関係',
        "help.drop_extra": 'ディレクトリ内で収集されなかった余分な画像を追加しない（デフォルトは cbz 末尾に追加）',
        "help.overwrite": '対象 cbz が既に存在する場合に強制的に再生成（デフォルトはスキップ）',
        "help.timeout": 'ファイルごとの変換タイムアウト秒数。タイムアウトで自動スキップし失敗に計上（デフォルト 600、0 は制限なし）',
        "help.min_size": '指定バイト数未満の電子書籍を除外；数字なしでデフォルト 1000 バイト、0 でサイズフィルタ無効、未指定で無効',
        "help.output_dir": "CBZ を指定ディレクトリに出力（自動作成）、デフォルトでは入力の相対サブディレクトリ構造を保持（例: One Piece/001.mobi → DIR/One Piece/001.cbz）、--flatten でルートにフラット化",
    "help.flatten": "--output-dir との併用時のみ：全 CBZ を出力ディレクトリのルートにフラット化、重複は自動で (2)(3)… にリネーム；単独使用はエラー終了",
        "help.dry_run": '試運転：ファイルをスキャンして変換フローを表示するだけで、解凍・パッキング・出力ディレクトリ作成は行わない',
        "help.progress": 'ファイル別プログレスバーを強制表示（デフォルトは TTY かつファイル数≥2 で自動表示；--no-progress と同時指定時は最後のパラメータが優先）',
        "help.no_progress": 'プログレスバーを強制オフ（TTY かつファイル数≥2 でも）',
        "help.quiet": '静音モード：エラーと最終サマリーのみ表示（ログファイルには影響なし）',
        "help.short_summary": '簡潔サマリー：成功/スキップのファイルはパスを列挙せず数のみ表示、失敗ファイルは常にフルパス表示',
        "help.compress": 'zip 圧縮レベル 0-9：0=無圧縮（デフォルト、画像は既に圧縮済み）、1-9=deflate 圧縮（PNG 元で効果あり、レベルが高いほど小さく遅い）',
        "help.inspect": '検査モード：位置引数が単一ファイルの場合はそのファイルを直接検査し、ディレクトリの場合はランダムに 1 冊を抽出して、解凍して内部情報（メタデータ/構造/画像/解像度/DRM）を読み取るだけで、CBZ は生成せず、終了後に一時ディレクトリを自動削除',
        "help.inspect_all": '全電子書籍を検査（--inspect と併用必須、単独指定時は自動的に --inspect を有効化）',
        "warn.inspect_all_auto_enable": '注意: --inspect-all により --inspect が自動的に有効化されました',
        "help.no_comicinfo": "ComicInfo.xml を生成しない（既定: CBZ ルートに漫画メタデータを書き込む）",
        "comicinfo.generating": "ComicInfo.xml を生成中",
        "comicinfo.created": "ComicInfo.xml を書き込みました",
        "comicinfo.disabled": "ComicInfo.xml は無効です（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml が無効、または生成に失敗しました: {err}",
        "comicinfo.inferred": "推定",
        "help.log": 'すべての出力を指定ログファイルに追記',
        # ---- 输出标签 ----
        "tag.info": '[情報]',
        "tag.fail": '[失敗]',
        "tag.error": '[エラー]',
        "tag.skip": '[スキップ]',
        "skip_entry": '[スキップ] {path}（{reason}）',
        "tag.overwrite": '[上書き]',
        "tag.clean": '[クリーンアップ]',
        "tag.sort": '[ソート]',
        "tag.dedup": '[重複除去]',
        "tag.done": '[完了]',
        "tag.verify": '[検証]',
        "tag.verify_fail": '[検証失敗]',
        "tag.timeout": '[タイムアウト]',
        "tag.elapsed": '[経過時間]',
        "tag.file": '[ファイル]',
        "tag.pending": '[変換待ち]',
        "tag.will_skip": '[スキップ予定]',
        "tag.dryrun": '[試運転]',
        # ---- 进度条 ----
        "progress.desc.convert": '変換中',
        "progress.desc.dry_run": '試運転',
        "progress.desc.inspect": '検査中',
        "progress.done": '{desc}: [{n}/{total}] 完了',
        # ---- 去重 ----
        "dedupe.fallback": '  [重複除去] 拡張子優先度 [{priority}] がこのグループをカバーしていないため、フォールバック順に戻ります: {order}',
        "dedupe.reason": '同じディレクトリで同名のため、--ext-priority {priority} に従い {name} を保持',
        "dedupe.both_dirs": '  [重複除去] 二重ディレクトリを検出、{dir} を保持',
        # ---- 目录对齐 ----
        "align.drop": '  [情報] ディレクトリ内の未収集画像 {count} 枚を --drop-extra により破棄',
        "align.append": '  [情報] ディレクトリ内の未収集画像 {count} 枚を末尾に追加',
        # ---- 【转换】转换流程 ----
        "convert.skip_exists": '  [スキップ] 対象は既に存在: {name}',
        "convert.overwrite": '  [上書き] 古いファイルを削除し再生成: {name}',
        "convert.spine": '  [ソート] OPF spine 順に抽出（{count} 枚）',
        "convert.spine_empty": '  [ソート] spine 抽出が空のため、ファイル名順にフォールバック（{count} 枚）',
        "convert.dedup_physical": '  [重複排除] 物理的に重複する {count} ファイルをスキップ（同一ファイルが重複出現、CBZ に書き込みません）',
        "convert.no_opf": '  [ソート] OPF が見つからないため、ファイル名順にフォールバック（{count} 枚）',
        "convert.no_images": '  [失敗] 画像が見つかりません: {name}',
        "convert.drm_hint": '  [情報] DRM 暗号化された Kindle 漫画の可能性があります。mobi ライブラリでは復号できないため、DRM を除去してから再変換してください',
        "convert.count_mismatch": '  [情報] ディレクトリ内の画像は {total} 枚、収集は {collected} 枚で不一致',
        "convert.done": '  [完了] {name} ({count} 枚の画像, {size} MB)',
        "convert.verify_fail": '  [検証失敗] {name}: {msg}、壊れたファイルを削除しました',
        "convert.verify_ok": '  [検証] {msg}',
        "convert.deleted_original": '  [クリーンアップ] 元ファイルを削除しました: {name}',
        "convert.error": '  [エラー] {name}: {err}',
        "convert.error_drm_hint": '  [情報] このファイルは DRM 暗号化された Kindle 漫画の可能性があります。mobi ライブラリでは復号できないため、DRM を除去してから再変換してください',
        # ---- 【检查】校验（CBZ 完整性）----
        "verify.no_eocd": 'EOCD レコードがありません（ファイルが不完全、中断された可能性）',
        "verify.bad_entry": 'エントリが破損: {name}',
        "verify.ok": '検証パス（{count} エントリ）',
        "verify.badzip": 'BadZipFile: {err}',
        "verify.exception": '検証エラー: {err}',
        # ---- 【预处理】预处理检查（大小/0字节/魔数）----
        "precheck.small": 'ファイルは {size} バイトで、最小制限 {min} バイト未満',
        "precheck.zero": 'ファイルサイズが 0 バイト',
        "precheck.too_small": 'ファイルが小さすぎます（<68 バイト）、破損または電子書籍以外の可能性',
        "precheck.magic": 'ファイルヘッダー検証に失敗（オフセット 60 に BOOKMOBI マジックなし）、破損または電子書籍以外の可能性',
        "precheck.magic_warning": "  [警告] {name}: ファイルヘッダー検証に失敗（オフセット 60 に BOOKMOBI マジックなし）、それでも解包を試みます。解包に失敗した場合は失敗リストに計上されます",
        "precheck.oserror": 'ファイルを読み取れません（{err}）',
        # ---- 【检查】inspect 检查 ----
        "inspect.file_line": '[ファイル] {name} ({size} MB)',
        "inspect.base_invalid_magic": '  基本: マジック不正（オフセット 60 に BOOKMOBI なし） | --min-size では除外されません',
        "inspect.base_reason": '  基本: {reason}',
        "inspect.invalid_hint": '  ヒント: 破損または電子書籍以外の可能性があるため、解凍をスキップ',
        "inspect.base_magic_ok": 'マジック正常',
        "inspect.drm_marked": 'DRM: あり（ヘッダーフラグ）',
        "inspect.drm_unmarked": 'DRM: ヘッダーフラグなし',
        "inspect.below_min_size": '--min-size({min}) 未満',
        "inspect.min_size_not_filter": '--min-size では除外されません',
        "inspect.base_line": '  基本: {parts}',
        "inspect.drm_hint": '  ヒント: ヘッダーに DRM 暗号化のマークあり、解凍をスキップ。変換は失敗するため先に DRM を除去してください',
        "inspect.meta_title": 'タイトル {value}',
        "inspect.meta_author": '著者 {value}',
        "inspect.meta_language": '言語 {value}',
        "inspect.meta_publish_date": '出版日 {value}',
        "inspect.meta_publisher": '出版社 {value}',
        "inspect.meta_isbn": 'ISBN {value}',
        "inspect.meta_asin": 'ASIN {value}',
        "inspect.meta_copyright": '著作権 {value}',
        "inspect.meta_line": '  メタデータ: {parts}',
        "inspect.both_dirs": '  二重ディレクトリフラグ: mobi7={mobi7} mobi8={mobi8}',
        "inspect.opf_exists": '  OPF ファイル: あり',
        "inspect.opf_missing": '  OPF ファイル: なし',
        "inspect.spine_count": '  Spine 抽出画像: {count} 枚',
        "inspect.ncx_count": '  目次(NCX): {count} エントリ | プレビュー: {preview}',
        "inspect.ncx_missing": '  目次(NCX): 見つからないか解析失敗',
        "inspect.dir_images": '  ディレクトリ内の全画像: {count} 枚',
        "inspect.drm_suspected": '  DRM: 疑いあり（ヘッダーフラグなし、画像 0 枚）',
        "inspect.cover_missing": '  カバー画像が見つかりません',
        "inspect.fmt_none": '  画像形式統計: 集計できる画像なし',
        "inspect.drm_bad_hint": '  ヒント: DRM 暗号化または内容破損の疑い。変換は失敗するため先に DRM を除去してください',
        "inspect.drm_none": '  DRM: なし（ヘッダーフラグなし、画像 {count} 枚）',
        "inspect.cover_src_guide": 'OPF guide 公式参照',
        "inspect.cover_src_filename": 'ファイル名一致',
        "inspect.cover_found": '  カバー画像が見つかりました: {name}（{src}）',
        "inspect.fmt_stats": '  画像形式統計: {parts}',
        "inspect.res_main_h": '主な高さ {height} ({count}枚, {pct}%)',
        "inspect.res_w_range": '幅 {min}~{max}',
        "inspect.res_main_w": '主な幅 {width} ({count}枚, {pct}%)',
        "inspect.res_h_range": '高さ {min}~{max}',
        "inspect.res_line": '  解像度: {parts}',
        "inspect.adv_png": '  提案: PNG が中心なので --compress 6~9 で大幅に縮小できます',
        "inspect.adv_jpeg": '  提案: JPEG が中心なので --compress の効果は限定的、非推奨',
        "inspect.adv_mixed": '  提案: 混在形式、--compress 6 でサイズを比較してみてください',
        "inspect.unpack_fail": '  ヒント: 解凍に失敗しました（{err}）',
        "inspect_mode.precheck_header": 'プリチェックで {count} ファイルをスキップ（マジック不正/小さすぎ、検査対象外）：',
        # ---- 【检查】inspect 模式 ----
        "inspect_mode.none": '検査できる有効な電子書籍ファイルがありません（すべてプリチェックで除外）',
        "inspect_mode.all": '全 {count} ファイルの有効な電子書籍を検査しています...\n',
        "inspect_mode.random": '1/{total} ファイルをランダムに検査しています...\n',
        "inspect_mode.timeout": '  [タイムアウト] {name}: 検査が {seconds} 秒を超えたためスキップ（失敗に計上）',
        "inspect_mode.timeout_residue": '  [ヒント] 検査がタイムアウトしました。展開された一時ディレクトリが残っている可能性があります。手動でクリーンアップしてください',
        "inspect_mode.ctrl_c": '\nCtrl+C を検出、検査を中断し現在の進捗サマリーを表示：',
        "inspect_mode.random_note": '[検査] 1/{total} をサンプリング（ランダム）、全件は --inspect-all を追加',
        "inspect_mode.summary": '[検査] 検査完了: 計 {total} 件, 正常 {ok}, マジック不正 {invalid}, DRM マーク {drm}, DRM 疑い/画像なし {noimg}, 解凍タイムアウト {timeout}, 合計 {elapsed}s',
        # ---- 【汇总】主入口 ----
        "main.ctrl_c": '[情報] ユーザーによる中断（Ctrl+C）、終了します',
        "main.crash": 'プログラムがクラッシュしました。スタックトレース：',
        "run.auto_language": "言語を自動検出しました: {lang}",
        # ---- 【汇总】运行主流程（汇总统计）----
        "run.path_not_found": 'パスが存在しません: {path}',
        "run.no_ebooks": '電子書籍ファイル（.mobi/.azw/.azw3）が見つかりません: {path}',
        "run.precheck_header": 'プリチェックで {count} ファイルをスキップ：',
        "run.none_convertible": '変換できる有効な電子書籍ファイルがありません（すべてプリチェックまたは同名重複で除外）',
        "run.found": '有効な電子書籍 {total} ファイルを検出（プリチェックで {pre} 除外、同名重複で {dedup} 除外）\n',
        "run.dryrun_banner": '[試運転] --dry-run モード：スキャンしてフローを表示するのみ。解凍・パッキング・出力ディレクトリ作成は行いません',
        "dryrun.output_not_writable": '  [警告] 出力ディレクトリが書き込み不可です: {path}。正式な変換は失敗します',
        "run.plan_output_dir": '出力予定ディレクトリ: {path}（正式変換時のみ自動作成）',
        "run.dryrun_precheck": '試運転でプリチェックにより {count} ファイルをスキップ：',
        "run.dryrun_end": '試運転終了。出力ファイルやフォルダは作成されませんでした',
        "run.start": '{count} ファイルの変換を開始...\n',
        "run.timeout": '  [タイムアウト] {name}: 変換が {seconds} 秒を超えたためスキップ（失敗に計上）',
        "run.elapsed": '  [経過時間] {name}: {seconds} 秒',
        "run.ctrl_c": '\nCtrl+C を検出、変換を中断し現在の進捗サマリーを表示：',
        "run.done": '\n変換完了: {success}/{total} 成功',
        "run.interrupted_note": '（タスクは中断されました。上記は処理済み部分のサマリーで、残りは未処理です）',
        "run.stats": '変換統計: 成功 {success} 件, スキップ {skip} 件, 失敗 {fail} 件',
        "run.output_short": '出力ファイル: {count} 件（簡潔サマリー、パスは省略）',
        "run.output_header": '出力ファイル:',
        "run.skipped_header": 'スキップファイル（対象 cbz が既に存在）: {count} 件',
        "run.failed_header": '失敗ファイル: {count} 件',
        "run.total_elapsed": '合計時間: {seconds} 秒',
    "output.mode_preserve": "出力モード: 相対サブディレクトリ構造を保持 -> {dir}",
    "output.mode_flatten": "出力モード: フラット化（--flatten）-> {dir}",
    "output.renamed_due_to_conflict": "  [情報] 対象 {name} は既に存在するため {new} に自動リネームしました",
    "output.flatten_requires_dir": "--flatten は --output-dir と併用してください。出力ディレクトリも指定してください",
    "error.flatten_without_output_dir": "--flatten は --output-dir と一緒に使用する必要があります（出力ディレクトリなしではフラット化できません）",
    "rel_fallback": "  [警告] {name} の相対サブディレクトリパスを計算できません（ドライブをまたいでいる可能性）。出力ディレクトリのルートにフォールバックします: {path}",
    },
}

CURRENT_LANGUAGE = "zh-CN"


def _auto_language() -> str:
    """按系统 locale 判定语言：简体中文归 zh-CN、繁体中文归 zh-TW、日文归 ja、其余归 en"""
    code = None
    try:
        locale.setlocale(locale.LC_ALL, "")
        code, _ = locale.getlocale()
    except Exception:
        code = None
    if not code:
        try:
            code = locale.getdefaultlocale()[0]
        except Exception:
            code = None
    if not code:
        return "en"
    lc = code.replace("-", "_").lower()
    # Windows 上 locale 名称常为英文（如 Chinese (Simplified)_China.936）
    if "chinese" in lc:
        if any(m in lc for m in ("traditional", "taiwan", "hong", "macau")):
            return "zh-TW"
        return "zh-CN"
    if "japanese" in lc:
        return "ja"
    if not lc.startswith("zh") and not lc.startswith("ja"):
        return "en"
    if lc.startswith("zh"):
        for marker in ("tw", "hk", "mo", "hant"):
            if marker in lc:
                return "zh-TW"
        return "zh-CN"
    return "ja"


def set_language(lang: str) -> None:
    """设置当前语言；auto 按系统 locale 判定，未知语言回退 en"""
    global CURRENT_LANGUAGE
    if lang == "auto":
        lang = _auto_language()
    if lang not in LANGUAGES:
        lang = "en"
    CURRENT_LANGUAGE = lang


def t(key: str, **kwargs) -> str:
    """取当前语言文案：缺键回退 en，再缺失回退 [{key}]，不抛异常中断转换"""
    table = LANGUAGES.get(CURRENT_LANGUAGE, {})
    if key not in table:
        table = LANGUAGES.get("en", {})
    if key not in table:
        return "[%s]" % key
    tmpl = table[key]
    if not kwargs:
        return tmpl
    try:
        return tmpl.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return tmpl


# 全局前置依赖检测，启动即校验，无需等到循环文件
try:
    import mobi
except ImportError:
    set_language("auto")
    print(t("error.missing_dependency"))
    print("    pip install mobi")
    sys.exit(1)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif"}
EOCD_SIGNATURE = b"\x50\x4b\x05\x06"  # End of Central Directory 签名
OPF_NS = {"opf": "http://www.idpf.org/2007/opf"}

# 支持的电子书输入扩展名（大小写不敏感）；同名去重未覆盖时的兜底优先级
SUPPORTED_INPUT_EXTENSIONS = {".mobi", ".azw", ".azw3"}
KEEP_EXT_ORDER = (".azw3", ".mobi", ".azw")  # --ext-priority 未覆盖时的兜底顺序


def parse_ext_priority(value: str) -> list[str]:
    """解析 --ext-priority：逗号分隔、仅接受 mobi/azw/azw3、顺序即优先级（高→低）。

    输入：命令行传入的原始字符串（如 "azw3,mobi"）。
    输出：规范化后的扩展名优先级列表（如 ["azw3", "mobi"]）；
    为空或含非法扩展名时抛 argparse.ArgumentTypeError（文案经 t() 多语言化）。
    """
    parts = [p.strip().lower() for p in value.split(",") if p.strip()]
    if not parts:
        raise argparse.ArgumentTypeError(t("error.ext_priority_empty"))
    for p in parts:
        if p not in ("mobi", "azw", "azw3"):
            raise argparse.ArgumentTypeError(t("error.ext_priority_invalid", p=p))
    return parts



class ConvStatus(str, Enum):
    """ebook_to_cbz 返回状态枚举，替代魔法字符串 ok/skip/fail，减少拼写错误"""
    OK = "ok"
    SKIP = "skip"
    FAIL = "fail"


# 输出标签不再定义常量，统一经 t("tag.xxx") 获取（多语言文案表在顶部 LANGUAGES）


def norm_path(p: Path) -> str:
    """路径归一化：resolve 后转小写，兼容 Windows 不区分大小写的文件系统，
    避免同名仅大小写差异的文件在对比时被误判为不同/重复。"""
    return str(p.resolve()).lower()


    # 输入：目标函数 func、超时秒数 timeout 及透传参数；输出：(timed_out, result) 二元组：
    # 超时 → (True, None)，正常 → (False, func 的返回值)
def run_with_timeout(func, timeout: float, *args, **kwargs):
    """在单线程池中执行 func；返回 (timed_out, result) 二元组：
    超时 → (True, None)，正常 → (False, func 的返回值)。

    timeout <= 0 时不限制，直接在当前线程执行。

    注意：Python 线程无法强制杀死阻塞任务，超时后 mobi.extract 的工作线程
    会后台残留，持续占用内存 / IO；批量大量损坏文件时可能堆积后台僵尸线程，
    无法真正终止。若需彻底隔离卡死任务，可改用 multiprocessing 实现可终止
    子进程，但会增加跨平台兼容复杂度，暂未采用。"""
    if timeout <= 0:
        return False, func(*args, **kwargs)
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(func, *args, **kwargs)
    try:
        return False, future.result(timeout=timeout)
    except TimeoutError:
        return True, None
    finally:
        # wait=False：不等待可能永久阻塞的工作线程
        executor.shutdown(wait=False)

# 全局输出控制：--quiet 抑制 info 输出，--log 将输出同时写入文件，
# --short-summary 精简汇总（不逐条罗列成功/跳过文件路径），
# --compress 设置 zip 压缩级别（0=不压缩，1-9=deflate）
_quiet_mode = False
_log_path = None
_log_write_failed = False
_short_summary = False
_compress_level = 0


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
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + t("error.log_write_failed", err=e, path=_log_path))
    if not _quiet_mode or level in ("summary", "error"):
        print(line)


def truncate_name(name: str, max_len: int = 40) -> str:
    """截断文件名用于进度条展示：超过 max_len 时保留尾部、前缀省略号"""
    if len(name) <= max_len:
        return name
    return "..." + name[-(max_len - 3):]


def should_show_progress(args, final_files: list) -> bool:
    """进度条显示策略：
    --no-progress 强制关闭（与 --progress 同传时已在主流程按最后出现者修正）；
    --progress 强制开启（非 TTY 也显示）；
    否则自动判断：stderr 为 TTY 且有效文件数 >= 2。
    """
    if args.no_progress:
        return False
    if args.progress:
        return True
    return sys.stderr.isatty() and len(final_files) >= 2


class _SimpleProgress:
    """tqdm 缺失时的降级进度：简单文本 [i/N] 输出到 stderr，不崩溃"""

    def __init__(self, total: int, desc: str):
        self.total = total
        self.n = 0
        self.desc = desc
        self._name = ""

    def set_postfix_str(self, s: str) -> None:
        self._name = s

    def update(self, n: int = 1) -> None:
        self.n += n
        sys.stderr.write(f"{self.desc}: [{self.n}/{self.total}] {self._name}\n")

    def close(self) -> None:
        sys.stderr.write(t("progress.done", desc=self.desc, n=self.n, total=self.total) + "\n")


def create_progress(total: int, desc: str):
    """创建进度条对象：优先 tqdm（可选依赖），缺失时降级为简单文本进度"""
    try:
        from tqdm import tqdm
        return tqdm(
            total=total, desc=desc, file=sys.stderr, disable=False,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
        )
    except Exception:
        return _SimpleProgress(total, desc)


def create_progress_if_needed(args, final_files: list, desc: str):
    """按策略创建进度条；不需要时返回 None（total 严格等于去重后最终列表长度）"""
    if not should_show_progress(args, final_files):
        return None
    return create_progress(len(final_files), desc)


def natural_key(p: Path) -> list:
    """自然排序键：让 2.jpg 排在 10.jpg 前面"""
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r"(\d+)", p.name)]


    # 输入：cbz 文件路径；输出：(是否通过完整性校验, 校验结果消息)
def validate_cbz(cbz_path: Path, require_comicinfo: bool = False) -> tuple[bool, str]:
    """校验 cbz 文件完整性：检查 EOCD 记录存在且所有条目可正常读取。

    require_comicinfo=True 时追加 3 项 ComicInfo 校验：ComicInfo.xml
    存在、可被标准 XML parser 解析、根节点为 ComicInfo。
    """
    try:
        data = cbz_path.read_bytes()[-70000:]  # EOCD 在文件末尾，读尾部足够
        if EOCD_SIGNATURE not in data:
            return False, t("verify.no_eocd")
        with zipfile.ZipFile(str(cbz_path)) as zf:
            bad = zf.testzip()
            if bad is not None:
                return False, t("verify.bad_entry", name=bad)
            if require_comicinfo:
                if "ComicInfo.xml" not in zf.namelist():
                    return False, t("comicinfo.invalid", err="missing")
                try:
                    parsed = ET.fromstring(zf.read("ComicInfo.xml"))
                except Exception as e:
                    return False, t("comicinfo.invalid", err=e)
                if parsed.tag.split("}")[-1] != "ComicInfo":
                    return False, t("comicinfo.invalid", err=f"root={parsed.tag}")
            count = len(zf.namelist())
            return True, t("verify.ok", count=count)
    except zipfile.BadZipFile as e:
        return False, t("verify.badzip", err=e)
    except Exception as e:
        return False, t("verify.exception", err=e)


    # 输入：目录或文件路径 target；输出：待转换的电子书文件路径列表（按路径排序保证顺序可预测）
def collect_ebook_files(target: Path) -> list[Path]:
    """收集所有待转换的电子书文件（.mobi/.azw/.azw3），按路径排序保证处理顺序可预测"""
    if target.is_file():
        if target.suffix.lower() in SUPPORTED_INPUT_EXTENSIONS:
            return [target]
        return []
    ebook_files = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if Path(f).suffix.lower() in SUPPORTED_INPUT_EXTENSIONS:
                ebook_files.append(Path(root) / f)
    return sorted(ebook_files)


def precheck_ebook(p: Path, min_bytes: int) -> str | None:
    """预处理检查电子书文件（.mobi/.azw/.azw3），返回跳过原因；正常返回 None。

    检查项：
    - 大小下限：min_bytes > 0 时，小于该字节数的文件直接跳过
      （默认 1000 字节；合法电子书体积远大于此，可兜住头部恰好完整
      但内容被截断的边缘损坏样本；0 表示关闭大小过滤）
    - 文件大小为 0 字节：直接跳过
    - 文件头校验：标准电子书（MOBI/AZW/AZW3 均基于 PalmDB 容器）在偏移
      60 处有 8 字节魔数 "BOOKMOBI"。文件过小或魔数不匹配时仅输出
      warning 提示、不再直接判为损坏跳过，仍交给转换阶段尝试解包
      （mobi.extract 内部自带二次校验，解包失败会正常计入失败列表）
    （文件头正常但内容深层损坏的，仍会在转换阶段解压失败并计入失败列表）
    """
    try:
        size = p.stat().st_size
        if min_bytes > 0 and size < min_bytes:
            return t("precheck.small", size=size, min=min_bytes)
        if size == 0:
            return t("precheck.zero")
        if size < 68:
            return t("precheck.too_small")
        with open(p, "rb") as f:
            f.seek(60)
            magic = f.read(8)
        if magic != b"BOOKMOBI":
            # 降级策略：魔数失败不再判损坏跳过，warning 提示后仍尝试解包
            emit(t("precheck.magic_warning", name=p.name), level="warning")
        return None
    except OSError as e:
        return t("precheck.oserror", err=e)


    # 输入：文件路径列表与扩展名优先级（高→低）；输出：(保留列表, [(被跳过的路径, 原因)])
def dedupe_ebook_files(files: list[Path], ext_priority: list[str]) -> tuple[list[Path], list[tuple[Path, str]]]:
    """同目录同主文件名（仅扩展名不同）去重：按 --ext-priority 保留一份。

    分组键：(parent.resolve(), stem.lower())，不同目录的同名文件不去重。
    ext_priority: 用户指定优先级（高→低），如 ["azw3"] 或 ["azw3", "mobi"]；
      组内按此顺序取第一个命中；全部未命中时输出提示并回退兜底顺序
      KEEP_EXT_ORDER（azw3→mobi→azw）。
    返回 (kept, skipped)：skipped 为 [(path, reason)]。
    """
    groups: dict[tuple, list[Path]] = {}
    for p in files:
        groups.setdefault((p.parent.resolve(), p.stem.lower()), []).append(p)

    priority_exts = [f".{e.lstrip('.')}" for e in ext_priority]
    priority_desc = " > ".join(ext_priority)
    kept: list[Path] = []
    skipped: list[tuple[Path, str]] = []

    for key, group in groups.items():
        if len(group) == 1:
            kept.append(group[0])
            continue
        chosen = None
        for ext in priority_exts:
            for p in group:
                if p.suffix.lower() == ext:
                    chosen = p
                    break
            if chosen is not None:
                break
        if chosen is None:
            emit(t("dedupe.fallback", priority=priority_desc, order=" > ".join(e.lstrip(".") for e in KEEP_EXT_ORDER)), level="summary")
            for ext in KEEP_EXT_ORDER:
                for p in group:
                    if p.suffix.lower() == ext:
                        chosen = p
                        break
                if chosen is not None:
                    break
        if chosen is None:
            chosen = group[0]
        for p in group:
            if p == chosen:
                continue
            reason = t("dedupe.reason", priority=priority_desc, name=chosen.name)
            skipped.append((p, reason))
            emit("  " + t("skip_entry", path=str(p), reason=reason), level="summary")
        kept.append(chosen)
    return kept, skipped


    # 输入：源电子书路径、输出目录、是否平铺、相对基准与已占用名集合；输出：目标 cbz 绝对路径
def sanitize_filename_component(name: str) -> str:
    """替换 Windows 文件名非法字符（<>:"/\|?*）为下划线，保证平铺文件名可写"""
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def flat_base_name(ebook_path: Path, input_root: Path | None) -> str:
    """平铺基础文件名：relative 仅一层 → stem；两层及以上 → 「父目录名 - stem」。

    非法文件名字符替换为 _；input_root 为 None 或相对计算失败时回退仅用 stem。"""
    stem = ebook_path.stem
    if input_root is not None:
        try:
            rel = ebook_path.relative_to(input_root)
            parts = list(rel.parts)
            if len(parts) >= 2:
                return sanitize_filename_component(f"{parts[-2]} - {stem}")
        except ValueError:
            pass
    return sanitize_filename_component(stem)


def unique_path(output_dir: Path, base: str, used: set) -> Path:
    """平铺唯一化：base.cbz 已被占用时依次尝试 base (2).cbz、base (3).cbz…

    used 记录本次任务已占用的字符串路径（按处理顺序），与磁盘 exists 检查
    配合，保证 dry-run 模拟与正式运行一致。"""
    candidate = output_dir / (base + ".cbz")
    n = 2
    while candidate.exists() or str(candidate) in used:
        candidate = output_dir / f"{base} ({n}).cbz"
        n += 1
    return candidate


def target_cbz_path(ebook_path: Path, output_dir: Path | None, flatten: bool = False, input_root: Path | None = None, used_names: set | None = None) -> Path:
    """计算目标 cbz 路径。

    - output_dir 为 None：与源电子书同目录（历史行为）
    - output_dir + flatten=False：保留相对 input_root 的子目录结构；
      相对路径计算失败（跨盘符等）时回退 output_dir/stem.cbz 并输出 warning
    - output_dir + flatten=True：平铺到 output_dir 根下，重名自动唯一化
      base.cbz → base (2).cbz → …
    """
    if output_dir is None:
        return ebook_path.with_suffix(".cbz")
    if flatten:
        base = flat_base_name(ebook_path, input_root)
        used = used_names if used_names is not None else set()
        cbz = unique_path(output_dir, base, used)
        if used_names is not None:
            used_names.add(str(cbz))
        return cbz
    if input_root is not None:
        try:
            rel = ebook_path.relative_to(input_root)
            return output_dir / rel.with_suffix(".cbz")
        except ValueError:
            cbz = output_dir / (ebook_path.stem + ".cbz")
            emit(t("rel_fallback", name=ebook_path.name, path=cbz), level="warning")
            return cbz
    return output_dir / (ebook_path.stem + ".cbz")


def find_opf(base_dir: Path) -> Path | None:
    """在目录下递归查找 .opf 文件"""
    for p in base_dir.rglob("*.opf"):
        return p
    return None


class HtmlImgParser(HTMLParser):
    """HTMLParser 子类：收集 <img> 标签的 src 属性。

    convert_charrefs=True 时 HTML 实体由 HTMLParser 自动解码
    （如 &amp; → &、&#x20; → 空格），收集后再统一用
    urllib.parse.unquote 处理 %XX 百分号编码。"""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.srcs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "img":
            for k, v in attrs:
                if k.lower() == "src" and v:
                    self.srcs.append(v)


def extract_img_srcs_with_parser(content: str) -> list[str]:
    """HTMLParser 兜底提取 img src：实体自动解码 + unquote 处理 %XX。

    与正则提取互补：覆盖属性顺序/换行/大小写、实体编码、%XX 等
    正则难以稳定的场景；任何异常返回 []，不影响调用方主流程。"""
    try:
        parser = HtmlImgParser()
        parser.feed(content)
        parser.close()
        out: list[str] = []
        for s in parser.srcs:
            try:
                out.append(unquote(s))
            except Exception:
                out.append(s)
        return out
    except Exception:
        return []


def extract_images_from_html(html_path: Path) -> list[Path]:
    """从 HTML 文件中提取所有 <img> 引用的本地图片路径"""
    try:
        content = html_path.read_text(encoding="utf-8", errors="ignore")
        srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not srcs:
            # 兜底：HtmlImgParser（实体自动解码 + unquote 处理 %XX），
            # 覆盖正则难以处理的属性顺序/换行/实体编码场景
            srcs = extract_img_srcs_with_parser(content)
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
        return images, t("align.drop", count=len(extras))
    return images + extras, t("align.append", count=len(extras))


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


    # 输入：mobi.extract 解包出的临时目录与 prefer（mobi7/mobi8）；输出：实际使用的子目录路径
def select_mobi_dir(tempdir: Path, prefer: str) -> Path:
    """根据 prefer 参数选择 mobi7 或 mobi8 目录；如果只有一份则返回那一份"""
    mobi7_dir = tempdir / "mobi7"
    mobi8_dir = tempdir / "mobi8"

    has7 = mobi7_dir.is_dir()
    has8 = mobi8_dir.is_dir()

    if has7 and has8:
        chosen = mobi7_dir if prefer == "mobi7" else mobi8_dir
        emit(t("dedupe.both_dirs", dir="mobi7" if prefer == "mobi7" else "mobi8"))
        return chosen
    if has8:
        return mobi8_dir
    if has7:
        return mobi7_dir
    # 都没有子目录，直接用 tempdir
    return tempdir


    # 输入：电子书路径与转换选项（delete/prefer/drop_extra/overwrite/output_dir/compress）；输出：(cbz 路径或 None, ConvStatus)
def ebook_to_cbz(ebook_path: Path, delete_original: bool = False, prefer: str = "mobi8", drop_extra: bool = False, overwrite: bool = False, output_dir: Path | None = None, compress: int = 0, flatten: bool = False, input_root: Path | None = None, used_names: set | None = None, comicinfo: bool = True) -> tuple[Path | None, ConvStatus]:
    """将单个 mobi 文件转换为 cbz

    prefer: 双目录 mobi（mobi7/mobi8）时保留哪份，默认 "mobi8"
    drop_extra: 目录中有未被收集的多余图片时放弃追加，默认追加到末尾
    overwrite: 目标 cbz 已存在时强制重新生成（默认跳过）
    output_dir: 指定 CBZ 输出目录（自动创建），默认与源 mobi 同目录
    flatten: 与 output_dir 联用时平铺到输出目录根下（默认保留相对子目录结构）
    input_root: target 为目录时作为相对子目录结构计算的基准
    used_names: 平铺唯一化已占用名集合（按处理顺序维护，保证 dry-run 与实跑一致）
    comicinfo: 是否生成 ComicInfo.xml（默认生成，--no-comicinfo 关闭）

    返回 (结果, 状态)：状态为 ConvStatus 枚举，
    - OK: 转换成功，结果为 cbz 路径
    - SKIP: 目标已存在且未指定 --overwrite，结果为 None
    - FAIL: 转换失败，结果为 None
    """
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
    cbz_path = target_cbz_path(ebook_path, output_dir, flatten=flatten, input_root=input_root, used_names=used_names)
    cbz_path.parent.mkdir(parents=True, exist_ok=True)
    if cbz_path.exists() and not overwrite:
        emit(t("convert.skip_exists", name=cbz_path.name))
        return None, ConvStatus.SKIP
    if cbz_path.exists():
        cbz_path.unlink()
        emit(t("convert.overwrite", name=cbz_path.name))

    extract_temp_paths = []  # 记录mobi库自动生成的临时文件夹

    try:
        # mobi.extract 不支持 output_dir，仅传输入文件
        tempdir_raw, _ = mobi.extract(str(ebook_path))
        tempdir = Path(tempdir_raw)
        extract_temp_paths.append(tempdir)

        # Step 2: 选择目录（mobi7/mobi8 去重）
        base_dir = select_mobi_dir(tempdir, prefer)

        # Step 3: 优先按 OPF spine 顺序提取图片，兜底按文件名排序
        opf_path = find_opf(base_dir)
        if opf_path:
            images = extract_images_by_spine(opf_path)
            if images:
                emit(t("convert.spine", count=len(images)))
            else:
                images = collect_images_fallback(base_dir)
                emit(t("convert.spine_empty", count=len(images)))
        else:
            images = collect_images_fallback(base_dir)
            emit(t("convert.no_opf", count=len(images)))

        if not images:
            emit(t("convert.no_images", name=ebook_path.name), level="error")
            emit(t("convert.drm_hint"), level="error")
            return None, ConvStatus.FAIL

        # 确保封面在第一位（兼容 cover/front 命名，封面可能未被 spine 引用）
        images = ensure_cover_first(images, base_dir)

        # 目录对齐兜底：目录图片数 vs 收集数不一致时，多出的图片追加到末尾
        total_in_dir = count_images_in_dir(base_dir)
        images, align_msg = align_images_with_dir(images, base_dir, drop_extra)
        if align_msg:
            emit(f"  {align_msg}")
        elif total_in_dir != len(images):
            emit(t("convert.count_mismatch", total=total_in_dir, collected=len(images)))

        # Step 3.6: 生成 ComicInfo.xml（默认启用，--no-comicinfo 关闭）
        comicinfo_xml = None
        if comicinfo:
            try:
                opf_meta = read_opf_metadata(opf_path) if opf_path else {}
                exth_meta = read_exth_metadata(ebook_path)
                meta = collect_comicinfo_meta(opf_meta, exth_meta, ebook_path)
                inferred = infer_series_number(ebook_path)
                comicinfo_xml = build_comicinfo(meta, images, inferred)
            except Exception:
                comicinfo_xml = None
            if comicinfo_xml is None:
                emit(t("comicinfo.invalid", err="build"), level="error")
                if cbz_path.exists():
                    cbz_path.unlink(missing_ok=True)
                return None, ConvStatus.FAIL
            emit(t("comicinfo.generating"))

        # Step 4: 打包为 cbz（默认 ZIP 无压缩，图片本身已压缩；--compress 1-9 启用 deflate）
        seen = {}
        seen_paths = set()  # 归一化路径集合：判物理重复（同一物理文件重复出现则跳过不写入）
        skipped_dup = 0
        if compress > 0:
            zf_obj = zipfile.ZipFile(str(cbz_path), "w", zipfile.ZIP_DEFLATED, compresslevel=compress)
        else:
            zf_obj = zipfile.ZipFile(str(cbz_path), "w", zipfile.ZIP_STORED)
        with zf_obj as zf:
            for idx, img in enumerate(images, 1):
                norm = norm_path(img)
                if norm in seen_paths:
                    # 物理重复：同一物理文件（含大小写差异等归一化后相同）再次出现，跳过不写入
                    skipped_dup += 1
                    continue
                seen_paths.add(norm)
                if img.name in seen:
                    # 重名：用序号前缀 + 原文件名，保证顺序且不冲突
                    arcname = f"{idx:04d}_{img.name}"
                else:
                    arcname = img.name
                    seen[img.name] = arcname
                zf.write(str(img), arcname)
        if skipped_dup:
            emit(t("convert.dedup_physical", count=skipped_dup))

        # Step 4b: 写入 ComicInfo.xml（追加进 CBZ ZIP 根目录）
        if comicinfo_xml is not None:
            try:
                write_comicinfo(cbz_path, comicinfo_xml)
                emit(t("comicinfo.created"))
            except Exception as e:
                cbz_path.unlink(missing_ok=True)
                emit(t("comicinfo.invalid", err=e), level="error")
                return None, ConvStatus.FAIL

        size_mb = cbz_path.stat().st_size / (1024 * 1024)
        emit(t("convert.done", name=cbz_path.name, count=len(images), size=f"{size_mb:.1f}"))

        # 完整性校验（ComicInfo 启用时追加 3 项校验）
        ok, msg = validate_cbz(cbz_path, require_comicinfo=(comicinfo_xml is not None))
        if not ok:
            cbz_path.unlink(missing_ok=True)
            emit(t("convert.verify_fail", name=cbz_path.name, msg=msg), level="error")
            return None, ConvStatus.FAIL
        emit(t("convert.verify_ok", msg=msg))

        # Step 5: 可选删除原始 mobi
        if delete_original:
            ebook_path.unlink()
            emit(t("convert.deleted_original", name=ebook_path.name))

        return cbz_path, ConvStatus.OK
    except Exception as e:
        # 转换失败仅清理半成品cbz
        if cbz_path.exists():
            cbz_path.unlink(missing_ok=True)
        emit(t("convert.error", name=ebook_path.name, err=e), level="error")
        err = str(e).lower()
        if any(k in err for k in ("drm", "encrypt", "decrypt", "protected", "kfx")):
            emit(t("convert.error_drm_hint"), level="error")
        return None, ConvStatus.FAIL
    finally:
        # 无论正常/异常，强制删除 mobi 解压出来的临时目录，解决 Ctrl+C 残留
        for p in extract_temp_paths:
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)


def read_exth_metadata(p: Path) -> dict:
    """读取 mobi 文件头 EXTH 扩展记录中的元数据（不解包，只读文件头）。

    EXTH 记录通过搜索 "EXTH" 魔数定位（限制在前 64KB 头部区域），
    兼容 BOOKMOBI 位于偏移 60 的非标准头部变体。
    返回 dict，仅包含实际存在的字段：
    title(503) author(100) publisher(101) language(524)
    publish_date(106) isbn(104) asin(113) copyright(109)
    """
    try:
        with open(p, "rb") as f:
            head = f.read(65536)
        idx = head.find(b"EXTH")
        if idx < 0 or idx > 65536 - 12:
            return {}
        count = struct.unpack(">I", head[idx + 8:idx + 12])[0]
        if count <= 0 or count > 1000:
            return {}
        key_map = {
            503: "title", 100: "author", 101: "publisher", 524: "language",
            106: "publish_date", 104: "isbn", 113: "asin", 109: "copyright",
        }
        pos = idx + 12
        meta = {}
        for _ in range(count):
            t = struct.unpack(">I", head[pos:pos + 4])[0]
            l = struct.unpack(">I", head[pos + 4:pos + 8])[0]
            if l < 8 or pos + l > len(head):
                break
            val = head[pos + 8:pos + l].decode("utf-8", errors="replace").strip("\x00")
            key = key_map.get(t)
            if key and val and key not in meta:
                meta[key] = val
            pos += l
        return meta
    except Exception:
        return {}


# 输入：OPF 文件路径；输出：dc:metadata 字段字典（title/creator/publisher/date/language/description）
def read_opf_metadata(opf_path: Path) -> dict:
    """读取 OPF 的 dc:metadata 元数据（title/creator/publisher/date/language/description）。

    仅返回实际存在的字段，供 ComicInfo.xml 字段映射使用。
    """
    try:
        tree = ET.parse(opf_path)
        root = tree.getroot()
        ns = {"dc": "http://purl.org/dc/elements/1.1/"}
        out = {}
        for key, tag in (
            ("title", "dc:title"), ("creator", "dc:creator"),
            ("publisher", "dc:publisher"), ("date", "dc:date"),
            ("language", "dc:language"), ("description", "dc:description"),
        ):
            el = root.find(f".//{tag}", ns)
            if el is not None and el.text and el.text.strip():
                out[key] = el.text.strip()
        return out
    except Exception:
        return {}


# 输入：OPF 元数据 + EXTH 元数据 + 源电子书路径；输出：ComicInfo 字段字典（仅含可靠来源的键）
def collect_comicinfo_meta(opf_meta: dict, exth_meta: dict, ebook_path: Path) -> dict:
    """按优先级聚合 ComicInfo 字段：Title/Writer/Publisher/Year/Language/Summary。

    Title=OPF title→EXTH title→文件名 stem；Writer=OPF creator→EXTH author；
    Publisher=OPF publisher→EXTH publisher；Year=PublicationDate 年份；
    LanguageISO=电子书自身语言（不按文件名猜）；Summary=OPF description。
    """
    meta: dict = {}
    title = opf_meta.get("title") or exth_meta.get("title") or ebook_path.stem
    if title and title.strip():
        meta["title"] = title.strip()
    writer = opf_meta.get("creator") or exth_meta.get("author")
    if writer and writer.strip():
        meta["writer"] = writer.strip()
    publisher = opf_meta.get("publisher") or exth_meta.get("publisher")
    if publisher and publisher.strip():
        meta["publisher"] = publisher.strip()
    date_str = opf_meta.get("date") or exth_meta.get("publish_date")
    if date_str:
        m = re.search(r"(19|20)\d{2}", date_str)
        if m:
            meta["year"] = m.group(0)
    lang_src = opf_meta.get("language") or exth_meta.get("language")
    if lang_src:
        norm = normalize_language(lang_src)
        if norm:
            meta["language"] = norm
    if opf_meta.get("description"):
        meta["summary"] = opf_meta["description"]
    return meta


# 输入：语言代码字符串；输出：ISO 639-1 两位小写代码，无法识别返回 None
def normalize_language(code: str) -> str | None:
    """把常见语言代码标准化为 ISO 639-1 两位小写。

    支持 2 位（en/ja/zh...）、3 位（eng/jpn/chi...）、带区域后缀
    （en-US/zh-CN/ja-jp...）等写法；无法高置信度识别时返回 None。
    """
    if not code:
        return None
    seg = code.strip().split("-")[0].split("_")[0].split(".")[0].lower()
    if not seg or not seg.isalpha():
        return None
    if len(seg) == 2:
        return seg
    three_to_two = {
        "eng": "en", "jpn": "ja", "chi": "zh", "zho": "zh", "cmn": "zh",
        "kor": "ko", "fre": "fr", "fra": "fr", "ger": "de", "deu": "de",
        "spa": "es", "ita": "it", "rus": "ru", "por": "pt", "ara": "ar",
        "tha": "th", "vie": "vi", "ind": "id", "msa": "ms", "may": "ms",
        "nld": "nl", "dut": "nl", "pol": "pl", "tur": "tr", "ukr": "uk",
        "swe": "sv", "dan": "da", "fin": "fi", "nor": "no", "ell": "el",
        "gre": "el", "heb": "he", "hin": "hi", "ces": "cs", "cze": "cs",
        "hun": "hu", "ron": "ro", "rum": "ro", "bul": "bg", "slk": "sk",
        "slo": "sk", "slv": "sl", "hrv": "hr", "srp": "sr", "est": "et",
        "lav": "lv", "lit": "lt", "cat": "ca", "fas": "fa", "per": "fa",
        "ben": "bn", "tam": "ta", "tel": "te", "mal": "ml", "kan": "kn",
        "guj": "gu", "pan": "pa", "urd": "ur", "nep": "ne", "sin": "si",
        "khm": "km", "lao": "lo", "mya": "my", "bur": "my", "tgl": "tl",
        "swa": "sw", "afr": "af", "sqi": "sq", "alb": "sq", "amh": "am",
        "aze": "az", "bel": "be", "bos": "bs", "cym": "cy", "wel": "cy",
        "epo": "eo", "eus": "eu", "baq": "eu", "fry": "fy", "gle": "ga",
        "gla": "gd", "glg": "gl", "hau": "ha", "hye": "hy", "arm": "hy",
        "isl": "is", "ice": "is", "kat": "ka", "geo": "ka", "kaz": "kk",
        "kur": "ku", "ltz": "lb", "mkd": "mk", "mac": "mk", "mon": "mn",
        "mar": "mr", "mlt": "mt", "nob": "nb", "nno": "nn", "oci": "oc",
        "pus": "ps", "kin": "rw", "snd": "sd", "sme": "se", "smo": "sm",
        "sna": "sn", "som": "so", "sot": "st", "sun": "su", "tgk": "tg",
        "tir": "ti", "tuk": "tk", "tat": "tt", "uig": "ug", "uzb": "uz",
        "xho": "xh", "yid": "yi", "yor": "yo", "zul": "zu",
    }
    return three_to_two.get(seg)


# 卷标记词：无实际系列名时，series 若为这些词或纯数字则视为无法推断（宁缺勿错）
_VOLUME_MARKERS = {"vol", "volume", "v", "第", "巻", "卷"}


def _is_volume_marker(series: str) -> bool:
    """判断 series 是否为纯卷标记词或纯数字（无实际系列名，宁缺勿错）。"""
    s = series.strip().lower()
    return s in _VOLUME_MARKERS or s.isdigit()


# 输入：电子书文件路径；输出：(series, number) 高置信度推断结果，无法判断返回 (None, None)
def infer_series_number(path: Path) -> tuple[str | None, str | None]:
    """从文件名高置信度推断漫画 Series/Number。

    支持形式：001 / 01 / 1 / Vol.01 / Vol 01 / Volume 01 / 第 01 卷 /
    01巻 等；纯数字结尾（如 "One Piece 108"）也视为高置信度，
    但 4 位年份（19xx/20xx）、纯数字文件名与无系列名的卷标记
    （如 "Vol.01" / "Volume 01" / "01巻"）会被排除，宁缺勿错。
    """
    stem = path.stem
    if not stem:
        return None, None
    s = stem.strip()
    # 1) Vol.01 / Vol 01 / Volume 01 / vol.1 / v01 形式
    m = re.match(r"^(?P<series>.+?)[\s_\-\.]*[Vv]ol(?:ume)?[\s_\-\.]*(\d{1,4})\s*$", s)
    if m:
        series = m.group("series").strip()
        if _is_volume_marker(series):
            return None, None
        return series, str(int(m.group(2)))
    # 2) 中文卷：第 01 卷 / 第1卷（阿拉伯数字）
    m = re.match(r"^(?P<series>.+?)[\s_\-\.]*第[\s_\-\.]*(\d{1,4})[\s_\-\.]*卷\s*$", s)
    if m:
        series = m.group("series").strip()
        if _is_volume_marker(series):
            return None, None
        return series, str(int(m.group(2)))
    # 3) 日文卷：01巻 / 第1巻
    m = re.match(r"^(?P<series>.+?)[\s_\-\.]*第?[\s_\-\.]*(\d{1,4})[\s_\-\.]*巻\s*$", s)
    if m:
        series = m.group("series").strip()
        if _is_volume_marker(series):
            return None, None
        return series, str(int(m.group(2)))
    # 4) 纯数字结尾（空格/连字符/下划线/点分隔）：如 "One Piece 108"
    m = re.match(r"^(?P<series>.+?)[\s_\-\.]+(\d{1,4})$", s)
    if m:
        num = m.group(2)
        if len(num) == 4 and 1900 <= int(num) <= 2100:
            return None, None  # 疑似年份，宁缺勿错
        series = m.group("series").strip()
        if not series or _is_volume_marker(series):
            return None, None
        return series, str(int(num))
    return None, None


# 输入：聚合后的元数据字典 + 最终图片列表 + (series, number) 推断结果；输出：ComicInfo.xml 文本或 None
def build_comicinfo(meta: dict, images: list, inferred: tuple) -> str | None:
    """用 xml.etree.ElementTree 生成 ComicInfo.xml（禁止手工拼接字符串）。

    PageCount 必写（=最终写入 CBZ 的实际图片数）；其余字段有可靠来源
    才写入，无来源直接省略，不生成空标签。返回含 XML 声明的 UTF-8 文本。
    """
    try:
        root = ET.Element("ComicInfo")
        series, number = inferred if isinstance(inferred, tuple) else (None, None)
        ordered = [
            ("Title", meta.get("title")),
            ("Series", series),
            ("Number", number),
            ("Writer", meta.get("writer")),
            ("Publisher", meta.get("publisher")),
            ("Year", meta.get("year")),
            ("LanguageISO", meta.get("language")),
            ("PageCount", str(len(images))),
            ("Summary", meta.get("summary")),
        ]
        for tag, val in ordered:
            if val is None:
                continue
            el = ET.SubElement(root, tag)
            el.text = str(val)
        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        return xml_bytes.decode("utf-8")
    except Exception:
        return None


# 输入：CBZ 文件路径 + ComicInfo.xml 文本内容；输出：追加写入 CBZ 根目录
def write_comicinfo(cbz_path: Path, xml_content: str) -> None:
    """把 ComicInfo.xml 追加写入 CBZ ZIP 根目录（UTF-8，含 XML 声明）。

    失败时抛出异常，由调用方决定清理与失败处理。
    """
    with zipfile.ZipFile(str(cbz_path), "a", zipfile.ZIP_STORED) as zf:
        zf.writestr("ComicInfo.xml", xml_content.encode("utf-8"))


def get_drm_flag(p: Path) -> bool:
    """读取 PalmDB 头偏移 12 处的加密字段，非 0 表示 DRM 加密"""
    try:
        with open(p, "rb") as f:
            f.seek(12)
            return struct.unpack(">H", f.read(2))[0] != 0
    except Exception:
        return False


def image_dimensions(img: Path) -> tuple[int, int] | None:
    """从图片文件头读取宽高（不加载整图），支持 png/jpeg/gif/webp/bmp，失败返回 None。

    JPEG 的 SOF 段可能被 APP0/APP1(EXIF) 等大段标记推后到几 KB 处，
    因此读取 64KB 头部用于扫描，避免只读到前 64 字节而解析失败。"""
    try:
        with open(img, "rb") as f:
            head = f.read(65536)
        if head.startswith(b"\x89PNG\r\n\x1a\n") and len(head) >= 24:
            w, h = struct.unpack(">II", head[16:24])
            return w, h
        if head.startswith(b"\xff\xd8"):
            # JPEG: 扫描 SOF 段（C0-CF，排除 D8/D9/DA 等）
            pos = 2
            while pos + 9 < len(head):
                if head[pos] != 0xFF:
                    pos += 1
                    continue
                marker = head[pos + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                              0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", head[pos + 5:pos + 9])
                    return w, h
                if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                    pos += 2
                else:
                    seg_len = struct.unpack(">H", head[pos + 2:pos + 4])[0]
                    pos += 2 + seg_len
            return None
        if head.startswith(b"GIF8"):
            w, h = struct.unpack("<HH", head[6:10])
            return w, h
        if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
            if head[12:16] == b"VP8X" and len(head) >= 32:
                w = struct.unpack("<I", head[24:28])[0] & 0xFFFFFF
                h = struct.unpack("<I", head[28:32])[0] & 0xFFFFFF
                return w + 1, h + 1
            if head[12:16] == b"VP8 " and len(head) >= 30:
                w = struct.unpack("<H", head[26:28])[0] & 0x3FFF
                h = struct.unpack("<H", head[28:30])[0] & 0x3FFF
                return w, h
            if head[12:16] == b"VP8L" and len(head) >= 25:
                b = head[21:25]
                w = (b[0] | ((b[1] & 0x3F) << 8)) + 1
                h = ((b[1] >> 6) | (b[2] << 2) | ((b[3] & 0x0F) << 10)) + 1
                return w, h
            return None
        if head.startswith(b"BM") and len(head) >= 26:
            w, h = struct.unpack("<ii", head[18:26])
            return abs(w), abs(h)
        return None
    except Exception:
        return None


def get_opf_guide_cover_href(opf_path: Path) -> str | None:
    """解析 OPF 文件中 <guide><reference type="cover" href="..."> 的封面引用。

    兼容 type/href 属性顺序互换；找不到 type="cover" 引用时返回 None。"""
    try:
        text = opf_path.read_text("utf-8", errors="replace")
        m = re.search(
            r'<reference\s+[^>]*type=["\']cover["\'][^>]*href=["\']([^"\']+)["\']',
            text, re.I,
        )
        if not m:
            m = re.search(
                r'<reference\s+[^>]*href=["\']([^"\']+)["\'][^>]*type=["\']cover["\']',
                text, re.I,
            )
        return m.group(1) if m else None
    except Exception:
        return None


def parse_ncx_toc(base_dir: Path) -> tuple[int, list[str]]:
    """解析 toc.ncx 目录条目数并预览前 3 条标题。

    返回 (条目数, 标题预览列表)；找不到 ncx 或解析失败返回 (0, [])。"""
    ncx = None
    for f in base_dir.rglob("*.ncx"):
        ncx = f
        break
    if ncx is None:
        return 0, []
    try:
        text = ncx.read_text("utf-8", errors="replace")
        titles = re.findall(r"<text>(.*?)</text>", text, re.I | re.S)
        titles = [re.sub(r"<[^>]+>", "", t).strip() for t in titles]
        titles = [t for t in titles if t]
        return len(titles), titles[:3]
    except Exception:
        return 0, []


    # 输入：电子书文件路径、最小字节数过滤与 prefer；输出：状态字符串 ok/invalid/noimg/drm/fail（供汇总计数）
def inspect_ebook(p: Path, min_bytes: int, prefer: str = "mobi8") -> str:
    """检查单个电子书内部信息（--inspect 模式核心）。

    流程：头部基础检查（魔数/大小/DRM）→ EXTH 元数据 → 解包 →
    目录结构/OPF/spine/NCX/图片数/封面/格式分布/分辨率统计 → 压缩建议。
    DRM 双重判断：头部标记有→直接判有并跳过解包；
    无标记+解包图片0→疑似；无标记+有图片→无。
    只解包不打包，结束后自动清理临时目录。
    返回状态字符串：ok / invalid / noimg / drm / fail（供汇总计数）。
    """
    size = p.stat().st_size
    size_mb = size / (1024 * 1024)
    emit(t("inspect.file_line", name=p.name, size=f"{size_mb:.1f}"), level="summary")

    reason = precheck_ebook(p, min_bytes)
    if reason:
        if "BOOKMOBI" in reason:
            emit(t("inspect.base_invalid_magic"))
        else:
            emit(t("inspect.base_reason", reason=reason))
        emit(t("inspect.invalid_hint"))
        return "invalid"

    drm = get_drm_flag(p)
    meta = read_exth_metadata(p)

    base_parts = [t("inspect.base_magic_ok")]
    if drm:
        base_parts.append(t("inspect.drm_marked"))
    else:
        base_parts.append(t("inspect.drm_unmarked"))
    if min_bytes > 0 and size < min_bytes:
        base_parts.append(t("inspect.below_min_size", min=min_bytes))
    else:
        base_parts.append(t("inspect.min_size_not_filter"))
    emit(t("inspect.base_line", parts=" | ".join(base_parts)))
    if drm:
        emit(t("inspect.drm_hint"), level="summary")
        return "drm"

    meta_parts = []
    if meta.get("title"):
        meta_parts.append(t("inspect.meta_title", value=meta["title"]))
    if meta.get("author"):
        meta_parts.append(t("inspect.meta_author", value=meta["author"]))
    if meta.get("language"):
        meta_parts.append(t("inspect.meta_language", value=meta["language"]))
    if meta.get("publish_date"):
        meta_parts.append(t("inspect.meta_publish_date", value=meta["publish_date"]))
    if meta.get("publisher"):
        meta_parts.append(t("inspect.meta_publisher", value=meta["publisher"]))
    if meta.get("isbn"):
        meta_parts.append(t("inspect.meta_isbn", value=meta["isbn"]))
    if meta.get("asin"):
        meta_parts.append(t("inspect.meta_asin", value=meta["asin"]))
    if meta.get("copyright"):
        meta_parts.append(t("inspect.meta_copyright", value=meta["copyright"]))
    if meta_parts:
        emit(t("inspect.meta_line", parts=" | ".join(meta_parts)))

    extract_temp_paths = []
    try:
        tempdir_raw, _ = mobi.extract(str(p))
        tempdir = Path(tempdir_raw)
        extract_temp_paths.append(tempdir)

        has7 = (tempdir / "mobi7").is_dir()
        has8 = (tempdir / "mobi8").is_dir()
        emit(t("inspect.both_dirs", mobi7=has7, mobi8=has8))
        base_dir = select_mobi_dir(tempdir, prefer)

        opf_path = find_opf(base_dir)
        emit(t("inspect.opf_exists") if opf_path else t("inspect.opf_missing"))
        spine_count = 0
        spine_images = []
        if opf_path:
            spine_images = extract_images_by_spine(opf_path) or []
            spine_count = len(spine_images)
        emit(t("inspect.spine_count", count=spine_count))
        for s_img in spine_images[:5]:
            emit(f"    {s_img.name}")

        ncx_count, ncx_preview = parse_ncx_toc(base_dir)
        if ncx_count:
            emit(t("inspect.ncx_count", count=ncx_count, preview=" | ".join(ncx_preview)))
        else:
            emit(t("inspect.ncx_missing"))

        total_in_dir = count_images_in_dir(base_dir)
        emit(t("inspect.dir_images", count=total_in_dir))

        if total_in_dir == 0:
            emit(t("inspect.drm_suspected"))
            emit(t("inspect.cover_missing"))
            emit(t("inspect.fmt_none"))
            emit(t("inspect.drm_bad_hint"), level="summary")
            return "noimg"
        emit(t("inspect.drm_none", count=total_in_dir))

        # 封面检测：OPF guide type=cover 引用优先，未命中回退文件名扫描
        cover = None
        cover_src = ""
        if opf_path:
            href = get_opf_guide_cover_href(opf_path)
            if href:
                cand = (base_dir / href).resolve()
                if cand.is_file() and cand.suffix.lower() in IMAGE_EXTENSIONS:
                    cover = cand
                    cover_src = t("inspect.cover_src_guide")
                else:
                    fname = href.replace("\\", "/").rsplit("/", 1)[-1]
                    for cp in base_dir.rglob(fname):
                        if cp.is_file() and cp.suffix.lower() in IMAGE_EXTENSIONS:
                            cover = cp
                            cover_src = t("inspect.cover_src_guide")
                            break
        if cover is None:
            for cp in base_dir.rglob("*"):
                if (cp.is_file() and cp.suffix.lower() in IMAGE_EXTENSIONS
                        and any(k in cp.name.lower() for k in COVER_KEYWORDS)):
                    cover = cp
                    cover_src = t("inspect.cover_src_filename")
                    break
        if cover:
            emit(t("inspect.cover_found", name=cover.name, src=cover_src))
        else:
            emit(t("inspect.cover_missing"))

        # 格式分布 + 分辨率统计
        fmt_counter = {}
        res_list = []
        all_imgs = []
        for root, dirs, files in os.walk(base_dir):
            for f in files:
                fp = Path(root) / f
                if fp.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                all_imgs.append(fp)
                ext = fp.suffix.lower().lstrip(".")
                if ext == "jpeg":
                    ext = "jpg"
                fmt_counter[ext] = fmt_counter.get(ext, 0) + 1
                dim = image_dimensions(fp)
                if dim:
                    res_list.append(dim)

        total_fmt = sum(fmt_counter.values())
        fmt_parts = [
            f"{k} {v} ({v / total_fmt * 100:.1f}%)"
            for k, v in sorted(fmt_counter.items(), key=lambda x: -x[1])
        ]
        emit(t("inspect.fmt_stats", parts=" | ".join(fmt_parts)))

        if res_list:
            total_res = len(res_list)
            w_counter = Counter(d[0] for d in res_list)
            h_counter = Counter(d[1] for d in res_list)
            main_w, main_wc = w_counter.most_common(1)[0]
            main_h, main_hc = h_counter.most_common(1)[0]
            if main_hc >= main_wc:
                # 主流高度明确时：显示主流高 + 该高度下的宽度范围
                w_sub = [d[0] for d in res_list if d[1] == main_h]
                res_parts = [
                    t("inspect.res_main_h", height=main_h, count=main_hc, pct=f"{main_hc / total_res * 100:.0f}"),
                    t("inspect.res_w_range", min=min(w_sub), max=max(w_sub)),
                ]
            else:
                # 主流宽度明确时：显示主流宽 + 该宽度下的高度范围
                h_sub = [d[1] for d in res_list if d[0] == main_w]
                res_parts = [
                    t("inspect.res_main_w", width=main_w, count=main_wc, pct=f"{main_wc / total_res * 100:.0f}"),
                    t("inspect.res_h_range", min=min(h_sub), max=max(h_sub)),
                ]
            emit(t("inspect.res_line", parts=" | ".join(res_parts)))

        # 压缩建议
        jpeg_ratio = (fmt_counter.get("jpg", 0) + fmt_counter.get("jpeg", 0)) / total_fmt
        png_ratio = fmt_counter.get("png", 0) / total_fmt
        if png_ratio >= 0.5:
            emit(t("inspect.adv_png"))
        elif jpeg_ratio >= 0.8:
            emit(t("inspect.adv_jpeg"))
        else:
            emit(t("inspect.adv_mixed"))

        # ComicInfo.xml 预览块（inspect 不写文件，仅展示即将生成的元数据）
        opf_meta = read_opf_metadata(opf_path) if opf_path else {}
        cmeta = collect_comicinfo_meta(opf_meta, meta, p)
        cseries, cnumber = infer_series_number(p)
        emit("ComicInfo.xml:")
        if cmeta.get("title"):
            emit(f"  Title: {cmeta['title']}")
        if cseries:
            emit(f"  Series: {cseries} [{t('comicinfo.inferred')}]")
        if cnumber:
            emit(f"  Number: {cnumber} [{t('comicinfo.inferred')}]")
        if cmeta.get("writer"):
            emit(f"  Writer: {cmeta['writer']}")
        if cmeta.get("publisher"):
            emit(f"  Publisher: {cmeta['publisher']}")
        if cmeta.get("year"):
            emit(f"  Year: {cmeta['year']}")
        if cmeta.get("language"):
            emit(f"  LanguageISO: {cmeta['language']}")
        emit(f"  PageCount: {len(all_imgs)}")
        if cmeta.get("summary"):
            emit(f"  Summary: {cmeta['summary']}")
        return "ok"
    except Exception as e:
        emit(t("inspect.unpack_fail", err=e), level="summary")
        return "fail"
    finally:
        for tp in extract_temp_paths:
            if tp.exists():
                shutil.rmtree(tp, ignore_errors=True)


def inspect_mode(ebook_files: list[Path], precheck_skipped: list, args) -> None:
    """--inspect 模式入口：随机抽查或全量检查电子书内部信息，不生成 CBZ"""
    if precheck_skipped:
        emit(t("inspect_mode.precheck_header", count=len(precheck_skipped)), level="summary")
        for mf, reason in precheck_skipped:
            emit("  " + t("skip_entry", path=str(mf), reason=reason), level="summary")

    if not ebook_files:
        emit(t("inspect_mode.none"), level="error")
        sys.exit(0)

    if args.inspect_all:
        targets = ebook_files
        emit(t("inspect_mode.all", count=len(targets)), level="summary")
    else:
        targets = [random.choice(ebook_files)]
        emit(t("inspect_mode.random", total=len(ebook_files)), level="summary")

    total_start = time.perf_counter()
    ok = fail = invalid = noimg = drm_n = timeout_n = 0
    pbar = create_progress_if_needed(args, targets, t("progress.desc.inspect"))
    try:
        for mf in targets:
            if pbar is not None:
                pbar.set_postfix_str(truncate_name(mf.name))
            timed_out, result = run_with_timeout(inspect_ebook, args.timeout, mf, args.min_size, args.prefer)
            if timed_out:
                emit(t("inspect_mode.timeout", name=mf.name, seconds=args.timeout), level="error")
                emit(t("inspect_mode.timeout_residue"), level="warning")
                timeout_n += 1
            elif result == "invalid":
                invalid += 1
            elif result == "drm":
                drm_n += 1
            elif result == "noimg":
                noimg += 1
            elif result == "ok":
                ok += 1
            else:
                fail += 1
            if pbar is not None:
                pbar.update(1)
    except KeyboardInterrupt:
        emit(t("inspect_mode.ctrl_c"), level="summary")
    finally:
        if pbar is not None:
            pbar.close()

    total_elapsed = time.perf_counter() - total_start
    if not args.inspect_all:
        emit(t("inspect_mode.random_note", total=len(ebook_files)), level="summary")
    emit(
        t(
            "inspect_mode.summary",
            total=len(targets), ok=ok, invalid=invalid, drm=drm_n,
            noimg=noimg, timeout=timeout_n, elapsed=f"{total_elapsed:.1f}",
        ),
        level="summary",
    )


def main():
    """入口：统一捕获顶层异常，崩溃堆栈经 emit 输出到控制台与日志"""
    try:
        _main()
    except KeyboardInterrupt:
        # 主循环内的中断已有兜底，此处兜底参数解析/收集阶段的中断
        emit(t("main.ctrl_c"), level="summary")
        sys.exit(130)
    except Exception:
        emit(t("main.crash"), level="error")
        emit(traceback.format_exc().rstrip(), level="error")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    """构建参数解析器：help 文案全部经 t() 生成，随 --language 切换"""
    parser = argparse.ArgumentParser(description=t("help.description"))
    parser.add_argument(
        "--version", action="version", version=f"{SCRIPT_NAME} {__version__}"
    )
    # 输入：语言选择 auto/zh-CN/zh-TW/ja/en；输出：全部文案与 --help 随所选语言翻译
    parser.add_argument(
        "--language",
        choices=["auto", "zh-CN", "zh-TW", "ja", "en"],
        default="auto",
        help=t("help.language"),
    )
    # 输入：目标目录或文件路径（位置参数）；输出：作为扫描/转换的起点
    parser.add_argument("target", help=t("help.target"))
    # 输入：是否删除源文件；输出：转换成功后删除原始电子书
    parser.add_argument(
        "--delete", action="store_true", help=t("help.delete")
    )
    # 输入：双目录 mobi 保留哪份 mobi7/mobi8；输出：解包后选择目录的依据
    parser.add_argument(
        "--prefer",
        choices=["mobi7", "mobi8"],
        default="mobi8",
        help=t("help.prefer"),
    )
    # 输入：同名不同扩展名时的保留优先级（逗号分隔，如 azw3,mobi）；输出：去重时保留哪份
    parser.add_argument(
        "--ext-priority",
        type=parse_ext_priority,
        default=["azw3"],
        metavar="EXTS",
        help=t("help.ext_priority"),
    )
    # 输入：是否丢弃目录中多余图片；输出：对齐阶段是否放弃追加到末尾
    parser.add_argument(
        "--drop-extra",
        action="store_true",
        help=t("help.drop_extra"),
    )
    # 输入：目标 cbz 已存在时是否强制重生成；输出：覆盖旧 cbz 还是跳过
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=t("help.overwrite"),
    )
    # 输入：单文件转换超时秒数（0 不限制）；输出：超时文件跳过并计入失败
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        metavar="SECONDS",
        help=t("help.timeout"),
    )
    # 输入：最小字节数过滤（缺省值 1000，0 关闭）；输出：小于该值的文件预处理跳过
    parser.add_argument(
        "--min-size",
        type=int,
        nargs="?",
        const=1000,
        default=0,
        metavar="BYTES",
        help=t("help.min_size"),
    )
    # 输入：CBZ 输出目录；输出：转换结果写入该目录（默认与源同目录）
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        help=t("help.output_dir"),
    )
    # 输入：是否平铺输出；输出：所有 CBZ 放到输出目录根下（仅与 --output-dir 联用）
    parser.add_argument(
        "--flatten",
        action="store_true",
        help=t("help.flatten"),
    )
    # 输入：是否试运行；输出：只扫描打印流程，不做任何磁盘写入
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=t("help.dry_run"),
    )
    # 输入：是否强制显示进度条；输出：覆盖自动判断，始终显示
    parser.add_argument(
        "--progress",
        action="store_true",
        help=t("help.progress"),
    )
    # 输入：是否强制关闭进度条；输出：覆盖自动判断，始终不显示
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help=t("help.no_progress"),
    )
    # 输入：是否静默；输出：抑制非 summary/error 级输出（仅写日志）
    parser.add_argument(
        "--quiet",
        action="store_true",
        help=t("help.quiet"),
    )
    # 输入：是否精简汇总；输出：成功/跳过/预处理跳过只显示数量
    parser.add_argument(
        "--short-summary",
        action="store_true",
        help=t("help.short_summary"),
    )
    # 输入：zip 压缩级别 0-9；输出：打包时使用 STORED 或 DEFLATED
    parser.add_argument(
        "--compress",
        type=int,
        default=0,
        choices=range(0, 10),
        metavar="LEVEL",
        help=t("help.compress"),
    )
    # 输入：是否随机抽查 1 个文件检查内部信息；输出：inspect 检查结果（不生成 cbz）
    parser.add_argument(
        "--inspect",
        action="store_true",
        help=t("help.inspect"),
    )
    # 输入：是否全量检查；输出：对所有有效文件执行 inspect
    parser.add_argument(
        "--inspect-all",
        action="store_true",
        help=t("help.inspect_all"),
    )
    # 输入：是否关闭 ComicInfo.xml 生成；输出：关闭时 CBZ 不含漫画元数据
    parser.add_argument(
        "--no-comicinfo",
        action="store_true",
        help=t("help.no_comicinfo"),
    )
    # 输入：日志文件路径；输出：控制台输出同步写入该文件（UTF-8）
    parser.add_argument(
        "--log",
        metavar="FILE",
        help=t("help.log"),
    )
    return parser


def _main():
    # 先解析 --language（不触发帮助），确定语言后再建正式 parser，使 --help 随语言翻译
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        "--language",
        choices=["auto", "zh-CN", "zh-TW", "ja", "en"],
        default="auto",
    )
    known, _ = pre_parser.parse_known_args()
    set_language(known.language)

    parser = build_parser()
    args = parser.parse_args()

    # --progress 与 --no-progress 同传时，以最后出现的参数为准（argparse 会把两者都置 True，需扫描 argv 修正）
    last_progress_flag = None
    for a in sys.argv[1:]:
        if a == "--progress":
            last_progress_flag = "progress"
        elif a == "--no-progress":
            last_progress_flag = "no_progress"
    if last_progress_flag == "progress":
        args.progress, args.no_progress = True, False
    elif last_progress_flag == "no_progress":
        args.progress, args.no_progress = False, True

    global _quiet_mode, _log_path, _short_summary, _compress_level
    _quiet_mode = args.quiet
    _log_path = args.log
    _short_summary = args.short_summary
    _compress_level = args.compress

    # 输入：--language auto（或未显式指定走默认 auto）；输出：提示实际识别的语种（quiet 时抑制）
    if known.language == "auto":
        emit(t("run.auto_language", lang=CURRENT_LANGUAGE))

    target = Path(args.target)
    if not target.exists():
        emit(t("run.path_not_found", path=args.target), level="error")
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else None

    # 启动校验：--flatten 必须与 --output-dir 联用，否则报错退出
    if args.flatten and output_dir is None:
        emit(t("error.flatten_without_output_dir"), level="error")
        emit(t("output.flatten_requires_dir"), level="error")
        sys.exit(2)

    # --inspect-all 单独使用（未配合 --inspect）时自动启用 --inspect
    if args.inspect_all and not args.inspect:
        emit(t("warn.inspect_all_auto_enable"), level="warning")
        args.inspect = True

    # input_root：target 为目录时作为相对子目录结构的基准；
    # target 为文件时不计算相对路径，直接输出 DIR/stem.cbz
    input_root = target if target.is_dir() else None

    ebook_files = collect_ebook_files(target)
    if not ebook_files:
        emit(t("run.no_ebooks", path=args.target), level="error")
        sys.exit(0)

    # 预处理：过滤 0 字节 / 文件头损坏的电子书，直接跳过并记录原因
    precheck_skipped = []  # (Path, reason)
    valid_ebook_files = []
    for mf in ebook_files:
        reason = precheck_ebook(mf, args.min_size)
        if reason:
            precheck_skipped.append((mf, reason))
        else:
            valid_ebook_files.append(mf)
    ebook_files = valid_ebook_files

    # 同名去重：同目录同主文件名（仅扩展名不同）只保留一份
    ebook_files, dedupe_skipped = dedupe_ebook_files(ebook_files, args.ext_priority)

    if precheck_skipped and not args.dry_run and not args.inspect:
        emit(t("run.precheck_header", count=len(precheck_skipped)), level="summary")
        if not _short_summary:
            for mf, reason in precheck_skipped:
                emit("  " + t("skip_entry", path=str(mf), reason=reason), level="summary")

    if args.inspect:
        inspect_mode(ebook_files, precheck_skipped, args)
        return

    if not ebook_files:
        emit(t("run.none_convertible"), level="error")
        sys.exit(0)

    emit(t("run.found", total=len(ebook_files), pre=len(precheck_skipped), dedup=len(dedupe_skipped)))
    for mf in ebook_files:
        emit(f"  {t('tag.file')} {mf}")
    emit("")
    if output_dir is not None:
        if args.flatten:
            emit(t("output.mode_flatten", dir=output_dir), level="summary")
        else:
            emit(t("output.mode_preserve", dir=output_dir), level="summary")

    if args.dry_run:
        emit(t("run.dryrun_banner"), level="summary")
        # ComicInfo 启用状态提示（dry-run 不创建 XML，仅提示一行）
        emit(t("comicinfo.generating") if not args.no_comicinfo else t("comicinfo.disabled"), level="summary")
        # dry-run 输出目录可写性检查：--output-dir 指定目录，或各源文件所在目录（默认输出位置）
        if output_dir is not None:
            check_dirs = [str(output_dir)]
        else:
            check_dirs = sorted({str(mf.parent) for mf in ebook_files})
        for d in check_dirs:
            if not os.access(d, os.W_OK):
                emit(t("dryrun.output_not_writable", path=d), level="warning")
        if output_dir is not None:
            emit(t("run.plan_output_dir", path=output_dir.resolve()), level="summary")
        # 打印预处理过滤列表，和真实运行保持一致
        if precheck_skipped:
            emit(t("run.dryrun_precheck", count=len(precheck_skipped)), level="summary")
            for mf, reason in precheck_skipped:
                emit("  " + t("skip_entry", path=str(mf), reason=reason), level="summary")
        used_names: set = set()
        pbar = create_progress_if_needed(args, ebook_files, t("progress.desc.dry_run"))
        try:
            for mf in ebook_files:
                if pbar is not None:
                    pbar.set_postfix_str(truncate_name(mf.name))
                out = target_cbz_path(mf, output_dir, flatten=args.flatten, input_root=input_root, used_names=used_names)
                state_tag = t("tag.will_skip") if out.exists() and not args.overwrite else t("tag.pending")
                emit(f"  {state_tag} {mf} -> {out}", level="summary")
                if pbar is not None:
                    pbar.update(1)
        finally:
            if pbar is not None:
                pbar.close()
        emit(t("run.dryrun_end"), level="summary")
        return

    emit(t("run.start", count=len(ebook_files)))

    total_start = time.perf_counter()
    success = 0
    success_cbzs = []
    skipped_files = []
    failed_files = []
    interrupted = False
    used_names: set = set()
    pbar = create_progress_if_needed(args, ebook_files, t("progress.desc.convert"))
    try:
        for mf in ebook_files:
            if pbar is not None:
                pbar.set_postfix_str(truncate_name(mf.name))
            file_start = time.perf_counter()
            timed_out, converted = run_with_timeout(
                ebook_to_cbz, args.timeout,
                mf, delete_original=args.delete, prefer=args.prefer,
                drop_extra=args.drop_extra, overwrite=args.overwrite,
                output_dir=output_dir, compress=_compress_level,
                flatten=args.flatten, input_root=input_root, used_names=used_names,
                comicinfo=not args.no_comicinfo,
            )
            file_elapsed = time.perf_counter() - file_start
            if timed_out:
                emit(t("run.timeout", name=mf.name, seconds=args.timeout), level="error")
                failed_files.append(mf)
            else:
                result, status = converted
                if status == ConvStatus.OK:
                    success += 1
                    success_cbzs.append(result)
                elif status == ConvStatus.SKIP:
                    skipped_files.append(mf)
                elif status == ConvStatus.FAIL:
                    failed_files.append(mf)
            emit(t("run.elapsed", name=mf.name, seconds=f"{file_elapsed:.2f}"))
            if pbar is not None:
                pbar.update(1)
    except KeyboardInterrupt:
        # Ctrl+C：中断主循环，但仍输出已完成部分的汇总（临时目录由 ebook_to_cbz 的 finally 清理）
        interrupted = True
        emit(t("run.ctrl_c"), level="summary")
    finally:
        if pbar is not None:
            pbar.close()

    total_elapsed = time.perf_counter() - total_start

    emit(t("run.done", success=success, total=len(ebook_files)), level="summary")
    if interrupted:
        emit(t("run.interrupted_note"), level="summary")
    emit(t("run.stats", success=success, skip=len(skipped_files), fail=len(failed_files)), level="summary")
    if success_cbzs:
        if _short_summary:
            emit(t("run.output_short", count=len(success_cbzs)), level="summary")
        else:
            emit(t("run.output_header"))
            for cbz in success_cbzs:
                emit(f"  {cbz}")
    if skipped_files:
        emit(t("run.skipped_header", count=len(skipped_files)), level="summary")
        if not _short_summary:
            for mf in skipped_files:
                emit(f"  {mf}", level="summary")
    if failed_files:
        emit(t("run.failed_header", count=len(failed_files)), level="summary")
        for mf in failed_files:
            emit(f"  {mf}", level="summary")
    emit(t("run.total_elapsed", seconds=f"{total_elapsed:.2f}"), level="summary")


if __name__ == "__main__":
    main()
