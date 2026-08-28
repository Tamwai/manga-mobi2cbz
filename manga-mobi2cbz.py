#!/usr/bin/env python3
# Copyright (C) 2026 Tamwai
# SPDX-License-Identifier: GPL-3.0-only
"""
manga-mobi2cbz — 将 mobi/azw/azw3/epub 电子书漫画文件批量转换为 cbz 格式（OPF spine 排序 + 封面兜底增强版）

用法:
    python manga-mobi2cbz.py <目录或文件路径> [--language auto|zh-CN|zh-TW|ja|en] [--delete] [--prefer mobi7|mobi8|auto] [--ext-priority EXTS] [--drop-extra] [--drop-small] [--overwrite] [--timeout SECONDS] [--output-dir DIR] [--flatten] [--dry-run] [--rename[=TEMPLATE]] [--no-color] [--progress auto|on|off] [--quiet] [--short-summary] [--compress LEVEL] [--inspect sample|all] [--no-comicinfo] [--double-page auto|NUM|off] [--setinfo FIELD=VALUE] [--unpack] [--json] [--json-out FILE|auto] [--debug] [--log FILE]

示例:
    # 转换整个文件夹（递归搜索所有 .mobi/.azw/.azw3/.epub）
    python manga-mobi2cbz.py "D:\\ComicsLibrary\\"

    # 转换单个文件
    python manga-mobi2cbz.py "D:\\ComicsLibrary\\Vol.01.mobi"

    # 转换后自动删除原始电子书
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --delete

    # 双目录 mobi 时保留 mobi7
    python manga-mobi2cbz.py "D:\\ComicsLibrary\\Vol.01.mobi" --prefer mobi7

    # 目录中有未被收集的多余图片时放弃追加（默认追加到 cbz 末尾）
    python manga-mobi2cbz.py "D:\\ComicsLibrary\\Vol.01.mobi" --drop-extra

    # 已存在 cbz 时强制重新生成（覆盖旧文件）
    python manga-mobi2cbz.py "D:\\ComicsLibrary\\Vol.01.mobi" --overwrite

    # 单文件转换超过 300 秒自动跳过（防止损坏/加密电子书卡死批量任务）
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --timeout 300

    # CBZ 输出到自定义目录（默认保留相对输入的子目录结构，如 Sample Series/001.mobi → E:\\CBZ_Output\\Sample Series\\001.cbz）
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --output-dir "E:\\CBZ_Output"

    # 平铺输出：所有 CBZ 直接放到输出目录根下（同名未指定 --overwrite 时跳过）
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --output-dir "E:\\CBZ_Output" --flatten

    # 试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --dry-run

    # 强制显示文件级进度条（默认关闭；auto 在 TTY 且文件数≥2 时自动显示）
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --progress on

    # 静默模式批量转换，只显示错误与汇总；完整输出写入日志文件
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --quiet --log "D:\\ComicsLibrary\\convert.log"

    # 以 deflate 压缩级别 9 打包（PNG 源收益明显，JPEG 源没必要）
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --compress 9

    # 检查模式：随机抽查 1 个（默认 sample）；all 检查全部电子书（元数据/结构/图片/分辨率/DRM），不生成 CBZ
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --inspect

    # 检查全部电子书内部信息（--inspect all 等价旧 --inspect-all）
    python manga-mobi2cbz.py "D:\\ComicsLibrary" --inspect all

    # 覆盖/新增 ComicInfo 字段（可多次；VALUE 支持 %series/%number/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M）
    python manga-mobi2cbz.py "D:\\ComicsLibrary\\Vol.01.mobi" --setinfo "Series=Sample Series" --setinfo "Number=%number" --setinfo "Summary=hello, world"

    # 解包查看：只解压不转换，输出到源文件所在目录的「源名_扩展名」子目录
    python manga-mobi2cbz.py "D:\\ComicsLibrary\\Vol.01.mobi" --unpack

    # 重新打包：把已解包的 CBZ 解包目录（目录名以 .cbz 结尾）打包回 CBZ
    python manga-mobi2cbz.py "D:\\ComicsLibrary\\Vol.cbz" --repack

参数:
    --language LANG  输出语言：auto 按系统语言自动选择（zh 前缀→中文，
                     zh-TW/zh-Hant→繁体中文，ja/Japanese→日文，
                     否则→英文），或指定 zh-CN/zh-TW/ja/en
    --delete         转换成功后删除原始电子书文件
    --prefer         双目录 mobi（mobi7/mobi8）时保留哪份：auto 默认优先 mobi8、
                     空壳自动回退 mobi7；指定 mobi7/mobi8 时，指定目录为空
                     也自动回退另一份（默认 auto）
    --ext-priority EXTS 同目录同名（仅扩展名不同）时保留哪种格式，
                     逗号分隔、顺序即优先级从高到低，仅接受
                     mobi/azw/azw3/epub，默认 azw3；优先级未覆盖时
                     回退兜底顺序 azw3→epub→mobi→azw；与 --prefer（双目录）无关
    --drop-extra     丢弃指定格式/条件的图片（过滤器）：无值/extra=丢弃
                     目录外多余图（默认追加）；传格式词丢弃对应格式
                     （如 gif 丢 gif）；extra 可与格式组合；off/no/0=关闭
                     （多余图追加、不按格式丢弃）；过滤面与 --list-images 同源
    --overwrite      目标 cbz 已存在时强制重新生成（默认跳过）
    --timeout SECONDS 单文件转换超时秒数，超时自动跳过并计入失败（默认 600，0 表示不限制）
    --min-size BYTES  过滤小于指定字节的电子书（不带数字默认 1000，0 关闭，不传则关闭）
    --output-dir DIR CBZ 输出到指定目录（自动创建），默认保留相对输入的
                     子目录结构（如 Sample Series/001.mobi → DIR/Sample Series/001.cbz），
                     需要平铺时加 --flatten
    --flatten       仅与 --output-dir 联用：所有 CBZ 平铺到输出目录根下，
                     同名文件未指定 --overwrite 时跳过（SKIP），
                     指定时覆盖首选名；单独使用（无 --output-dir）将报错退出
    --dry-run        试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录
    --progress VAL   进度条显示策略：不传或 off 默认关闭；auto 在 TTY 且文件数≥2
                     且未用 --json/--json-out 时自动显示；on 强制显示
                     （旧 --no-progress 隐藏别名仍强制关闭，优先级最高）
    --quiet          静默模式：只显示错误与最终汇总（日志文件不受影响）
    --short-summary  精简汇总：成功/跳过文件只显示数量不列出路径，失败始终全路径
    --compress LEVEL zip 压缩级别 0-9：0=不压缩（默认，图片本身已压缩），
                     1-9=deflate 压缩（PNG 源有收益，级别越高越小但越慢）
    --inspect MODE   检查模式：sample 随机抽查 1 个（默认）；all 全量检查；
                     只解包读取内部信息（元数据/结构/图片/分辨率/DRM），
                     不生成 CBZ，结束自动清理临时目录
                     （旧 --inspect-all 隐藏别名等价 --inspect all）
    --no-comicinfo  不生成 ComicInfo.xml（默认生成：向 CBZ 根目录写入
                     Title/Series/Number/Writer/Publisher/Year/
                     LanguageISO/PageCount/Summary 等漫画元数据）
    --double-page   双页检测：图片宽/高 ≥ 阈值（默认 2.0）判为跨页横幅，
                     在 ComicInfo 写入逐页 <Page Type="DoublePage"/> 标记；
                     传数值调阈值，off/no/0 关闭（默认 auto 开启）
    --drop-small    丢弃小图：开启时"宽和高均小于中位数×比例"的图被丢弃
                     （默认比例 0.5，传数值调比例，off/no/0 关闭，默认关闭）；
                     封面小缩略图等自动命中，丢弃后 PageCount 按实际图数重算
    --setinfo FIELD=VALUE 设置 ComicInfo 字段（可多次，后出现覆盖先出现；
                     优先级最高，覆盖自动推断/元数据来源）。VALUE 支持
                     固定值或占位符：%series/%number/%title/%writer/%publisher/
                     %date/%language/%description/%filename/%leftN/%rightN/
                     %subN_M（%leftN=文件名前 N 字符，
                     %rightN=后 N 字符，%subN_M=第 N 字符起 M 个，1-based；
                     占位符对应值缺失时该字段不写入）。智能拆分：
                     仅当逗号后紧跟"字段名="时才拆分，否则逗号视为值的
                     一部分（如 Summary=hello, world 不拆分）。Manga 默认
                     不写入，需显式 --setinfo Manga=Unknown|No|Yes|YesAndRightToLeft
    --unpack        解包查看：只解压不转换，输出到各源文件所在目录的
                     「源名_扩展名」子目录（如 vol.cbz → vol_cbz/、
                     vol.mobi → vol_mobi/），与源文件不撞名，已存在时
                     再以 (N) 序号避让；_cbz 结尾的解包目录可直接被
                     --repack 重新打包；mobi 走 extract 保留完整结构，
                     cbz 走 extractall
    --repack       重新打包：把已解包的 CBZ 解包目录（目录名以 _cbz
                     结尾）重新打包回 CBZ，输出名还原为源文件
                     （vol_cbz → vol.cbz）；可配合 --setinfo 修改元数据，
                     目录里有 ComicInfo.xml 则原样带回（--setinfo 叠加
                     覆盖），无则生成基础版（--no-comicinfo 关闭）；
                     已存在默认跳过，--overwrite 覆盖，--output-dir
                     指定输出目录；执行前先列出待处理清单
    --log FILE       将全部输出追加写入指定日志文件
    --version        显示版本号

依赖: pip install mobi
要求: Python 3.10+

更新日志:
    v3.5.0 (2026-08-28)
        - 新增：--drop / --inspect 过滤器支持 - 前缀排除（负向条件，
          与逗号 OR / 加号 AND 由同一表达式引擎解析）
        - 变更：退出码语义细化——目标路径不存在退出 2；
          --repack 无可用解包目录 / 无 _cbz 目录退出 2 且计入失败 1；
          --unpack 解包失败退出 1；--inspect 异常退出 1；
          转换中 Ctrl+C 退出 130（128+SIGINT）
        - 新增：--repack 模式忽略 --rename 时给出提示
        - 修复：--drop-small 无效值错误文案矛盾（同时提示 off/no/0）
          改为"支持 auto 或数值(0~1)"
        - 修复：--setinfo 帮助与文件头示例中占位符 %% 误写为单 %
        - 修复：--unpack 目录撞名避让说明措辞（默认 源名_扩展名，
          撞名时以 (N) 序号避让）
        - 修复：--inspect 帮助补充 FILTER 语法说明（与 --drop 相同：
          逗号=OR、加号=AND、- 前缀排除）
        - 修复：四语 help.setinfo / help.rename 帮助文本中占位符
          %% 误写统一为单 %
        - 新增：--repack 处理清单（plan）每行标注推断输出文件名
          （解包目录名 → 输出.cbz），来源一目了然
        - 维护：回归测试退出码预期更新（目标不存在 1→2）
    v3.4.0 (2026-08-26)
        - 新增：退出码语义——0=全部成功（含全部跳过、无失败），
          1=存在转换失败文件（转换失败/DRM/校验失败等），
          2=参数用法错误（argparse 内置）
        - 变更：--inspect --json 精简输出新增 formats 汇总字段
          （各图片格式数量分布），供脚本化消费
        - 维护：回归测试增至 56 项（新增退出码语义 / inspect formats / 版本号护栏）
    v3.3.0 (2026-08-25)
        - 新增：--drop [EXPR] 统一丢弃入口——无值 = 丢弃目录外多余图
          （同旧 --drop-extra 无值语义）；格式词 / 条件词 /
          small[=比例] 均可；多条件逗号 = OR、加号 = AND、- 前缀排除，
          off 关闭；旧 --drop-extra / --drop-small 降为隐藏别名并入
        - 新增：--inspect [MODE][,FILTER]——在 sample/all 基础上可附
          过滤器（如 all,small=0.6），命中条件的图片输出数量 + 文件名
          清单（含尺寸）；--json 对应新增 filter_hits 结构
        - 新增：small 独立带参条件词——无参 / auto = 默认比例 0.5，
          可传 0~1 数值；四语别名（异常小图 / 異常小圖 / 異常小画像 /
          極小画像）均可带参
        - 变更：三链路（转换丢弃 / inspect 预览 / list 清单）统一由
          --drop 表达式驱动，小图面积口径单一来源
        - 变更：--drop-extra / --drop-small 从 --help 隐藏（兼容仍可用）
        - 维护：回归测试增至 46 项
    v3.2.0 (2026-08-24)
        - 新增：[异常] 行内恒显标记（首列，汇总该行任一异常），一眼可见
        - 新增：[推断] 独立推断标记，替代"疑似"：旋转跨页/缩略图/封面补位
          等推断性标注去"疑似"，仅凭尺寸/文件名推断、非 OPF 明确声明者标
          [推断]（OPF guide 封面/动图/多余不标）；新增四语筛选别名
          inferred/推断/推斷/推測/推定
        - 变更：模式列统一英文规范名（index/gray/rgb/graya/rgba），
          取消四语本地化键，省维护
        - 变更：小图判定改面积口径（宽×高 < 面积中位数×比例），并与
          --drop-small 比例统一——标了即会丢；--list-images /
          --inspect 预览 / 转换丢弃三条链路同一口径
        - 变更：--drop-small 关闭时不再标 [小图]（与"标了即会丢"一致）
        - 维护：回归测试同步（34 项全通过）
    v3.1.1 (2026-08-24)
        - 修复：--unpack 的 help 文案残留旧「自动加序号避让」描述，
          与 v3.1.0 起「源名_扩展名」统一命名矛盾；四语同步更正
        - 维护：--repack 的 help 注明 --rename 不适用于本模式；
          --list-images 的 help 补充 [追加]/[舍弃]/[筛选] 处置标记说明
        - 维护：回归测试扩充至 34 项（新增 repack 还原+ComicInfo 叠加、
          _safe_zip_extract 的 C:foo 逃逸、name 原子 WindowsPath 三组）
    v3.1.0 (2026-08-24)
        - 新增：过滤表达式多语言别名（中/繁/日/英），支持直接粘贴
          [标签]（自动剥壳），如 封面/[封面]/cover/表紙 等价
        - 新增：统计标签筛选词 超大页/疑似旋转跨页/异常
          （overscale / rotated_double / anom）及四语别名
        - 新增：文件名子串筛选 name=关键词（大小写不敏感，含扩展名）
        - 新增：处置筛选 追加/舍弃/筛选（append/drop/filter）；
          --drop-extra 同步支持全部新标签词
        - 新增：--repack 重新打包模式（把已解包的 _cbz 解包目录打包回
          CBZ，目录名以 _cbz 结尾识别，支持批量，执行前先列出待处理
          清单；目录内 ComicInfo.xml 有则原样带回、无则生成基础版，
          --setinfo 叠加覆盖，--no-comicinfo 关闭；输出名还原为源文件
          （vol_cbz → vol.cbz），已存在默认跳过，--overwrite 覆盖）
        - 变更：--unpack 解包目录名统一为 源名_扩展名（vol.cbz →
          vol_cbz/，vol.mobi → vol_mobi/），与源文件不撞名，已存在时
          再以 (N) 序号避让；解包/重新打包均先输出处理清单再执行
        - 修复：_safe_zip_extract 补驱动器相对路径（C:foo）逃逸防护
        - 修复：cover/extra 筛选词未覆盖封面补位图（cover_extra），
          封面筛选此前命中 0；封面补位不再计入异常明细
        - 修复：_parse_atom 对 8bit 解析崩溃、name 原子在 WindowsPath
          上的崩溃
        - 维护：新增回归测试 tests/test_mobi2cbz.py（30 项）
    v3.0.0 (2026-08-24)
        - 变更：许可证由 MIT 切换为 GPL-3.0-only（因依赖 mobi 库为
          GPL-3.0-only，公开发布即构成分发）；LICENSE 替换为 GNU GPL v3，
          三语 README 许可章节同步更新
        - 修复 NCX 定位漏检：新增 find_ncx 统一定位（优先按 OPF
          manifest media-type=application/x-dtbncx+xml，其次 spine 的
          toc 属性指向 id，最后兜底 *.ncx），兼容把 NCX 命名为
          xml/vol.nav 等非 .ncx 扩展名的封装；parse_ncx_toc /
          parse_ncx_entries 均改用
        - 修复 --inspect 目录(NCX) 计数口径：仅统计 <navLabel><text>
          目录条目（此前把 docTitle/docAuthor 也算入，条目数虚高 1-2）
        - 新增：target 支持 glob 通配符模式（* / ?，如 *.epub、卷*/001.mobi），
          命中多个文件时按扩展名过滤后作为平铺文件列表处理；处理当前目录可写 .
        - 新增：--top-only 仅处理 target 目录顶层电子书，不递归子目录
        - 破坏性：进度条默认关闭。不再智能自动显示，需显式
          --progress on / auto 开启；统一为 --progress auto|on|off
          （不传或 off=关闭；auto=TTY 且文件≥2 且未用 --json 时显示）
        - --inspect 收敛为 --inspect [sample|all]（默认 sample=旧抽查 1 个，
          all=旧 --inspect-all）；旧 --inspect-all 单独使用自动启用 --inspect
          的黑盒行为删除，需显式 --inspect all
        - 兼容：旧 --progress/--no-progress、--inspect-all 保留为隐藏别名
        - 安全修复(P0)：ET.parse 全部替换为 safe_et_parse，禁用外部实体
          解析，消除 XXE 注入风险（7 处调用点）
        - 转换链路补充超时残留清理提示 run.timeout_residue（此前仅 inspect
          链路有）；移除实跑链路 used_names 死参数
        - 卷号推断：4 位年份（19xx/20xx）不再误判为卷号（如 "Series 2024"）
        - 魔数 65536 提升为命名常量 HEAD_READ_BYTES，注释说明取值依据
        - 错误状态字符串收敛为 ConvStatus/InspectStatus 枚举（续）
        - 维护性：_VOLUME_PATTERNS 补充匹配语义与排序说明注释；修 validate_cbz
          后错位游离注释归位至 collect_ebook_files
        - 新增 --inspect 的 JSON 输出：--json 每文件一行精简 JSON
          （status/series/number/source/page_count/drm，status 取值
          ok/drm/invalid/noimg/timeout/fail），--json-out 落盘全量
          （含 spine/toc 与 summary）；inspect_ebook 改为返回
          (InspectStatus, info dict) 结构化元组
        - --dry-run 配合 --setinfo 时逐文件预览 ComicInfo 字段变化
          （~ 字段: 旧 → 新；仅新增标 +；值不变省略），不写盘
        - 新增 --list-images [FILTER] 只读图片清单：不转换、不写 CBZ、
          不生成 ComicInfo、不落盘；按 spine 阅读顺序（CBZ 按 zip 自然
          排序）列出序号/文件名/分辨率/大小/模式色深/方向/目录/标记，
          末尾附全量统计（格式/模式色深/尺寸分布/双页横幅/动图/小图/
          异常明细）；CBZ 直读 zip 无目录列；FILTER 过滤表达式与
          --drop-extra 同源（逗号=OR、+ =AND），配 --json 每文件一行、
          --quiet 仅计数
        - --drop-extra 改造为通用丢弃过滤器（布尔 → nargs='?'）：
          无值=extra 丢全部多余图（等价旧 --drop-extra）；带值按格式/
          res/size/方向/模式/位深/标记条件丢弃（如 --drop-extra gif、
          --drop-extra gif,extra），off/no/0 关闭；执行顺序：多余图丢弃
          → 去重 → 条件过滤 → 小图丢弃，与 --drop-small 可叠加
        - --inspect 省略号统一为英文 ...：spine 图片前 5 张后追加
          "...（共 N 张）" 行，目录(NCX)/目录(EPUB3 nav) 预览截断改用
          英文 ...（仅实际数量超出显示数量才显示）
        - 修复：--drop-extra 的 cover 原子此前为哑弹（封面存于独立
          attrs["cover"]，mark 集合不含封面，--list-images=cover 命中 0）；
          现按 OPF guide 封面 + 文件名关键词（COVER_KEYWORDS）识别封面打标，
          list 与转换两链路均生效，--drop-extra cover 可可靠舍弃封面
        - 修复：DRM 误报——get_drm_flag 原读 PalmDB 头偏移 12 的 2 字节，
          该位置落在 name 字段内（书名/文件名含 '-' '_' 等即非 0 误报，
          如 [Anon] 系列 mobi 被误判加密无法转换）；改为读 PalmDB
          attributes（偏移 32）copy-protection 位 + PalmDOC header
          encryption type（偏移 78+8*nrec+0x0E，权威判据，0=无加密）
        - 修复：--inspect 遇 DRM 标记不再跳过解包——标记降级为信息项，
          仍尝试解包；解出图片→正常检查并标注"有标记但可读"（status=ok，
          drm 字段如实带标记），解包失败/0 图且带标记→判 DRM；与转换
          链路"先尝试解析"语义统一，打位未加密的假上锁文件可完整检查
        - 卷/话号推断增强（Kavita 语义对齐）：新增话/章族词库（話/话/
          話数/话数/Chapter/Ch./ch/chp/c/Episode/화/회/回/集/บทที่/ตอนที่/Глава），
          支持紧贴式（c001/ch001/v01/T3/S01）、卷+章同现（Vol.0001
          Ch.0001、Том 1 Глава 3）、卷/章区间（v16-17、c001-006 取起始
          值）、小数（025.5）、尾字母半话（153b→153.5）、多语言卷补漏
          （冊N/1권/장N/季N/第N季）、括号/方括号注释剔除；修复英文标记词被吞入
          系列名与区间取尾数的旧缺陷；4 位年份防护保留
        - 新增 --rename 重命名输出 CBZ 文件名（可选模板，默认关闭）：无值=
          默认模板（系列名+自动标记前缀，前缀按类型自动选：整卷[Vol.x]/单话
          [Ch.x]/卷+章[Vol.x][Ch.x]/无类型[x]，连话話005-006 标 [Ch.5-6]）；
          占位符 %series/%number/%volume/%title/%writer/%publisher/%date/
          %language/%description/%filename/%leftN/%rightN/%subN_M 及
          %03number 补零；来源优先级：文件名推断 > 文件自带元数据
          (OPF/ComicInfo.xml) 兜底，setinfo 不参与；输入为已有 .cbz 时进入
          独立重命名模式（只改名不转换，可与其他模式叠加）；建议配合
          --dry-run 先预览
        - 新增 --no-color 禁用 ANSI 颜色输出（即使终端支持也不上色）；
          日志/JSON/管道输出本就不含颜色
        - 撞名提示增强：--rename 跳过时区分两类提示（rename_cbz.skip_existing=
          磁盘同名建议加 --overwrite；rename_cbz.skip_conflict=本批撞名建议
          调整命名模板），dry-run 与非 dry-run 分支均区分，JSON reason 字段
          分别写 existing/conflict
        - 修复 --dry-run 的 JSON 输出：dry-run 配合 --json/--json-out 时输出
          结构化 JSON（此前契约缺失、文档称不输出），每条记录带 dry_run 布尔
          标记区分试运行与真实运行，dry-run 状态取值 will_skip/pending
        - 修复 --rename 的 %title% 占位符：OPF 分支补 dc:title 兜底读取
          （此前 %title% 仅取 ComicInfo.xml <Title>，epub 无 ComicInfo 时
          恒空；现与 series/number 的 OPF 兜底一致，来源优先级：OPF
          dc:title → ComicInfo.xml <Title>）
        - 新增占位符 %writer/%publisher/%date/%language/%%description
          （--rename 与 --setinfo 均支持）：OPF 读 dc:creator/dc:publisher/
          dc:date/dc:language（经 normalize 归一）/dc:description，ComicInfo
          读 Writer/Publisher/LanguageISO/Summary；date 原样保留（如
          2024-01-15，ComicInfo 无对应字段）；%language 缺失时按未归一值
          原样兜底，均缺失时占位符渲染为空（--setinfo 则字段不写入）
        - 新增 --setinfo 占位符与固定文本混用（如 "%writer·重制"、
          "第%number话"）：与 --rename 一致的全局替换，缺失值渲染为空串、
          未知占位符原样保留；整段恰为单个已知占位符时保留原语义（缺值
          不写入该字段）
        - 修复 NCX/NAV 目录解析顺序与实体：parse_ncx_entries 改栈建树 +
          文档顺序先序遍历（父条目恒在子条目前、同层保持文档顺序），标题
          剥离嵌套标签并解码 HTML 实体（&amp;→&）；parse_nav_entries
          同步补实体解码
        - 维护性：脚本头部补充 SPDX-License-Identifier: GPL-3.0-only
        - 修复：gif_frame_count 帧数误报——head.count(b"\x2c") 扫描
          LZW 压缩数据改为按 GIF 结构块解析（仅计数图像描述符 0x2C，
          子块按边界整体跳过不读内容），静态 GIF 压缩数据内任意 0x2C
          不再被误计为帧而误标 animated；头部截断安全退出
        - 安全修复(P0)：_safe_zip_extract 补 is_absolute() 检查，拦截
          盘符（C:/）与 UNC（//server/share）zip-slip 越界写盘
        - 修复(P1)：validate_cbz 读尾改 seek——文件 >70KB 时仅读末尾
          ZIP_EOCD_READ_TAIL(70000) 字节，大 CBZ 校验内存峰值由
          O(文件大小) 降为 O(70KB)
        - 修复(P1)：build_cbz_image_attrs 改 zf.open() 流式取头，仅
          解压 HEAD_READ_BYTES 字节，大图条目不再整图解压进内存
        - 维护性(P2)：_fill_small_mark 硬编码 0.5 替换为常量
          DEFAULT_DROP_SMALL_RATIO（语义与行为不变）
    v2.5.1 (2026-08-20)
        - 修复 --setinfo/--inspect/--unpack 模式下去重误删同名 .cbz：
          转换产物 .cbz 不参与 mobi/azw/azw3/epub 同名去重，保证已转
          CBZ 可被修改/检查；flatten 平铺同名冲突跳过新增专用提示
        - 维护性：清理实跑链路 used_names 死参数（dry-run 分支保留）
        - 新增 LICENSE 文件（MIT）
    v2.5.0 (2026-08-20)
        - Manga 默认不再自动写入 ComicInfo：双页检测只生成 <Pages> 逐页
          DoublePage 标记，不再附带 <Manga>Yes</Manga> 声明；Manga 改由
          --setinfo Manga= 显式指定，取值限官方 v2.0 枚举
          Unknown/No/Yes/YesAndRightToLeft，非法值 warning 忽略
        - --setinfo 白名单扩展：新增 CommunityRating（0-5 评分）/
          MainCharacterOrTeam / Review 三个官方 v2.0 字段（39→42）
        - --ext-priority 支持 epub：仅接受 mobi/azw/azw3/epub，优先级
          未覆盖时兜底顺序调整为 azw3→epub→mobi→azw
        - 无图提示按扩展名分流：epub 无图时改用中性文案（确认含漫画图
          且未加密），不再误报 Kindle DRM；mobi 族仍提示 DRM
        - --help 四语言文案同步 .epub（help.description/help.target/
          help.ext_priority），docstring 说明同步
        - 新增 --drop-small 丢弃小图：默认关闭，开启时按"宽和高均小于
          中位数×比例"丢弃异常小图（默认比例 0.5，可用 --drop-small 数值
          调比例，off/no/0 关闭）。逐图读宽高复用 image_dimensions（不引
          新依赖）；丢弃后 ComicInfo PageCount 按实际剩余图数重算；
          汇总/--log/--json 新增『丢弃小图』计数；--inspect 预览标记
          『开启 --drop-small 时将丢弃 N 张』；封面小缩略图等自动命中
    v2.4.0 (2026-08-20)
        - 新增 EPUB 输入支持：SUPPORTED_INPUT_EXTENSIONS 扩展 .epub；
          ebook_to_cbz / inspect / unpack 按扩展名分流（epub 走 zipfile
          安全解包，mobi/azw/azw3 仍走 mobi.extract），复用现有 OPF spine
          提取与 ComicInfo 元数据链路
        - EPUB 封面兜底增强：get_opf_guide_cover_href 新增
          <meta name="cover"> 与 manifest properties="cover-image" 两来源
          （EPUB2/EPUB3 约定），并修正封面 href 相对 OPF 目录解析
        - EPUB 无 EXTH 头：read_exth_metadata 自然返回空，inspect 改从
          OPF dc:metadata 补充标题/作者/语言等；get_drm_flag 对 epub 直接
          放行（zip 容器无 PalmDB DRM 字段，避免误报）
        - --prefer 对 epub 静默忽略（无 mobi7/mobi8 双目录，天然单目录）
        - EPUB3 nav 目录识别：--inspect 优先从 OPF manifest
          properties="nav" 定位 nav 文档（兜底 *nav*.xhtml），解析
          <nav epub:type="toc"> 内 <a> 标题；与 EPUB2 toc.ncx 同时显示
    v2.3.1 (2026-08-19)
        - 修复校验顺序：先对临时文件 validate_cbz 校验、通过后才
          os.replace 覆盖目标；失败仅清理 tmp，旧 CBZ 保留；ComicInfo
          生成失败不再删除已有目标 CBZ
        - 修复 Ctrl+C（KeyboardInterrupt）残留 .tmp：finally 兜底清理
        - 修复 --setinfo 未知占位符：白名单外输出 warning 后按原样写入
          （新增 i18n 四语言键）
        - 修复 sanitize：补充 ASCII 控制字符 + 去除尾部点/空格
        - 修复 find_opf 多 OPF 命名优先级：content.opf / package.opf 优先
        - 维护性：清理残留 docstring；_strip_html 改用 HTMLParser
        - 文档：--help 四语文案补充（--setinfo 多次传入 / 已有 .cbz
          就地修改 / --json 仅转换与修改模式输出 / 2>&1 混流提示），
          README 三语同步
    v2.3.0 (2026-08-19)
        - 新增 --json：stdout 输出单行紧凑 JSON（给 AI/管道读取），
          开启时屏蔽人类可读文本输出
        - 新增 --json-out：转换结果写本地 JSON 文件；nargs='?' 与 --log
          同模式（省略文件名自动生成时间戳文件，或指定路径），缩进格式
        - 统一结果结构：summary 统计 + files 逐文件记录（状态/输出/耗时/
          失败原因），--json 与 --json-out 共用一份 schema，可同时开启
        - 修复原子替换：转换分支 CBZ 打包改为先写 xxx.cbz.tmp 临时
          文件，全部成功后再 os.replace 覆盖目标；删除打包前 unlink 旧
          文件与失败分支的 cbz 删除，异常仅清理半成品 tmp，消除 Ctrl+C/
          中途崩溃残留残缺 CBZ、以及覆盖失败丢旧文件的数据丢失风险
          （modify_cbz_comicinfo 原有原子替换逻辑保持一致）
        - 修复 --inspect PageCount 非数字值：int 转换失败由静默
          pass 改为输出 warning（新增 i18n 键 inspect.pagecount_non_numeric）
        - help.timeout 文案补充：超时后底层解包线程可能后台残留
    v2.2.0 (2026-08-18)
        - 新增 CBZ 修改模式：输入为已有 .cbz 且带 --setinfo 时直接修改
          其 ComicInfo.xml，读原 XML → 覆盖指定字段、未指定字段保留原值
          （含命名空间字段）→ 临时文件 + os.replace 原子替换；纳入
          --dry-run 预览 / 汇总统计 / --log
        - setinfo 白名单：--setinfo 字段名需在 ComicInfo 标准字段白名单
          内（39 个简单字段，Pages 复杂结构排除），白名单外字段输出
          warning 并忽略
        - 源文件更新自动重转：断点续跑时比较源文件与目标 CBZ 的 mtime，
          源文件更新则自动重新转换
        - --unpack / --setinfo 支持 CBZ 输入：收集阶段在 --unpack 或
          --setinfo 时也收集 .cbz 文件
        - --prefer auto（默认）：双目录 mobi 默认自动选择，优先 mobi8，
          mobi8 无图片自动回退 mobi7；明确指定 mobi7/mobi8 时该目录无
          图片自动回退另一份
        - Summary HTML 清理：ComicInfo 的 Summary 字段自动去除 HTML 标签
          （纯文本落盘）
        - 封面来源标记：ComicInfo 的 Notes 字段追加 CoverSource
          （OPF guide / 文件名匹配）
        - CBZ 预处理：.cbz 输入同样执行 0 字节 / --min-size 检查
        - --inspect PageCount 一致性检查：比对 CBZ 内 ComicInfo 的
          PageCount 与实际图片数，不一致时提示
        - --unpack 路径安全：cbz 解包增加 zip-slip 路径穿越防护（拒绝
          ../ 与绝对路径条目），并输出解包汇总
        - 多 OPF 提示：目录下存在多个 .opf 时输出 warning 并取第一个
        - 损坏 CBZ 重转原因：断点续跑遇损坏 CBZ 自动重转时输出
          validate_cbz 的具体失败原因
        - HTML 图片路径兼容：提取 <img> 时去除 src 中的 query/fragment
          （? / #）再拼本地路径
        - 目录创建时机：目标 CBZ 已存在且将 SKIP 时不再提前创建输出目录
        - 代码卫生：ebook_to_cbz 返回类型注解补全三元组；_auto_language
          末尾显式标注
    v2.1.0 (2026-08-17)
        - 断点续跑（默认行为）：目标 CBZ 已存在且 validate_cbz 校验有效
          时直接 SKIP，损坏/无效自动重转；--overwrite 无条件覆盖
        - 失败分类：ebook_to_cbz 返回三元组 (result, status, reason)，
          失败原因分类 timeout/drm/corrupt/no_images/comicinfo/verify/other，
          主流程新增 failed_reasons 统计并在汇总输出
        - --inspect 支持 CBZ：合并进 inspect_ebook，纯 zipfile 读取
          不解压；抽出 image_dimensions_bytes(bytes) 复用
        - --inspect 输出增强：封面行加分辨率+大小，格式统计加总文件数，
          Spine 前 5 列表每行加宽高
        - 新增 --setinfo FIELD=VALUE（可多次）：覆盖/新增 ComicInfo 字段，
          优先级最高；VALUE 支持固定值/%series/%number/%title/%filename/
          %leftN/%rightN；智能拆分（逗号后紧跟字段名=才拆）；CBZ 修改
          模式直接重写 zip；--inspect 预览块同步应用
        - ComicInfo 并入同一次 zip 写入：删除 write_comicinfo 函数，
          Step4 with 块内 zf.writestr
        - --log 自动命名：nargs="?" + const="auto"，auto 时生成
          manga-mobi2cbz_YYYYMMDD_HHMMSS.log（当前目录）
        - 新增 --unpack 解包查看：只解压不转换，mobi 走 extract 保留
          完整结构，cbz 走 extractall；默认解到文件名同名目录，已存在
          自动加序号避让 (2)(3)
    v2.0.2 (2026-08-17)
        - infer_series_number 支持括号后缀：文件名带 "(作者)" 等括号
          内容时不再阻断卷号推断
        - 纯卷标记（Vol.01 / 第 01 卷 / 01巻 等）只返回卷号
          (None, number)，不再返回 (None, None)，ComicInfo 可写入 Number
        - --flatten 同名处理改为 SKIP/--overwrite：平铺输出根下同名
          文件不再自动编号重转 (2).cbz，未指定 --overwrite 时跳过
          （SKIP），指定时覆盖首选名；dry-run 与实跑保持一致
        - 移除已无引用的 unique_path 函数
        - 修复 PageCount 一致性：物理去重提前到 ComicInfo 生成之前，
          PageCount 与打包均用去重后实际写入数
        - 修复 run_with_timeout 跨版本：except 同时捕获内置 TimeoutError
          与 concurrent.futures.TimeoutError（Python 3.10 兼容）
        - 修复 infer_series_number 点号失效：改用 path.name 手动去扩展名，
          "Sample Series Vol.01" 等点号卷号可正确推断
        - LanguageISO 白名单 + alias：ISO 639-1 全量 184 个白名单校验，
          新增 jp→ja / cn→zh / zhtw→zh 等常见别名
        - Year 严格日期解析：优先完整日期字段，范围/多值（2001-2005）
          返回 None
        - emit warning 在 --quiet 下可见
        - EXTH 循环变量 t 改名 type_id，避免遮蔽全局 t()
        - 正则 img src 提取补 unquote，与 HtmlImgParser 兜底路径一致
        - --language 参数容错：支持 zh/cn/zhtw/jp 等常见写法，
          新增 _normalize_lang 规范化（argparse 移除 choices 限制）
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
         ）；"Sample Series Vol.01" 等正常推断不受影响

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
          重名自动唯一化 base.cbz → base (2).cbz → ...，不静默覆盖、不跳过
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

__version__ = "3.5.0"

SCRIPT_NAME = "manga-mobi2cbz"

import glob
import json
import locale
import os
import re
import sys
import time
import random
import struct
import shutil
import tempfile
import zipfile
import argparse
import traceback
import statistics
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from html import unescape
from urllib.parse import unquote
from enum import Enum
from pathlib import Path
from datetime import datetime
from collections import Counter
import concurrent.futures
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
        "error.json_write_failed": "【警告】JSON 结果写入失败（{err}），路径: {path}",
        "error.ext_priority_empty": "--ext-priority 不能为空",
        "error.ext_priority_invalid": "--ext-priority 仅接受 mobi/azw/azw3/epub，收到: {p}",
        # ---- --help 文案 ----
        "help.description": "mobi/azw/azw3/epub 漫画批量转 cbz",
        "help.language": "输出语言：auto 按系统语言自动选择（zh 前缀→中文，zh-TW/zh-Hant→繁体中文，ja/Japanese→日文，否则→英文），或指定 zh-CN/zh-TW/ja/en（兼容 zh/cn/zhtw/jp 等常见写法）",
        "help.target": "电子书文件路径、包含电子书（.mobi/.azw/.azw3/.epub）的目录，或含 * / ? 的通配符模式（如 *.epub）；处理当前目录可写 .",
        "help.delete": "转换成功后删除原始电子书文件",
        "help.prefer": "双目录 mobi（mobi7/mobi8）时保留哪份：auto 默认优先 mobi8、空壳自动回退 mobi7；指定 mobi7/mobi8 时，指定目录为空也自动回退另一份",
        "help.ext_priority": "同目录同名（仅扩展名不同）时保留哪种格式：逗号分隔、顺序即优先级从高到低，仅接受 mobi/azw/azw3/epub，默认 azw3；优先级未覆盖时回退兜底顺序 azw3→epub→mobi→azw；与 --prefer（双目录选择）无关",
        "help.drop_extra": "丢弃目录外多余图（隐藏别名，已并入 --drop extra）：无值=丢弃目录外多余图（默认追加）；off/no/0=关闭；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "help.drop": "丢弃指定图片（统一丢弃入口）：无值/extra=丢弃目录外多余图（默认追加）；格式词丢弃对应格式（如 gif 丢 gif）；条件词过滤（small[=比例] 小图、超大页、疑似旋转跨页、异常、封面、宽高比等，支持中/日/英多语言别名）；off/no/0=关闭；多条件逗号=OR、加号=AND、- 前缀排除；过滤面与 --list-images 同源；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "help.overwrite": "目标 cbz 已存在时强制重新生成（默认跳过）",
        "help.timeout": "单文件转换超时秒数，超时自动跳过并计入失败（默认 600，0 表示不限制；超时后底层解包线程可能后台残留）",
        "help.min_size": "过滤小于指定字节的电子书；不带数字默认1000字节，0关闭大小过滤，不传则关闭；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "help.output_dir": "CBZ 输出到指定目录（自动创建），默认保留相对输入的子目录结构（如 Sample Series/001.mobi → DIR/Sample Series/001.cbz），加 --flatten 可平铺到目录根下",
        "help.top_only": "仅处理 target 目录顶层的电子书文件，不递归子目录",
    "help.flatten": "仅与 --output-dir 联用：所有 CBZ 平铺到输出目录根下，同名文件未指定 --overwrite 时跳过（SKIP），指定时覆盖首选名；单独使用将报错退出",
        "help.dry_run": "试运行：只扫描文件并打印转换流程，不实际解压打包、不创建输出目录",
        "help.progress": "进度条显示策略：auto 在 TTY 且文件数≥2 且未用 --json/--json-out 时显示；on 强制显示；off 强制关闭（默认 off 不显示）；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "help.no_progress": "强制关闭进度条（即使 TTY 且文件数≥2）",
        "help.quiet": "静默模式：只显示错误与最终汇总（日志文件不受影响）",
        "help.no_color": "禁用 ANSI 颜色输出（即使终端支持也不上色）；日志/JSON/管道输出本就不含颜色",
        "help.debug": "输出调试信息（debug 级到 stderr；日志文件始终记录）",
        "warn.cleanup_tmp_fail": "清理临时目录失败 {path}: {err}",
        "warn.disk_space": "磁盘空间不足：{label} {path} 剩余 {free_mb} MB < 估算需要 {need_mb} MB",
        "help.short_summary": "精简汇总：成功/跳过文件只显示数量不列出路径，失败文件始终全路径列出",
        "help.compress": "zip 压缩级别 0-9：0=不压缩（默认，图片本身已压缩），1-9=deflate 压缩（PNG 源有收益，级别越高越小但越慢）",
        "help.inspect": "检查模式：sample 随机抽查 1 个（默认），all 全量检查；可附过滤器 [MODE][,FILTER]（如 all,small=0.6）输出命中条件图的数量+文件名清单，FILTER 语法与 --drop 相同（逗号=OR、加号=AND、- 前缀排除）；只解包读取内部信息（元数据/结构/图片/分辨率/DRM），不生成 CBZ，结束自动清理临时目录；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "help.inspect_all": "检查全部电子书（等价 --inspect all，兼容旧命令）",
        "help.no_comicinfo": "不生成 ComicInfo.xml（默认生成：向 CBZ 根目录写入漫画元数据）",
        "help.double_page": "双页检测：不传/auto 开启（阈值 2.0）；数值调阈值；off/no/0 关闭（开启时写入逐页 DoublePage 标记，不写 Manga 声明；如需 Manga 请用 --setinfo Manga=）；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "error.double_page_invalid": "无效的 --double-page 值 '{value}'：支持 auto/数值/off/no/0",
        "help.drop_small": "丢弃小图（隐藏别名，已并入 --drop small）：转换时剔除尺寸明显偏小的图片（面积 宽×高 < 面积中位数×比例 判为小图；不传/auto=0.5，可传 0~1 数值调比例，off/no/0 关闭）；丢弃后 PageCount 按实际剩余图数重算；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "error.drop_small_invalid": "无效的 --drop-small 值 '{value}'：支持 auto 或数值(0~1)",
        "convert.drop_small": "  [清理] 丢弃小图 {count} 张{names}",
        "run.drop_small_total": "丢弃小图合计: {count} 张",
        "inspect.drop_small_preview": "  [提示] 图片中 {count} 张为小图（开启 --drop small 时将被丢弃）",
        "inspect.filter_hits": "  [命中] {count} 张图片命中过滤条件（--inspect 过滤器）",
        "inspect.filter_no_hit": "  [无命中] 没有图片命中过滤条件",
        "help.setinfo": "设置 ComicInfo 字段（可多次，格式 FIELD=VALUE；VALUE 支持 %series/%number/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M（%subN_M=第 N 字符起 M 个，1-based）；逗号后紧跟字段名=才拆分，值内含 Key= 结构请用多次 --setinfo 传入；Manga 取值限 Unknown/No/Yes/YesAndRightToLeft，默认不写；--setinfo 开启时输入中的已有 .cbz 会就地修改其 ComicInfo.xml）",
"help.rename": "重命名输出 CBZ 文件名（可选模板，默认关闭）。--rename 无值=默认模板（系列名+自动标记前缀）；标记前缀按类型自动选：整卷[Vol.x]/单话[Ch.x]/卷+章[Vol.x][Ch.x]/无类型[x]，连话（話005-006）标 [Ch.5-6]；占位符 %series/%number/%volume/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M 及 %03number 补零；来源优先级：文件名推断 > 文件自带元数据(OPF/ComicInfo.xml) 兜底，setinfo 不参与；%description 不建议用于文件名（内容可能过长），确需使用可配合 %subN_M 截取片段；建议配合 --dry-run 先预览；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "comicinfo.generating": "生成 ComicInfo.xml",
        "comicinfo.created": "已写入 ComicInfo.xml",
        "comicinfo.disabled": "ComicInfo.xml 已禁用（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml 无效或生成失败: {err}",
        "comicinfo.build_fail": "ComicInfo.xml 生成失败: {err}",
        "comicinfo.write_fail": "ComicInfo.xml 写入失败: {err}",
        "comicinfo.src.setinfo": "setinfo",
        "comicinfo.src.opf": "OPF 元数据",
        "comicinfo.src.inferred": "文件名推断",
        "help.log": "将全部输出追加写入日志文件（省略文件名时自动生成时间戳日志）；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "help.json": "在 stdout 输出单行紧凑 JSON 结果（给 AI/管道读取），开启时屏蔽人类可读文本；转换/修改模式为整体单行紧凑 JSON，inspect 模式每文件一行精简 JSON，dry-run 带 dry_run 标记输出，仅 unpack 模式不输出；进度条写 stderr 不与 JSON 混流，但 2>&1 合并重定向会混入",
        "help.json_out": "将转换结果写入 JSON 文件（省略文件名时自动生成时间戳文件，或指定路径；同 --json 仅转换/修改模式写入）；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "log.auto_named": "日志文件: {path}（自动命名）",
        "json.written": "JSON 结果已写入: {path}",
        "help.unpack": "解包模式：只解压不转换，输出到源文件所在目录的「源名_扩展名」子目录（如 vol.cbz → vol_cbz/），与源文件不撞名；_cbz 结尾的解包目录可直接被 --repack 重新打包",
        "unpack.done": "已解包 {name} -> {dir}",
        "help.repack": "重新打包：将已解包的 CBZ 解包目录（目录名以 _cbz 结尾）重新打包回 CBZ（输出名还原为源文件名，如 vol_cbz → vol.cbz），可配合 --setinfo 修改元数据（--rename 不适用于本模式）",
        "repack.none_found": "未找到 _cbz 结尾的解包目录: {path}",
        "repack.no_images": "[错误] {dir}：目录内未找到图片",
        "repack.skip_exists": "[跳过] {path} 已存在（--overwrite 强制覆盖）",
        "repack.done": "[完成] {name}：共 {count} 张图片，{size} MB",
        "repack.fail": "[失败] {dir} 重新打包失败: {err}",
        "repack.done_summary": "重新打包完成：成功 {ok} 个，失败 {fail} 个",
        "repack.plan": "将重新打包 {count} 个解包目录：",
    "repack.rename_ignored": "提示：--repack 模式不适用 --rename，已忽略（输出文件名由解包目录名推断）",
        "unpack.plan": "将解包 {count} 个文件：",
        "unpack.done_summary": "解包完成：成功 {ok} 个，失败 {fail} 个",
        "error.repack_need_dir": "repack 模式仅接受目录（_cbz 结尾的解包目录，或含 *_cbz 解包目录的父目录）: {path}",
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
        "dedupe.auto_fallback": "  [去重] 双目录，mobi8 为空壳，自动回退 mobi7",
        "dedupe.prefer_empty_fallback": "  [去重] 指定保留 {prefer} 但该目录无图片，自动回退 {fallback}",
        # ---- 目录对齐 ----
        "align.drop": "  [提示] 目录中 {count} 张图片未被收集，已按 --drop-extra 放弃{names}",
        "align.append": "  [提示] 目录中 {count} 张图片未被收集，已追加到末尾{names}",
        # ---- 【转换】转换流程 ----
        "convert.skip_exists": "  [跳过] 目标已存在: {name}",
        "convert.flatten_conflict_skip": "  [警告] 平铺同名冲突: {src} 与已存在的 {name} 同名，已跳过；如确定覆盖请用 --overwrite",
        "convert.skip_corrupt_reconvert": "  [提示] 目标 {name} 已存在但校验失败（{reason}），自动重新转换",
        "convert.overwrite": "  [覆盖] 将覆盖旧文件，重新生成: {name}",
        "convert.spine": "  [排序] 按 OPF spine 顺序（{count} 张图片）",
        "convert.spine_empty": "  [排序] spine 提取为空，兜底按文件名排序（{count} 张）",
        "convert.dedup_physical": "  [去重] 跳过 {count} 个物理重复文件（同一文件重复出现，未写入 CBZ）",
        "convert.no_opf": "  [排序] 未找到 OPF，兜底按文件名排序（{count} 张）",
        "convert.multi_opf": "  [排序] 检测到 {count} 个 OPF 文件，使用第一个: {first}",
        "convert.no_images": "  [失败] 未找到图片: {name}",
        "convert.drm_hint": "  [提示] 可能为 DRM 加密的 Kindle 漫画，mobi 库无法解密，请先去除 DRM 后再转换",
        "convert.drm_hint_epub": "  [提示] 该 EPUB 未解析出图片，请确认其包含漫画图片、且未加密",
        "convert.count_mismatch": "  [提示] 目录共 {total} 张图片，收集 {collected} 张，数量不一致",
        "convert.done": "  [完成] {name} ({count} 张图片, {size} MB)",
        "convert.verify_fail": "  [校验失败] {name}: {msg}，旧文件已保留",
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
        "inspect.drm_marked_try": " 提示: 头部带 DRM 标记，继续尝试解包",
        "inspect.drm_hint": " 提示: 头部带 DRM 标记且解包失败，内容可能加密，需先去除 DRM 再转换",
        "inspect.drm_but_readable": "  DRM: 有(头部标记)但内容可读(图片{count}张)",
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
        "inspect.nav_count": "  目录(EPUB3 nav): {count} 个条目 | 预览: {preview}",
        "inspect.nav_missing": "  目录(EPUB3 nav): 未找到",
        "inspect.dir_images": "  目录全部图片: {count} 张",
        "inspect.drm_suspected": "  DRM: 疑似(头部标记无但图片0张)",
        "inspect.cover_missing": "  封面文件未找到",
        "inspect.fmt_none": "  图片格式统计: 无图片可统计",
        "inspect.drm_bad_hint": "  提示: 疑似 DRM 加密或内容损坏，转换会失败，需先去除 DRM",
        "inspect.drm_none": "  DRM: 无(头部标记无+图片{count}张)",
        "inspect.cover_src_guide": "OPF guide 官方引用",
        "inspect.cover_src_filename": "文件名匹配",
        "inspect.cover_found": "  封面文件已找到: {name}（{src}）{dim} {size}",
        "inspect.fmt_stats": "  图片格式统计（共 {total} 张）: {parts}",
        "inspect.res_main_h": "主流高 {height} ({count}张, {pct}%)",
        "inspect.res_w_range": "宽 {min}~{max}",
        "inspect.res_main_w": "主流宽 {width} ({count}张, {pct}%)",
        "inspect.res_h_range": "高 {min}~{max}",
        "inspect.res_line": "  分辨率: {parts}",
        "inspect.res_summary": "  分辨率摘要: 主分辨率 {w}x{h} 共 {count} 张 ({pct}%)；异常小图 {small} 张",
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
        "run.no_ebooks": "未找到电子书文件（.mobi/.azw/.azw3/.epub）: {path}",
        "run.precheck_header": "预处理跳过 {count} 个文件：",
        "run.none_convertible": "无有效电子书文件可转换（全部被预处理过滤或同名去重）",
        "run.found": "找到 {total} 个有效电子书文件（预处理过滤 {pre} 个，同名去重 {dedup} 个）\n",
        "run.dryrun_banner": "[试运行] --dry-run 模式：仅扫描与打印流程，不实际解压打包、不创建输出目录",
        "dryrun.output_not_writable": "  [警告] 输出目录不可写: {path}，正式转换将失败",
        "run.plan_output_dir": "计划输出目录: {path}（仅正式转换时自动创建）",
        "run.dryrun_precheck": "试运行预处理跳过 {count} 个文件：",
        "run.dryrun_end": "试运行结束，未产生任何输出文件与文件夹",
        "run.stale_tmp": "  [提示] 发现 {count} 个上次中断/异常残留的 *.cbz.tmp 半成品，请确认后手动清理（不自动删除）",
        "run.start": "开始转换 {count} 个文件...\n",
        "run.timeout": "  [超时] {name}: 转换超过 {seconds} 秒，已跳过（计入失败）",
        "run.timeout_residue": "  [提示] 转换超时，底层解压线程可能残留，大量超时建议重启脚本",
        "run.elapsed": "  [耗时] {name}: {seconds} 秒",
        "rename.preview": "  [重命名] {old} -> {new}",
        "run.ctrl_c": "\n检测到 Ctrl+C，中断转换，输出当前进度汇总：",
        "run.done": "\n转换完成: {success}/{total} 成功",
        "run.interrupted_note": "（任务被中断，以上为已处理部分的汇总，剩余文件未处理）",
        "run.stats": "转换统计: 成功 {success} 个, 跳过 {skip} 个, 失败 {fail} 个",
        "run.failed_reasons": "失败分类: {summary}",
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
    # ---- 【修改】CBZ ComicInfo 修改模式 ----
    "modify.header": "  [修改] 共 {count} 个 CBZ 将更新 ComicInfo.xml",
    "modify.plan": "  [将修改] {name}",
    "modify.plan_add": "    + {field}: {value}（新增）",
    "modify.plan_change": "    ~ {field}: {old} → {new}",
    "modify.done": "  [修改] {name}：ComicInfo.xml 已更新",
    "modify.nochange": "  [修改] {name}：无字段变化，未改动",
    "modify.fail": "  [失败] {name}: {err}",
    "modify.stats": "  修改完成：成功 {success}，无变化 {nochange}，失败 {fail}",
    "modify.failed_reasons": "修改失败原因: {summary}",
    "modify.dryrun_end": "  试运行结束：未实际修改任何 CBZ",
    "progress.desc.modify": "修改中",
    "rename_cbz.header": "  [重命名] 共 {count} 个 CBZ 将重命名文件名",
    "rename_cbz.done": "  [重命名] {name} -> {new}",
    "rename_cbz.nochange": "  [重命名] {name}：文件名无需变更",
    "rename_cbz.skip_existing": "  [跳过] {name}：目标文件已存在：{target}（如需覆盖请加 --overwrite）",
    "rename_cbz.skip_conflict": "  [跳过] {name}：改名后与本批文件撞名：{target}（建议调整命名模板避免冲突）",
    "rename_cbz.fail": "  [失败] {name}: {err}",
    "rename_cbz.failed_reasons": "重命名失败原因: {summary}",
    "rename_cbz.stats": "  重命名完成：成功 {success}，无变化 {nochange}，跳过 {skip}（磁盘同名 {existing}，本批撞名 {conflict}），失败 {fail}",
    "rename_cbz.skipped_existing_header": "  跳过（磁盘已存在同名目标）{count} 个：",
    "rename_cbz.skipped_conflict_header": "  跳过（本批撞名）{count} 个：",
    "rename_cbz.dryrun_end": "  试运行结束：未实际重命名任何 CBZ",
    "progress.desc.rename": "重命名中",
    "tag.rename_preview": "[重命名预览]",
    "setinfo.whitelist_skip": "  [警告] {field} 不在 ComicInfo 白名单，已忽略",
    "setinfo.unknown_placeholder": "  [警告] 未知占位符 {raw}，按原样写入",
    "setinfo.invalid_manga": "  [警告] 无效的 Manga 取值 '{value}'（限 Unknown/No/Yes/YesAndRightToLeft），已忽略",
    "convert.source_newer_reconvert": "  [提示] 目标 {name} 已存在但源文件更新，自动重新转换",
    "inspect.pagecount_mismatch": "  [提示] ComicInfo PageCount={declared} 与实际图片数 {actual} 不一致",
    "inspect.pagecount_non_numeric": "  [警告] ComicInfo PageCount 非数字: {raw}",
        # ---- 【清单】--list-images / --drop-extra 共用文案 ----
        "anom.animated": "动图 ({frames} 帧)",
        "anom.extra_append": "目录外图片（默认追加末尾）",
        "anom.extra_drop": "目录外图片（配 --drop-extra 将舍弃）",
        "anom.small": "异常小图",
        "anom.overscale": "超大页",
        "anom.rotated_double": "旋转跨页",
        "anom.thumbnail": "缩略图",
        "convert.drop_filter": "按过滤表达式丢弃 {count} 张图片{names}",
        "dir.landscape": "横向",
        "dir.portrait": "纵向",
        "dir.square": "方形",
        "error.filter_token": "无效的过滤条件词 '{token}'（表达式: {expr}）",
        "help.list_images": "列出电子书内部图片清单（只读，不转换、不生成 CBZ）：无值列出全部；带值按 FILTER 过滤（逗号=OR、'+'=AND；类目：格式/extra/res/size/方向/模式/位深/标记，如 gif,res<200 或 jpg+size>1mb）；与 --drop-extra 共用过滤引擎；清单中 [异常]/[推断] 为汇总/推断标记，[追加]/[舍弃]/[筛选] 对应 append/drop/filter 处置；配 --json 每文件精简 JSON；配 --quiet 只留计数；带值请用 --选项=值 写法，或把目标路径放在本选项之前",
        "inspect.status_fail": "清单提取失败: {err}",
        "list.animated": "动图: {n} 张",
        "list.anomaly": "异常图片: {n} 张",
        "list.anomaly_item": "  - {name}: {dim} ({desc})",
        "list.badzip": "不是有效的 zip 文件（{err}）",
        "list.col.dir": "方向",
        "list.col.file": "文件名",
        "list.col.mark": "标记",
        "list.col.mode": "模式/色深",
        "list.col.no": "序号",
        "list.col.res": "分辨率",
        "list.col.size": "大小",
        "list.col.toc": "目录",
        "list.double": "双页横幅: {n} 张",
        "list.fail": "清单失败: {err}",
        "list.file_line": "文件: {name}",
        "list.fmt": "格式: {parts}",
        "list.mode": "模式/色深: {parts}",
        "list.no_images": "未找到图片",
        "list.no_match": "无匹配图片",
        "list.res_item": "  {w}×{h} {count} 张 ({pct}%)",
        "list.res_other": "  其他 {count} 张 ({pct}%)",
        "list.res_other_note": "（尺寸分布较散，可能含扫描差异）",
        "list.res_title": "尺寸分布:",
        "list.small": "小图: {n} 张",
        "list.drop_small_note": "[提示] 小图阈值 = 面积中位数 × {ratio}（可用 --drop-small 调严/调松）",
        "list.total": "图片总数: {n} 张",
        "list.quiet_summary": "[提示] 共 {n} 张图片，其中 {anomalies} 张异常（--quiet 已抑制明细）",
        "mark.animated": "[动图]",
        "mark.extra": "[多余]",
        "mark.cover": "[封面]",
        "mark.double": "[双页]",
        "mark.thumbnail": "[缩略图]",
        "mark.small": "[异常小图]",
        "mark.filter": "[筛选]",
        "mark.drop": "[舍弃]",
        "mark.append": "[追加]",
        "mark.overscale": "[超大页]",
        "mark.rotated_double": "[旋转跨页]",
        "mark.anom": "[异常]",
        "mark.inferred": "[推断]",
        "unpack.path_skip": "[警告] {name}: 跳过不安全解包路径 {entry}",
    },
    "zh-TW": {
        "error.missing_dependency": "【致命錯誤】缺少核心依賴 mobi，請執行安裝命令：",
        "error.log_write_failed": "【警告】日誌寫入失敗（{err}），日誌檔案: {path}，後續日誌不再寫入",
        "error.json_write_failed": "【警告】JSON 結果寫入失敗（{err}），路徑: {path}",
        "error.ext_priority_empty": "--ext-priority 不能為空",
        "error.ext_priority_invalid": "--ext-priority 僅接受 mobi/azw/azw3/epub，收到: {p}",
        # ---- --help 文案 ----
        "help.description": "mobi/azw/azw3/epub 漫畫批量轉 cbz",
        "help.language": "輸出語言：auto 按系統語言自動選擇（zh 前綴→中文，zh-TW/zh-Hant→繁體中文，ja/Japanese→日文，否則→英文），或指定 zh-CN/zh-TW/ja/en（相容 zh/cn/zhtw/jp 等常見寫法）",
        "help.target": "電子書檔案路徑、包含電子書（.mobi/.azw/.azw3/.epub）的目錄，或含 * / ? 的通配符模式（如 *.epub）；處理當前目錄可寫 .",
        "help.delete": "轉換成功後刪除原始電子書檔案",
        "help.prefer": "雙目錄 mobi（mobi7/mobi8）時保留哪份：auto 預設優先 mobi8、空殼自動回退 mobi7；指定 mobi7/mobi8 時，指定目錄為空也自動回退另一份",
        "help.ext_priority": "同目錄同名（僅副檔名不同）時保留哪種格式：逗號分隔、順序即優先級從高到低，僅接受 mobi/azw/azw3/epub，預設 azw3；優先級未覆蓋時回退兜底順序 azw3→epub→mobi→azw；與 --prefer（雙目錄選擇）無關",
        "help.drop_extra": "丟棄目錄外多餘圖（隱藏別名，已併入 --drop extra）：無值=丟棄目錄外多餘圖（預設追加）；off/no/0=關閉；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "help.drop": "丟棄指定圖片（統一丟棄入口）：無值/extra=丟棄目錄外多餘圖（預設追加）；格式詞丟棄對應格式（如 gif 丟 gif）；條件詞過濾（small[=比例] 小圖、超大頁、疑似旋轉跨頁、異常、封面、寬高比等，支援中/日/英多語言別名）；off/no/0=關閉；多條件逗號=OR、加號=AND、- 前綴排除；過濾面與 --list-images 同源；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "help.overwrite": "目標 cbz 已存在時強制重新生成（預設跳過）",
        "help.timeout": "單檔轉換逾時秒數，逾時自動跳過並計入失敗（預設 600，0 表示不限制；逾時後底層解包執行緒可能於背景殘留）",
        "help.min_size": "過濾小於指定位元組的電子書；不帶數字預設1000位元組，0關閉大小過濾，不傳則關閉；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "help.output_dir": "CBZ 輸出到指定目錄（自動建立），預設保留相對輸入的子目錄結構（如 Sample Series/001.mobi → DIR/Sample Series/001.cbz），加 --flatten 可平鋪到目錄根下",
        "help.top_only": "僅處理 target 目錄頂層的電子書檔案，不遞迴子目錄",
    "help.flatten": "僅與 --output-dir 聯用：所有 CBZ 平鋪到輸出目錄根下，同名檔案未指定 --overwrite 時跳過（SKIP），指定時覆蓋首選名；單獨使用將報錯退出",
        "help.dry_run": "試運行：只掃描檔案並列印轉換流程，不實際解壓打包、不建立輸出目錄",
        "help.progress": "進度條顯示策略：auto 在 TTY 且檔案數≥2 且未用 --json/--json-out 時顯示；on 強制顯示；off 強制關閉（預設 off 不顯示）；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "help.no_progress": "強制關閉進度條（即使 TTY 且檔案數≥2）",
        "help.quiet": "靜默模式：只顯示錯誤與最終彙總（日誌檔案不受影響）",
        "help.no_color": "停用 ANSI 顏色輸出（即使終端支援也不上色）；日誌/JSON/管道輸出本就不含顏色",
        "help.debug": "輸出除錯資訊（debug 級到 stderr；日誌檔案始終記錄）",
        "warn.cleanup_tmp_fail": "清理暫存目錄失敗 {path}: {err}",
        "warn.disk_space": "磁碟空間不足：{label} {path} 剩餘 {free_mb} MB < 估算需要 {need_mb} MB",
        "help.short_summary": "精簡彙總：成功/跳過檔案只顯示數量不列出路徑，失敗檔案始終全路徑列出",
        "help.compress": "zip 壓縮級別 0-9：0=不壓縮（預設，圖片本身已壓縮），1-9=deflate 壓縮（PNG 來源有收益，級別越高越小但越慢）",
        "help.inspect": "檢查模式：sample 隨機抽查 1 個（預設），all 全量檢查；可附過濾器 [MODE][,FILTER]（如 all,small=0.6）輸出命中條件圖的數量+檔名清單，FILTER 語法與 --drop 相同（逗號=OR、加號=AND、- 前綴排除）；只解包讀取內部資訊（中繼資料/結構/圖片/解析度/DRM），不生成 CBZ，結束自動清理臨時目錄；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "help.inspect_all": "檢查全部電子書（等價 --inspect all，相容舊命令）",
        "help.no_comicinfo": "不生成 ComicInfo.xml（預設生成：向 CBZ 根目錄寫入漫畫元資料）",
        "help.double_page": "雙頁偵測：不傳/auto 開啟（閾值 2.0）；數值調閾值；off/no/0 關閉（開啟時寫入逐頁 DoublePage 標記，不寫 Manga 宣告；如需 Manga 請用 --setinfo Manga=）；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "error.double_page_invalid": "無效的 --double-page 值 '{value}'：支援 auto/數值/off/no/0",
        "help.drop_small": "丟棄小圖（隱藏別名，已併入 --drop small）：轉換時剔除尺寸明顯偏小的圖片（面積 寬×高 < 面積中位數×比例 判為小圖；不傳/auto=0.5，可傳 0~1 數值調比例，off/no/0 關閉）；丟棄後 PageCount 按實際剩餘圖數重算；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "error.drop_small_invalid": "無效的 --drop-small 值 '{value}'：支援 auto 或數值(0~1)",
        "convert.drop_small": "  [清理] 丟棄小圖 {count} 張{names}",
        "run.drop_small_total": "丟棄小圖合計: {count} 張",
        "inspect.drop_small_preview": "  [提示] 圖片中 {count} 張為小圖（開啟 --drop small 時將被丟棄）",
        "inspect.filter_hits": "  [命中] {count} 張圖片命中過濾條件（--inspect 過濾器）",
        "inspect.filter_no_hit": "  [無命中] 沒有圖片命中過濾條件",
        "help.setinfo": "設定 ComicInfo 欄位（可多次，格式 FIELD=VALUE；VALUE 支援 %series/%number/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M（%subN_M=第 N 字元起 M 個，1-based）；逗號後緊跟欄位名=才拆分，值內含 Key= 結構請用多次 --setinfo 傳入；Manga 取值限 Unknown/No/Yes/YesAndRightToLeft，預設不寫；--setinfo 開啟時輸入中的既有 .cbz 會就地修改其 ComicInfo.xml）",
"help.rename": "重新命名輸出 CBZ 檔名（可選範本，預設關閉）。--rename 無值=預設範本（系列名+自動標記前綴）；標記前綴依類型自動選：整卷[Vol.x]/單話[Ch.x]/卷+章[Vol.x][Ch.x]/無類型[x]，連話（話005-006）標 [Ch.5-6]；佔位符 %series/%number/%volume/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M 及 %03number 補零；來源優先序：檔名推斷 > 檔案中繼資料(OPF/ComicInfo.xml) 兜底，setinfo 不參與；%description 不建議用於檔案名稱（內容可能過長），確需使用可搭配 %subN_M 截取片段；建議搭配 --dry-run 先預覽；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "comicinfo.generating": "生成 ComicInfo.xml",
        "comicinfo.created": "已寫入 ComicInfo.xml",
        "comicinfo.disabled": "ComicInfo.xml 已停用（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml 無效或生成失敗: {err}",
        "comicinfo.build_fail": "ComicInfo.xml 生成失敗: {err}",
        "comicinfo.write_fail": "ComicInfo.xml 寫入失敗: {err}",
        "comicinfo.src.setinfo": "setinfo",
        "comicinfo.src.opf": "OPF 元數據",
        "comicinfo.src.inferred": "檔名推斷",
        "help.log": "將全部輸出追加寫入日誌檔案（省略檔名時自動產生時間戳日誌）；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "help.json": "在 stdout 輸出單行緊湊 JSON 結果（供 AI/管道讀取），開啟時屏蔽人類可讀文本；轉換/修改模式為整體單行緊湊 JSON，inspect 模式每檔案一行精簡 JSON，dry-run 帶 dry_run 標記輸出，僅 unpack 模式不輸出；進度條寫 stderr 不與 JSON 混流，但 2>&1 合併重新導向會混入",
        "help.json_out": "將轉換結果寫入 JSON 檔案（省略檔名時自動產生時間戳檔案，或指定路徑；同 --json 僅轉換/修改模式寫入）；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "log.auto_named": "日誌檔案: {path}（自動命名）",
        "json.written": "JSON 結果已寫入: {path}",
        "help.unpack": "解包模式：只解壓不轉換，輸出到來源檔案所在目錄的「來源名_副檔名」子目錄（如 vol.cbz → vol_cbz/），與來源檔案不撞名；_cbz 結尾的解包目錄可直接被 --repack 重新打包",
        "unpack.done": "已解包 {name} -> {dir}",
        "help.repack": "重新打包：將已解包的 CBZ 解包目錄（目錄名以 _cbz 結尾）重新打包回 CBZ（輸出名還原為來源檔名，如 vol_cbz → vol.cbz），可搭配 --setinfo 修改元資料（--rename 不適用於本模式）",
        "repack.none_found": "未找到 _cbz 結尾的解包目錄: {path}",
        "repack.no_images": "[錯誤] {dir}：目錄內未找到圖片",
        "repack.skip_exists": "[跳過] {path} 已存在（--overwrite 強制覆寫）",
        "repack.done": "[完成] {name}：共 {count} 張圖片，{size} MB",
        "repack.fail": "[失敗] {dir} 重新打包失敗: {err}",
        "repack.done_summary": "重新打包完成：成功 {ok} 個，失敗 {fail} 個",
        "repack.plan": "將重新打包 {count} 個解包目錄：",
    "repack.rename_ignored": "提示：--repack 模式不適用 --rename，已忽略（輸出檔名由解包目錄名推斷）",
        "unpack.plan": "將解包 {count} 個檔案：",
        "unpack.done_summary": "解包完成：成功 {ok} 個，失敗 {fail} 個",
        "error.repack_need_dir": "repack 模式僅接受目錄（_cbz 結尾的解包目錄，或含 *_cbz 解包目錄的父目錄）: {path}",
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
        "dedupe.auto_fallback": "  [去重] 雙目錄，mobi8 為空殼，自動回退 mobi7",
        "dedupe.prefer_empty_fallback": "  [去重] 指定保留 {prefer} 但該目錄無圖片，自動回退 {fallback}",
        # ---- 目录对齐 ----
        "align.drop": "  [提示] 目錄中 {count} 張圖片未被收集，已按 --drop-extra 放棄{names}",
        "align.append": "  [提示] 目錄中 {count} 張圖片未被收集，已追加到末尾{names}",
        # ---- 【转换】转换流程 ----
        "convert.skip_exists": "  [跳過] 目標已存在: {name}",
        "convert.flatten_conflict_skip": "  [警告] 平鋪同名衝突: {src} 與已存在的 {name} 同名，已跳過；如確定覆蓋請用 --overwrite",
        "convert.skip_corrupt_reconvert": "  [提示] 目標 {name} 已存在但校驗失敗，自動重新轉換",
        "convert.overwrite": "  [覆寫] 將覆蓋舊檔，重新生成: {name}",
        "convert.spine": "  [排序] 按 OPF spine 順序（{count} 張圖片）",
        "convert.spine_empty": "  [排序] spine 提取為空，兜底按檔名排序（{count} 張）",
        "convert.dedup_physical": "  [去重] 跳過 {count} 個物理重複檔案（同一檔案重複出現，未寫入 CBZ）",
        "convert.no_opf": "  [排序] 未找到 OPF，兜底按檔名排序（{count} 張）",
        "convert.multi_opf": "  [排序] 偵測到 {count} 個 OPF 檔案，使用第一個: {first}",
        "convert.no_images": "  [失敗] 未找到圖片: {name}",
        "convert.drm_hint": "  [提示] 可能為 DRM 加密的 Kindle 漫畫，mobi 函式庫無法解密，請先去除 DRM 後再轉換",
        "convert.drm_hint_epub": "  [提示] 該 EPUB 未解析出圖片，請確認其包含漫畫圖片、且未加密",
        "convert.count_mismatch": "  [提示] 目錄共 {total} 張圖片，收集 {collected} 張，數量不一致",
        "convert.done": "  [完成] {name} ({count} 張圖片, {size} MB)",
        "convert.verify_fail": "  [校驗失敗] {name}: {msg}，舊檔案已保留",
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
        "inspect.drm_marked_try": "  提示: 檔頭帶 DRM 標記，繼續嘗試解包",
        "inspect.drm_hint": "  提示: 檔頭帶 DRM 標記且解包失敗，內容可能加密，需先去除 DRM 再轉換",
        "inspect.drm_but_readable": "  DRM: 有(檔頭標記)但內容可讀(圖片{count}張)",
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
        "inspect.nav_count": "  目錄(EPUB3 nav): {count} 個條目 | 預覽: {preview}",
        "inspect.nav_missing": "  目錄(EPUB3 nav): 未找到",
        "inspect.dir_images": "  目錄全部圖片: {count} 張",
        "inspect.drm_suspected": "  DRM: 疑似(檔頭標記無但圖片0張)",
        "inspect.cover_missing": "  封面檔案未找到",
        "inspect.fmt_none": "  圖片格式統計: 無圖片可統計",
        "inspect.drm_bad_hint": "  提示: 疑似 DRM 加密或內容損壞，轉換會失敗，需先去除 DRM",
        "inspect.drm_none": "  DRM: 無(檔頭標記無+圖片{count}張)",
        "inspect.cover_src_guide": "OPF guide 官方引用",
        "inspect.cover_src_filename": "檔名匹配",
        "inspect.cover_found": "  封面檔案已找到: {name}（{src}）{dim} {size}",
        "inspect.fmt_stats": "  圖片格式統計（共 {total} 張）: {parts}",
        "inspect.res_main_h": "主流高 {height} ({count}張, {pct}%)",
        "inspect.res_w_range": "寬 {min}~{max}",
        "inspect.res_main_w": "主流寬 {width} ({count}張, {pct}%)",
        "inspect.res_h_range": "高 {min}~{max}",
        "inspect.res_line": "  解析度: {parts}",
        "inspect.res_summary": "  解析度摘要: 主解析度 {w}x{h} 共 {count} 張 ({pct}%)；異常小圖 {small} 張",
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
        # ---- 【清单】--list-images / --drop-extra 共用文案 ----
        "anom.animated": "動圖 ({frames} 幀)",
        "anom.extra_append": "目錄外圖片（預設追加末尾）",
        "anom.extra_drop": "目錄外圖片（配 --drop-extra 將捨棄）",
        "anom.small": "異常小圖",
        "anom.overscale": "超大頁",
        "anom.rotated_double": "旋轉跨頁",
        "anom.thumbnail": "縮圖",
        "convert.drop_filter": "按過濾表達式丟棄 {count} 張圖片{names}",
        "dir.landscape": "橫向",
        "dir.portrait": "縱向",
        "dir.square": "方形",
        "error.filter_token": "無效的過濾條件詞 '{token}'（表達式: {expr}）",
        "help.list_images": "列出電子書內部圖片清單（唯讀，不轉換、不生成 CBZ）：無值列出全部；帶值按 FILTER 過濾（逗號=OR、'+'=AND；類目：格式/extra/res/size/方向/模式/位深/標記，如 gif,res<200 或 jpg+size>1mb）；與 --drop-extra 共用過濾引擎；清單中 [異常]/[推斷] 為彙總/推斷標記，[追加]/[捨棄]/[篩選] 對應 append/drop/filter 處置；配 --json 每檔案精簡 JSON；配 --quiet 只留計數；帶值請用 --選項=值 寫法，或將目標路徑放在本選項之前",
        "inspect.status_fail": "清單提取失敗: {err}",
        "list.animated": "動圖: {n} 張",
        "list.anomaly": "異常圖片: {n} 張",
        "list.anomaly_item": "  - {name}: {dim} ({desc})",
        "list.badzip": "不是有效的 zip 檔案（{err}）",
        "list.col.dir": "方向",
        "list.col.file": "檔案名",
        "list.col.mark": "標記",
        "list.col.mode": "模式/色深",
        "list.col.no": "序號",
        "list.col.res": "解析度",
        "list.col.size": "大小",
        "list.col.toc": "目錄",
        "list.double": "雙頁橫幅: {n} 張",
        "list.fail": "清單失敗: {err}",
        "list.file_line": "檔案: {name}",
        "list.fmt": "格式: {parts}",
        "list.mode": "模式/色深: {parts}",
        "list.no_images": "未找到圖片",
        "list.no_match": "無匹配圖片",
        "list.res_item": "  {w}×{h} {count} 張 ({pct}%)",
        "list.res_other": "  其他 {count} 張 ({pct}%)",
        "list.res_other_note": "（尺寸分佈較散，可能含掃描差異）",
        "list.res_title": "尺寸分佈:",
        "list.small": "小圖: {n} 張",
        "list.drop_small_note": "[提示] 小圖閾值 = 面積中位數 × {ratio}（可用 --drop-small 調嚴/調鬆）",
        "list.total": "圖片總數: {n} 張",
        "list.quiet_summary": "[提示] 共 {n} 張圖片，其中 {anomalies} 張異常（--quiet 已抑制明細）",
        "mark.animated": "[動圖]",
        "mark.extra": "[多餘]",
        "mark.cover": "[封面]",
        "mark.double": "[雙頁]",
        "mark.thumbnail": "[縮圖]",
        "mark.small": "[異常小圖]",
        "mark.filter": "[篩選]",
        "mark.drop": "[捨棄]",
        "mark.append": "[追加]",
        "mark.overscale": "[超大頁]",
        "mark.rotated_double": "[旋轉跨頁]",
        "mark.anom": "[異常]",
        "mark.inferred": "[推斷]",
        "unpack.path_skip": "[警告] {name}: 跳過不安全解包路徑 {entry}",
        "main.ctrl_c": "[提示] 使用者中斷（Ctrl+C），程式退出",
        "main.crash": "程式崩潰，堆疊資訊如下：",
        "run.auto_language": "已自動辨識語種為 {lang}",
        # ---- 【汇总】运行主流程（汇总统计）----
        "run.path_not_found": "路徑不存在: {path}",
        "run.no_ebooks": "未找到電子書檔案（.mobi/.azw/.azw3/.epub）: {path}",
        "run.precheck_header": "預處理跳過 {count} 個檔案：",
        "run.none_convertible": "無有效電子書檔案可轉換（全部被預處理過濾或同名去重）",
        "run.found": "找到 {total} 個有效電子書檔案（預處理過濾 {pre} 個，同名去重 {dedup} 個）\n",
        "run.dryrun_banner": "[試運行] --dry-run 模式：僅掃描與列印流程，不實際解壓打包、不建立輸出目錄",
        "dryrun.output_not_writable": "  [警告] 輸出目錄不可寫: {path}，正式轉換將失敗",
        "run.plan_output_dir": "計畫輸出目錄: {path}（僅正式轉換時自動建立）",
        "run.dryrun_precheck": "試運行預處理跳過 {count} 個檔案：",
        "run.dryrun_end": "試運行結束，未產生任何輸出檔案與資料夾",
        "run.stale_tmp": "  [提示] 發現 {count} 個上次中斷/異常殘留的 *.cbz.tmp 半成品，請確認後手動清理（不自動刪除）",
        "run.start": "開始轉換 {count} 個檔案...\n",
        "run.timeout": "  [逾時] {name}: 轉換超過 {seconds} 秒，已跳過（計入失敗）",
        "run.timeout_residue": "  [提示] 轉換逾時，底層解壓執行緒可能殘留，大量逾時建議重啟腳本",
        "run.elapsed": "  [耗時] {name}: {seconds} 秒",
        "rename.preview": "  [重新命名] {old} -> {new}",
        "run.ctrl_c": "\n偵測到 Ctrl+C，中斷轉換，輸出目前進度彙總：",
        "run.done": "\n轉換完成: {success}/{total} 成功",
        "run.interrupted_note": "（任務被中斷，以上為已處理部分的彙總，剩餘檔案未處理）",
        "run.stats": "轉換統計: 成功 {success} 個, 跳過 {skip} 個, 失敗 {fail} 個",
        "run.failed_reasons": "失敗分類: {summary}",
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
    # ---- 【修改】CBZ ComicInfo 修改模式 ----
    "modify.header": "  [修改] 共 {count} 個 CBZ 將更新 ComicInfo.xml",
    "modify.plan": "  [將修改] {name}",
    "modify.plan_add": "    + {field}: {value}（新增）",
    "modify.plan_change": "    ~ {field}: {old} → {new}",
    "modify.done": "  [修改] {name}：ComicInfo.xml 已更新",
    "modify.nochange": "  [修改] {name}：無欄位變化，未改動",
    "modify.fail": "  [失敗] {name}: {err}",
    "modify.stats": "  修改完成：成功 {success}，無變化 {nochange}，失敗 {fail}",
    "modify.failed_reasons": "修改失敗原因: {summary}",
    "modify.dryrun_end": "  試運行結束：未實際修改任何 CBZ",
    "progress.desc.modify": "修改中",
    "rename_cbz.header": "  [重新命名] 共 {count} 個 CBZ 將重新命名檔名",
    "rename_cbz.done": "  [重新命名] {name} -> {new}",
    "rename_cbz.nochange": "  [重新命名] {name}：檔名無需變更",
    "rename_cbz.skip_existing": "  [跳過] {name}：目標檔案已存在：{target}（如需覆蓋請加 --overwrite）",
    "rename_cbz.skip_conflict": "  [跳過] {name}：改名後與本批檔案撞名：{target}（建議調整命名範本避免衝突）",
    "rename_cbz.fail": "  [失敗] {name}: {err}",
    "rename_cbz.failed_reasons": "重新命名失敗原因: {summary}",
    "rename_cbz.stats": "  重新命名完成：成功 {success}，無變化 {nochange}，跳過 {skip}（磁碟同名 {existing}，本批撞名 {conflict}），失敗 {fail}",
    "rename_cbz.skipped_existing_header": "  跳過（磁碟已存在同名目標）{count} 個：",
    "rename_cbz.skipped_conflict_header": "  跳過（本批撞名）{count} 個：",
    "rename_cbz.dryrun_end": "  試運行結束：未實際重新命名任何 CBZ",
    "progress.desc.rename": "重新命名中",
    "tag.rename_preview": "[重新命名預覽]",
    "setinfo.whitelist_skip": "  [警告] {field} 不在 ComicInfo 白名單，已忽略",
    "setinfo.unknown_placeholder": "  [警告] 未知佔位符 {raw}，按原樣寫入",
    "setinfo.invalid_manga": "  [警告] 無效的 Manga 取值 '{value}'（限 Unknown/No/Yes/YesAndRightToLeft），已忽略",
    "convert.source_newer_reconvert": "  [提示] 目標 {name} 已存在但來源檔案更新，自動重新轉換",
    "inspect.pagecount_mismatch": "  [提示] ComicInfo PageCount={declared} 與實際圖片數 {actual} 不一致",
    "inspect.pagecount_non_numeric": "  [警告] ComicInfo PageCount 非數字: {raw}",
    },
    "en": {
        "error.missing_dependency": "[Fatal Error] Missing required dependency mobi. Install with:",
        "error.log_write_failed": "[Warning] Failed to write log ({err}), log file: {path}, further log entries will be skipped",
        "error.json_write_failed": "[Warning] Failed to write JSON result ({err}), path: {path}",
        "error.ext_priority_empty": "--ext-priority must not be empty",
        "error.ext_priority_invalid": "--ext-priority accepts only mobi/azw/azw3/epub, got: {p}",
        # ---- --help 文案 ----
        "help.description": "Batch convert mobi/azw/azw3/epub ebooks to cbz",
        "help.language": "Output language: auto picks by system locale (zh prefix->Chinese, zh-TW/zh-Hant->Traditional Chinese, ja/Japanese->Japanese, otherwise->English), or choose zh-CN/zh-TW/ja/en (tolerant of common variants like zh/cn/zhtw/jp)",
        "help.target": "Path to an ebook file, a directory containing ebooks (.mobi/.azw/.azw3/.epub), or a glob pattern with * / ? (e.g. *.epub); use . to process the current directory",
        "help.delete": "Delete the original ebook file after successful conversion",
        "help.prefer": "Which directory to keep when both mobi7/mobi8 exist: auto (default) prefers mobi8 and falls back to mobi7 if empty; when mobi7/mobi8 is specified, falls back to the other if the chosen one is empty",
        "help.ext_priority": "When same-name files differ only by extension in the same directory, which format to keep: comma-separated, order is priority high->low, only mobi/azw/azw3/epub accepted, default azw3; falls back to azw3->epub->mobi->azw when not covered; unrelated to --prefer (mobi7/mobi8 selection)",
        "help.drop_extra": "Drop extra images outside the collection (hidden alias, merged into --drop extra): no value drops extra images (default: appended); off/no/0 disables; when passing a value use --option=value, or place the target path before this option",
        "help.drop": "Drop images matching the given formats/conditions (unified drop entry): no value/extra drops extra images outside the collection (default: appended); a format word drops that format (e.g. gif); condition words filter (small[=ratio] small images, overscale, suspected rotated spread, anomaly, cover, aspect ratio etc., with zh/ja/en aliases); off/no/0 disables; comma = OR, plus = AND, - prefix excludes; shares the filter engine with --list-images; when passing a value use --option=value, or place the target path before this option",
        "help.overwrite": "Force regenerate when the target cbz already exists (default: skip)",
        "help.timeout": "Per-file conversion timeout in seconds; on timeout the file is skipped and counted as failed (default 600, 0 = no limit; on timeout the underlying unpack thread may linger in the background)",
        "help.min_size": "Filter out ebooks smaller than the given bytes; without a number defaults to 1000 bytes, 0 disables size filtering, omitted disables it; when passing a value use --option=value, or place the target path before this option",
        "help.output_dir": "Output CBZ to the given directory (auto-created); by default keeps the relative subdirectory structure of the input (e.g. Sample Series/001.mobi -> DIR/Sample Series/001.cbz), add --flatten to flatten into the root",
        "help.top_only": "Only process ebook files directly in the target directory (do not recurse into subdirectories)",
    "help.flatten": "Only with --output-dir: flatten all CBZ into the root of the output directory; same-name files are skipped (SKIP) unless --overwrite is given, which overwrites the preferred name; using it alone exits with an error",
        "help.dry_run": "Dry run: only scan files and print the conversion flow, without extracting, packing or creating output directories",
        "help.progress": "Progress bar policy: auto shows when TTY and >=2 files and not using --json/--json-out; on forces display; off disables (default off); when passing a value use --option=value, or place the target path before this option",
        "help.no_progress": "Force-disable the progress bar (even when TTY and >=2 files)",
        "help.quiet": "Quiet mode: only show errors and the final summary (log file unaffected)",
        "help.no_color": "Disable ANSI color output (even if the terminal supports it); logs/JSON/pipes are never colored anyway",
        "help.debug": "Output debug info (debug level to stderr; always recorded in log file)",
        "warn.cleanup_tmp_fail": "Failed to clean temp directory {path}: {err}",
        "warn.disk_space": "Disk space low: {label} {path} free {free_mb} MB < estimated {need_mb} MB needed",
        "help.short_summary": "Compact summary: list counts instead of paths for succeeded/skipped files; failed files always show full paths",
        "help.compress": "zip compression level 0-9: 0=none (default, images already compressed), 1-9=deflate (helps for PNG sources, higher is smaller but slower)",
        "help.inspect": "Inspect mode: sample randomly inspects 1 ebook (default), all inspects every file; optional filter [MODE][,FILTER] (e.g. all,small=0.6) prints the count + filename list of matched images; FILTER syntax is the same as --drop (comma=OR, plus=AND, - prefix excludes); unpack only to read internal info (metadata/structure/images/resolution/DRM) without generating CBZ, then auto-clean temp dirs; when passing a value use --option=value, or place the target path before this option",
        "help.inspect_all": "Inspect all ebooks (equivalent to --inspect all; kept for old-command compatibility)",
        "help.no_comicinfo": "Do not generate ComicInfo.xml (default: write comic metadata into CBZ root)",
        "help.double_page": "Double-page detection: no value/auto enable (ratio 2.0); a number sets ratio; off/no/0 disable (when enabled, writes per-page DoublePage marks but no Manga element; use --setinfo Manga= for Manga); when passing a value use --option=value, or place the target path before this option",
        "error.double_page_invalid": "Invalid --double-page value '{value}': use auto, a number, or off/no/0",
        "help.drop_small": "Drop small images (hidden alias, merged into --drop small): exclude images clearly smaller than others during conversion (an image is small if its area width x height is below median area x ratio; no value/auto = 0.5, a 0~1 number sets ratio, off/no/0 disables). PageCount is recalculated after dropping; when passing a value use --option=value, or place the target path before this option",
        "error.drop_small_invalid": "Invalid --drop-small value '{value}': use auto or a number (0~1)",
        "convert.drop_small": "  [Clean] Dropped {count} small image(s){names}",
        "run.drop_small_total": "Total small images dropped: {count}",
        "inspect.drop_small_preview": "  [Note] {count} small image(s) found (will be dropped when --drop small is enabled)",
        "inspect.filter_hits": "  [Hits] {count} image(s) matched the filter (--inspect filter)",
        "inspect.filter_no_hit": "  [No hits] no image matched the filter",
        "help.setinfo": "Set ComicInfo field (repeatable, FIELD=VALUE; VALUE supports %series/%number/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M (%subN_M = M chars from the Nth char, 1-based); split on comma only when followed by FIELD=; use multiple --setinfo for a value containing Key=; Manga accepts Unknown/No/Yes/YesAndRightToLeft, not written by default; when enabled, existing .cbz inputs have their ComicInfo.xml modified in place)",
"help.rename": "Rename output CBZ filename (optional template, off by default). --rename (no value) uses default template (series + auto mark prefix); mark prefix by type: [Vol.x] volume-only / [Ch.x] chapter-only / [Vol.x][Ch.x] volume+chapter / [x] untyped; consecutive episodes (話005-006) -> [Ch.5-6]; placeholders %series/%number/%volume/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M and zero-pad %03number; source priority: filename inference > file metadata (OPF/ComicInfo.xml), setinfo excluded; %description is not recommended for filenames (content may be very long); if needed, slice it with %subN_M; combine with --dry-run to preview; when passing a value use --option=value, or place the target path before this option",
        "comicinfo.generating": "Generating ComicInfo.xml",
        "comicinfo.created": "ComicInfo.xml written",
        "comicinfo.disabled": "ComicInfo.xml disabled (--no-comicinfo)",
        "comicinfo.invalid": "ComicInfo.xml invalid or generation failed: {err}",
        "comicinfo.build_fail": "ComicInfo.xml generation failed: {err}",
        "comicinfo.write_fail": "ComicInfo.xml write failed: {err}",
        "comicinfo.src.setinfo": "setinfo",
        "comicinfo.src.opf": "OPF",
        "comicinfo.src.inferred": "inferred",
        "help.log": "Append all output to the given log file (omit filename to auto-generate a timestamped log); when passing a value use --option=value, or place the target path before this option",
        "help.json": "Print a single-line compact JSON result to stdout (for AI/pipe consumption); suppresses human-readable text when enabled; emitted as one compact JSON line in conversion/modify mode, one slim line per file in inspect mode, and with a dry_run flag in dry-run; only unpack mode emits nothing; the progress bar writes to stderr and stays separate, but 2>&1 combined redirection mixes it in",
        "help.json_out": "Write conversion results to a JSON file (omit filename to auto-generate a timestamped file, or specify a path; like --json, only written in conversion/modify mode); when passing a value use --option=value, or place the target path before this option",
        "log.auto_named": "Log file: {path} (auto-named)",
        "json.written": "JSON result written to: {path}",
        "help.unpack": "Unpack mode: extract only without converting, output to a `<source>_<ext>` subdirectory next to the source (e.g. vol.cbz → vol_cbz/, never clashing with the source name); _cbz-suffixed directories can be repacked with --repack",
        "unpack.done": "Unpacked {name} -> {dir}",
        "help.repack": "Repack mode: repack an unpacked CBZ directory (name ending in _cbz) back into a CBZ (output name restored to the source, e.g. vol_cbz → vol.cbz); use with --setinfo to edit metadata (--rename does not apply to this mode)",
        "repack.none_found": "No _cbz unpack directories found: {path}",
        "repack.no_images": "[Error] {dir}: no images found in directory",
        "repack.skip_exists": "[Skip] {path} already exists (use --overwrite to force)",
        "repack.done": "[Done] {name}: {count} images, {size} MB",
        "repack.fail": "[Failed] repack failed for {dir}: {err}",
        "repack.done_summary": "Repack finished: {ok} succeeded, {fail} failed",
        "repack.plan": "Will repack {count} unpack directory(ies):",
    "repack.rename_ignored": "Note: --rename does not apply to --repack mode and was ignored (output filename is inferred from the unpack directory name)",
        "unpack.plan": "Will unpack {count} file(s):",
        "unpack.done_summary": "Unpack finished: {ok} succeeded, {fail} failed",
        "error.repack_need_dir": "repack mode accepts only directories (an _cbz unpack dir, or a parent dir containing *_cbz unpack dirs): {path}",
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
        "dedupe.auto_fallback": "  [Dedup] Dual directories, mobi8 is empty, auto fallback to mobi7",
        "dedupe.prefer_empty_fallback": "  [Dedup] {prefer} specified but has no images, auto fallback to {fallback}",
        # ---- 目录对齐 ----
        "align.drop": "  [Info] {count} images in the directory were not collected, dropped per --drop-extra{names}",
        "align.append": "  [Info] {count} images in the directory were not collected, appended to the end{names}",
        # ---- 【转换】转换流程 ----
        "convert.skip_exists": "  [Skip] Target already exists: {name}",
        "convert.flatten_conflict_skip": "  [Warning] Flatten name conflict: {src} collides with existing {name}, skipped; use --overwrite to force",
        "convert.skip_corrupt_reconvert": "  [Info] Target {name} exists but failed validation ({reason}), reconverting automatically",
        "convert.overwrite": "  [Overwrite] Old file will be replaced, regenerating: {name}",
        "convert.spine": "  [Sort] Using OPF spine order ({count} images)",
        "convert.spine_empty": "  [Sort] spine extraction empty, fell back to filename order ({count} images)",
        "convert.dedup_physical": "  [Dedup] Skipped {count} physically duplicate file(s) (same file appeared more than once, not written to CBZ)",
        "convert.no_opf": "  [Sort] No OPF found, fell back to filename order ({count} images)",
        "convert.multi_opf": "  [Sort] {count} OPF files detected, using the first: {first}",
        "convert.no_images": "  [Failed] No images found: {name}",
        "convert.drm_hint": "  [Info] Possibly a DRM-protected Kindle comic; the mobi library cannot decrypt it. Remove DRM first and retry",
        "convert.drm_hint_epub": "  [Info] No images parsed from this EPUB. Confirm it contains comic images and is not encrypted",
        "convert.count_mismatch": "  [Info] Directory has {total} images but {collected} were collected; count mismatch",
        "convert.done": "  [Done] {name} ({count} images, {size} MB)",
        "convert.verify_fail": "  [Verify Failed] {name}: {msg}; old file kept",
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
        # ---- 【清单】--list-images / --drop-extra 共用文案 ----
        "anom.animated": "animated ({frames} frames)",
        "anom.extra_append": "extra image (not in spine, appended to end)",
        "anom.extra_drop": "extra image (not in spine, dropped via --drop-extra)",
        "anom.small": "abnormally small",
        "anom.overscale": "overscale",
        "anom.rotated_double": "rotated double-page",
        "anom.thumbnail": "thumbnail",
        "convert.drop_filter": "Dropped {count} image(s) by filter{names}",
        "dir.landscape": "landscape",
        "dir.portrait": "portrait",
        "dir.square": "square",
        "error.filter_token": "Invalid filter token '{token}' (expression: {expr})",
        "help.list_images": "List images inside the ebook (read-only; no conversion, no CBZ): no value lists all; a FILTER filters rows (comma=OR, '+''=AND; categories: format/extra/res/size/direction/mode/depth/mark, e.g. gif,res<200 or jpg+size>1mb); shares the filter engine with --drop-extra; rows show [anomaly]/[inferred] summary/inference marks and [append]/[drop]/[filtered] marks for append/drop/filter dispositions; with --json prints compact JSON per file; with --quiet keeps only counts; when passing a value use --option=value, or place the target path before this option",
        "inspect.status_fail": "Failed to extract listing: {err}",
        "list.animated": "Animated: {n}",
        "list.anomaly": "Anomalous images: {n}",
        "list.anomaly_item": "  - {name}: {dim} ({desc})",
        "list.badzip": "Not a valid zip file ({err})",
        "list.col.dir": "Direction",
        "list.col.file": "File",
        "list.col.mark": "Marks",
        "list.col.mode": "Mode/Depth",
        "list.col.no": "No.",
        "list.col.res": "Resolution",
        "list.col.size": "Size",
        "list.col.toc": "TOC",
        "list.double": "Double-page spreads: {n}",
        "list.fail": "Listing failed: {err}",
        "list.file_line": "File: {name}",
        "list.fmt": "Formats: {parts}",
        "list.mode": "Modes/Depths: {parts}",
        "list.no_images": "No images found",
        "list.no_match": "No images match the filter",
        "list.res_item": "  {w}x{h} {count} ({pct}%)",
        "list.res_other": "  Other {count} ({pct}%)",
        "list.res_other_note": " (scattered sizes, may include scan variance)",
        "list.res_title": "Size distribution:",
        "list.small": "Small images: {n}",
        "list.drop_small_note": "[note] small threshold = median area x {ratio} (tune with --drop-small)",
        "list.total": "Total images: {n}",
        "list.quiet_summary": "[note] {n} images total, {anomalies} anomalous (detail hidden by --quiet)",
        "mark.animated": "[animated]",
        "mark.extra": "[extra]",
        "mark.cover": "[cover]",
        "mark.double": "[double]",
        "mark.thumbnail": "[thumbnail]",
        "mark.small": "[small]",
        "mark.filter": "[filtered]",
        "mark.drop": "[drop]",
        "mark.append": "[append]",
        "mark.overscale": "[overscale]",
        "mark.rotated_double": "[rotated]",
        "mark.anom": "[anomaly]",
        "mark.inferred": "[inferred]",
        "unpack.path_skip": "[Warning] {name}: skipping unsafe extraction path {entry}",
        "inspect.drm_unmarked": "DRM: no header flag",
        "inspect.below_min_size": "below --min-size({min})",
        "inspect.min_size_not_filter": "--min-size does not filter",
        "inspect.base_line": "  Base: {parts}",
        "inspect.drm_marked_try": "  Hint: DRM flag set in header, continuing to attempt extraction",
        "inspect.drm_hint": "  Hint: DRM flag set and extraction failed; content may be encrypted, remove DRM first",
        "inspect.drm_but_readable": "  DRM: flagged but readable ({count} images)",
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
        "inspect.nav_count": "  TOC (EPUB3 nav): {count} entries | preview: {preview}",
        "inspect.nav_missing": "  TOC (EPUB3 nav): not found",
        "inspect.dir_images": "  All images in directory: {count}",
        "inspect.drm_suspected": "  DRM: suspected (no header flag but 0 images)",
        "inspect.cover_missing": "  Cover image not found",
        "inspect.fmt_none": "  Image format stats: no images to count",
        "inspect.drm_bad_hint": "  Hint: suspected DRM encryption or corrupted content; conversion would fail, remove DRM first",
        "inspect.drm_none": "  DRM: none (no header flag, {count} images)",
        "inspect.cover_src_guide": "OPF guide reference",
        "inspect.cover_src_filename": "filename match",
        "inspect.cover_found": "  Cover image found: {name} ({src}) {dim} {size}",
        "inspect.fmt_stats": "  Image format stats ({total} total): {parts}",
        "inspect.res_main_h": "main height {height} ({count} images, {pct}%)",
        "inspect.res_w_range": "width {min}~{max}",
        "inspect.res_main_w": "main width {width} ({count} images, {pct}%)",
        "inspect.res_h_range": "height {min}~{max}",
        "inspect.res_line": "  Resolution: {parts}",
        "inspect.res_summary": "  Resolution summary: dominant {w}x{h} x{count} ({pct}%); abnormal small images: {small}",
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
        "run.no_ebooks": "No ebook files (.mobi/.azw/.azw3/.epub) found: {path}",
        "run.precheck_header": "Precheck skipped {count} files:",
        "run.none_convertible": "No valid ebook files to convert (all filtered by precheck or dedup)",
        "run.found": "Found {total} valid ebook files (precheck filtered {pre}, dedup removed {dedup})\n",
        "run.dryrun_banner": "[Dry Run] --dry-run mode: scan and print flow only; no extraction, packing or output directories",
        "dryrun.output_not_writable": "  [Warning] Output directory is not writable: {path}; real conversion will fail",
        "run.plan_output_dir": "Planned output dir: {path} (auto-created only in real runs)",
        "run.dryrun_precheck": "Dry-run precheck skipped {count} files:",
        "run.dryrun_end": "Dry run finished, no output files or folders were created",
        "run.stale_tmp": "  [Hint] Found {count} leftover *.cbz.tmp partial file(s) from a previous interrupted/abnormal run; please review and clean them manually (not auto-deleted)",
        "run.start": "Converting {count} files...\n",
        "run.timeout": "  [Timeout] {name}: conversion exceeded {seconds}s, skipped (counted as failed)",
        "run.timeout_residue": "  [Hint] Conversion timed out; the underlying extraction thread may be left behind, restart the script if many timeouts occur",
        "run.elapsed": "  [Elapsed] {name}: {seconds} s",
        "rename.preview": "  [Rename] {old} -> {new}",
        "run.ctrl_c": "\nCtrl+C detected, conversion interrupted; showing current progress summary:",
        "run.done": "\nConversion complete: {success}/{total} succeeded",
        "run.interrupted_note": "(Task interrupted; summary above covers processed files only, the rest were not handled)",
        "run.stats": "Statistics: {success} succeeded, {skip} skipped, {fail} failed",
        "run.failed_reasons": "Failure breakdown: {summary}",
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
    # ---- 【Modify】CBZ ComicInfo modification mode ----
    "modify.header": "  [Modify] {count} CBZ file(s) will have ComicInfo.xml updated",
    "modify.plan": "  [will modify] {name}",
    "modify.plan_add": "    + {field}: {value} (new)",
    "modify.plan_change": "    ~ {field}: {old} -> {new}",
    "modify.done": "  [Modified] {name}: ComicInfo.xml updated",
    "modify.nochange": "  [Modified] {name}: no field changes, untouched",
    "modify.fail": "  [Failed] {name}: {err}",
    "modify.stats": "  Modify done: success {success}, unchanged {nochange}, failed {fail}",
    "modify.failed_reasons": "Modify failure reasons: {summary}",
    "modify.dryrun_end": "  Dry-run finished: no CBZ was actually modified",
    "progress.desc.modify": "Modifying",
    "rename_cbz.header": "  [Rename] {count} CBZ file(s) will be renamed",
    "rename_cbz.done": "  [Renamed] {name} -> {new}",
    "rename_cbz.nochange": "  [Rename] {name}: filename needs no change",
    "rename_cbz.skip_existing": "  [Skip] {name}: target file already exists: {target} (add --overwrite to overwrite)",
    "rename_cbz.skip_conflict": "  [Skip] {name}: renamed target collides with another file in this batch: {target} (consider adjusting the naming template)",
    "rename_cbz.fail": "  [Failed] {name}: {err}",
    "rename_cbz.failed_reasons": "Rename failure reasons: {summary}",
    "rename_cbz.stats": "  Rename done: ok {success}, no-change {nochange}, skipped {skip} (existing {existing}, conflict {conflict}), failed {fail}",
    "rename_cbz.skipped_existing_header": "  Skipped (target already exists on disk) {count}:",
    "rename_cbz.skipped_conflict_header": "  Skipped (name conflict within batch) {count}:",
    "rename_cbz.dryrun_end": "  Dry-run finished: no CBZ was actually renamed",
    "progress.desc.rename": "Renaming",
    "tag.rename_preview": "[Rename preview]",
    "setinfo.whitelist_skip": "  [Warning] {field} is not in the ComicInfo whitelist, ignored",
    "setinfo.unknown_placeholder": "  [Warning] Unknown placeholder {raw}, written as-is",
    "setinfo.invalid_manga": "  [Warning] Invalid Manga value '{value}' (allowed: Unknown/No/Yes/YesAndRightToLeft), ignored",
    "convert.source_newer_reconvert": "  [Info] Target {name} exists but the source is newer, reconverting automatically",
    "inspect.pagecount_mismatch": "  [Info] ComicInfo PageCount={declared} does not match actual image count {actual}",
    "inspect.pagecount_non_numeric": "  [Warn] ComicInfo PageCount is not numeric: {raw}",
    },
    "ja": {
        "error.missing_dependency": '【致命的エラー】必須依存ライブラリ mobi がありません。インストールを実行してください：',
        "error.log_write_failed": '【警告】ログの書き込みに失敗しました（{err}）、ログファイル: {path}、以降のログは書き込みません',
        "error.json_write_failed": '【警告】JSON 結果の書き込みに失敗しました（{err}）、パス: {path}',
        "error.ext_priority_empty": "--ext-priority を空にすることはできません",
        "error.ext_priority_invalid": "--ext-priority は mobi/azw/azw3/epub のみ受け付けます。受信: {p}",
        # ---- --help 文案 ----
        "help.description": 'mobi/azw/azw3/epub 漫画を一括で cbz に変換',
        "help.language": '出力言語：auto はシステム言語で自動判定（zh プレフィックス→中国語、zh-TW/zh-Hant→繁体字中国語、ja/Japanese→日本語、それ以外→英語）、または zh-CN/zh-TW/ja/en を指定（zh/cn/zhtw/jp などの一般的な表記も許容）',
        "help.target": '電子書籍ファイルのパス、電子書籍（.mobi/.azw/.azw3/.epub）を含むディレクトリ、または * / ? を含むグロブパターン（例: *.epub）；カレントディレクトリを処理するには . を指定',
        "help.delete": '変換成功後に元の電子書籍ファイルを削除',
        "help.prefer": '二重ディレクトリ mobi（mobi7/mobi8）がある場合にどちらを残すか：auto（デフォルト）は mobi8 優先、空なら mobi7 に自動フォールバック。mobi7/mobi8 指定時も、指定先が空ならもう一方に自動フォールバック',
        "help.ext_priority": '同じディレクトリで同名（拡張子のみ異なる）の場合にどの形式を残すか：カンマ区切り、順序が優先度（高→低）、mobi/azw/azw3/epub のみ指定可能、デフォルト azw3；優先度がカバーしない場合は azw3→epub→mobi→azw にフォールバック；--prefer（二重ディレクトリ選択）とは無関係',
        "help.drop_extra": "目次外の余分な画像を破棄（隠しエイリアス、--drop extra に統合）：値なし=目次外の余分な画像を破棄（デフォルトは末尾に追加）；off/no/0 で無効；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください",
        "help.drop": "指定した形式・条件の画像を破棄（統合破棄エントリ）：値なし/extra=目次外の余分な画像を破棄（デフォルトは末尾に追加）；形式語でその形式を破棄（例: gif）；条件語でフィルタ（small[=比率] 小画像、超大、疑似回転見開き、異常、表紙、アスペクト比など、中/日/英の別名対応）；off/no/0 で無効；複数条件はカンマ=OR、プラス=AND、- プレフィックスで除外；--list-images と同一フィルタエンジン；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください",
        "help.overwrite": '対象 cbz が既に存在する場合に強制的に再生成（デフォルトはスキップ）',
        "help.timeout": 'ファイルごとの変換タイムアウト秒数。タイムアウトで自動スキップし失敗に計上（デフォルト 600、0 は制限なし。タイムアウト後、基盤の解凍スレッドがバックグラウンドに残る可能性あり）',
        "help.min_size": '指定バイト数未満の電子書籍を除外；数字なしでデフォルト 1000 バイト、0 でサイズフィルタ無効、未指定で無効；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください',
        "help.output_dir": "CBZ を指定ディレクトリに出力（自動作成）、デフォルトでは入力の相対サブディレクトリ構造を保持（例: Sample Series/001.mobi → DIR/Sample Series/001.cbz）、--flatten でルートにフラット化",
        "help.top_only": "target ディレクトリ直下の電子書籍のみ処理（サブディレクトリへ再帰しない）",
    "help.flatten": "--output-dir との併用時のみ：全 CBZ を出力ディレクトリのルートにフラット化、同名ファイルは --overwrite 指定時のみ上書き、未指定時はスキップ（SKIP）；単独使用はエラー終了",
        "help.dry_run": '試運転：ファイルをスキャンして変換フローを表示するだけで、解凍・パッキング・出力ディレクトリ作成は行わない',
        "help.progress": 'プログレスバー表示ポリシー：auto は TTY かつファイル数≥2 かつ --json/--json-out 未使用時に表示；on は強制表示；off は強制オフ（デフォルト off で非表示）；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください',
        "help.no_progress": 'プログレスバーを強制オフ（TTY かつファイル数≥2 でも）',
        "help.quiet": '静音モード：エラーと最終サマリーのみ表示（ログファイルには影響なし）',
        "help.no_color": 'ANSI カラー出力を無効化（ターミナルが対応していても無効化）。ログ/JSON/パイプ出力には元々色が付かない',
        "help.debug": 'デバッグ情報を出力（debug レベルは stderr へ；ログファイルには常時記録）',
        "warn.cleanup_tmp_fail": '一時ディレクトリの削除に失敗 {path}: {err}',
        "warn.disk_space": 'ディスク容量不足：{label} {path} 残り {free_mb} MB < 必要見込み {need_mb} MB',
        "help.short_summary": '簡潔サマリー：成功/スキップのファイルはパスを列挙せず数のみ表示、失敗ファイルは常にフルパス表示',
        "help.compress": 'zip 圧縮レベル 0-9：0=無圧縮（デフォルト、画像は既に圧縮済み）、1-9=deflate 圧縮（PNG 元で効果あり、レベルが高いほど小さく遅い）',
        "help.inspect": '検査モード：sample はランダムに 1 冊を抽出（デフォルト）、all は全件検査；フィルタ [MODE][,FILTER] 付き（例: all,small=0.6）で条件一致画像の件数+ファイル名一覧を出力、FILTER の構文は --drop と同一（カンマ=OR、プラス=AND、- 接頭辞で除外）；解凍して内部情報（メタデータ/構造/画像/解像度/DRM）を読み取るだけで CBZ は生成せず、終了後に一時ディレクトリを自動削除；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください',
        "help.inspect_all": '全電子書籍を検査（--inspect all と等価、旧コマンド互換用）',
        "help.no_comicinfo": "ComicInfo.xml を生成しない（既定: CBZ ルートに漫画メタデータを書き込む）",
        "help.double_page": "見開き検出：値なし/auto で有効（閾値 2.0）；数値で閾値調整；off/no/0 で無効（有効時はページ毎の DoublePage を書き込むが Manga 要素は書かない；Manga が必要なら --setinfo Manga= を使用）；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください",
        "error.double_page_invalid": "無効な --double-page 値 '{value}'：auto/数値/off/no/0 のいずれか",
        "help.drop_small": "小画像を破棄（隠しエイリアス、--drop small に統合）：明らかに小さい画像を変換時に除外（面積 幅×高さ が 面積中央値×比率 未満で小画像と判定；値なし/auto=0.5、0〜1 の数値で比率調整、off/no/0 で無効）。破棄後は PageCount を実画像数で再計算；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください",
        "error.drop_small_invalid": "無効な --drop-small 値 '{value}'：auto または数値(0〜1) のいずれか",
        "convert.drop_small": "  [クリーン] 小画像を {count} 枚破棄{names}",
        "run.drop_small_total": "破棄した小画像の合計: {count} 枚",
        "inspect.drop_small_preview": "  [注意] 小画像が {count} 枚（--drop small 有効時は破棄されます）",
        "inspect.filter_hits": "  [ヒット] {count} 枚の画像がフィルタ条件に一致（--inspect フィルタ）",
        "inspect.filter_no_hit": "  [該当なし] フィルタ条件に一致する画像はありません",
        "help.setinfo": "ComicInfo フィールドを設定（複数可、形式 FIELD=VALUE；VALUE は %series/%number/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M をサポート（%subN_M=N 文字目から M 文字、1-based）；カンマ直後にフィールド名= がある場合のみ分割、値に Key= 構造が含まれる場合は --setinfo を複数回指定；Manga は Unknown/No/Yes/YesAndRightToLeft のみ有効、デフォルトでは書かない；--setinfo 有効時、入力中の既存 .cbz は ComicInfo.xml を直接変更）",
"help.rename": "出力 CBZ のファイル名をリネーム（テンプレート任意、デフォルト無効）。--rename 値なし=デフォルトテンプレート（シリーズ名+自動マーク接頭辞）；マーク接頭辞は種類別に自動選択：単巻[Vol.x]/単話[Ch.x]/巻+話[Vol.x][Ch.x]/型なし[x]、連話（話005-006）は [Ch.5-6]；プレースホルダ %series/%number/%volume/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M と %03number ゼロ埋め；優先順位：ファイル名推測 > ファイルメタデータ(OPF/ComicInfo.xml)、setinfo は不参加；%description はファイル名への使用は推奨しません（内容が非常に長くなる可能性があります）。使用する場合は %subN_M で切り出してください；--dry-run でプレビュー推奨；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください",
        "comicinfo.generating": "ComicInfo.xml を生成中",
        "comicinfo.created": "ComicInfo.xml を書き込みました",
        "comicinfo.disabled": "ComicInfo.xml は無効です（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml が無効、または生成に失敗しました: {err}",
        "comicinfo.build_fail": "ComicInfo.xml の生成に失敗しました: {err}",
        "comicinfo.write_fail": "ComicInfo.xml の書き込みに失敗しました: {err}",
        "comicinfo.src.setinfo": "setinfo",
        "comicinfo.src.opf": "OPF",
        "comicinfo.src.inferred": "推定",
        "help.log": 'すべての出力を指定ログファイルに追記（ファイル名を省略するとタイムスタンプ付きログを自動生成）；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください',
        "help.json": '単一行のコンパクトな JSON 結果を stdout に出力（AI/パイプ読み取り用）。有効時は人間向けテキスト出力を抑制。変換/変更モードでは全体を 1 行のコンパクト JSON、inspect モードではファイルごとに 1 行のスリム JSON、dry-run では dry_run フラグ付きで出力。unpack モードのみ出力しない。プログレスバーは stderr に書き込まれ JSON と混ざらないが、2>&1 で結合リダイレクトすると混入する',
        "help.json_out": '変換結果を JSON ファイルに書き出し（ファイル名省略でタイムスタンプ付きファイルを自動生成、またはパス指定。--json と同様、変換/変更モードのみ書き込み）；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください',
        "log.auto_named": 'ログファイル: {path}（自動命名）',
        "json.written": 'JSON 結果を書き込みました: {path}',
        "help.unpack": '解凍モード：解凍のみで変換は行わず、元ファイルと同じディレクトリの「元名_拡張子」サブディレクトリに出力（例 vol.cbz → vol_cbz/、元ファイルと衝突しない）。_cbz で終わる解凍ディレクトリは --repack で再パックできます',
        "unpack.done": '解凍しました {name} -> {dir}',
        "help.repack": '再パックモード：解凍済みの CBZ ディレクトリ（_cbz で終わるディレクトリ名）を CBZ に再パック（出力名は元ファイル名に復元、例 vol_cbz → vol.cbz）。--setinfo と併用してメタデータを編集できます（--rename はこのモードでは使用できません）',
        "repack.none_found": '_cbz で終わる解凍ディレクトリが見つかりません: {path}',
        "repack.no_images": '[エラー] {dir}: ディレクトリ内に画像が見つかりません',
        "repack.skip_exists": '[スキップ] {path} は既に存在します（--overwrite で強制上書き）',
        "repack.done": '[完了] {name}: 画像 {count} 枚、{size} MB',
        "repack.fail": '[失敗] {dir} の再パックに失敗: {err}',
        "repack.done_summary": '再パック完了：成功 {ok} 件、失敗 {fail} 件',
        "repack.plan": '再パックする解凍ディレクトリ {count} 件：',
        "repack.rename_ignored": 'ヒント：--repack モードでは --rename は適用されず無視しました（出力ファイル名は解凍ディレクトリ名から推測）',
        "unpack.plan": '解凍するファイル {count} 件：',
        "unpack.done_summary": '解凍完了：成功 {ok} 件、失敗 {fail} 件',
        "error.repack_need_dir": 'repack モードはディレクトリのみ受け付けます（_cbz で終わる解凍ディレクトリ、または *_cbz 解凍ディレクトリを含む親ディレクトリ）: {path}',
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
        # ---- 【清单】--list-images / --drop-extra 共用文案 ----
        "anom.animated": "アニメ ({frames} フレーム)",
        "anom.extra_append": "目次外画像（デフォルトは末尾に追加）",
        "anom.extra_drop": "目次外画像（--drop-extra で破棄）",
        "anom.small": "異常に小さい",
        "anom.overscale": "特大ページ",
        "anom.rotated_double": "回転見開き",
        "anom.thumbnail": "縮小サムネイル",
        "convert.drop_filter": "フィルタで {count} 枚の画像を破棄{names}",
        "dir.landscape": "横向き",
        "dir.portrait": "縦向き",
        "dir.square": "正方形",
        "error.filter_token": "無効なフィルタ条件 '{token}'（式: {expr}）",
        "help.list_images": "電子書籍内の画像一覧を表示（読み取り専用、変換・CBZ 生成なし）：値なしで全件表示；FILTER で行をフィルタ（カンマ=OR、'+'=AND；カテゴリ：形式/extra/res/size/向き/モード/色深度/マーク、例: gif,res<200 または jpg+size>1mb）；--drop-extra と同一フィルタエンジンを共有；一覧の [異常]/[推測] は集計/推測マーク、[追加]/[破棄]/[フィルタ] は append/drop/filter の処置に対応；--json でファイル毎に簡潔 JSON；--quiet でカウントのみ；値を渡す場合は --オプション=値 の形式にするか、対象パスをこのオプションの前に置いてください",
        "inspect.status_fail": "一覧の抽出に失敗: {err}",
        "list.animated": "アニメ: {n} 枚",
        "list.anomaly": "異常画像: {n} 枚",
        "list.anomaly_item": "  - {name}: {dim} ({desc})",
        "list.badzip": "有効な zip ファイルではありません（{err}）",
        "list.col.dir": "向き",
        "list.col.file": "ファイル",
        "list.col.mark": "マーク",
        "list.col.mode": "モード/色深度",
        "list.col.no": "No.",
        "list.col.res": "解像度",
        "list.col.size": "サイズ",
        "list.col.toc": "目次",
        "list.double": "見開き: {n} 枚",
        "list.fail": "一覧取得に失敗: {err}",
        "list.file_line": "ファイル: {name}",
        "list.fmt": "形式: {parts}",
        "list.mode": "モード/色深度: {parts}",
        "list.no_images": "画像が見つかりません",
        "list.no_match": "条件に一致する画像がありません",
        "list.res_item": "  {w}×{h} {count} 枚 ({pct}%)",
        "list.res_other": "  その他 {count} 枚 ({pct}%)",
        "list.res_other_note": "（サイズばらつき大、スキャン差異の可能性あり）",
        "list.res_title": "サイズ分布:",
        "list.small": "小画像: {n} 枚",
        "list.drop_small_note": "[ヒント] 小画像閾値 = 面積中央値 × {ratio}（--drop-small で調整可）",
        "list.total": "画像総数: {n} 枚",
        "list.quiet_summary": "[ヒント] 計 {n} 枚中 {anomalies} 枚異常（--quiet で明細非表示）",
        "mark.animated": "[アニメ]",
        "mark.extra": "[余分]",
        "mark.cover": "[表紙]",
        "mark.double": "[見開き]",
        "mark.thumbnail": "[縮小サムネ]",
        "mark.small": "[異常小画像]",
        "mark.filter": "[フィルタ]",
        "mark.drop": "[破棄]",
        "mark.append": "[追加]",
        "mark.overscale": "[特大ページ]",
        "mark.rotated_double": "[回転見開き]",
        "mark.anom": "[異常]",
        "mark.inferred": "[推測]",
        "unpack.path_skip": "[警告] {name}: 安全でない展開パス {entry} をスキップ",
        "progress.desc.convert": '変換中',
        "progress.desc.dry_run": '試運転',
        "progress.desc.inspect": '検査中',
        "progress.done": '{desc}: [{n}/{total}] 完了',
        # ---- 去重 ----
        "dedupe.fallback": '  [重複除去] 拡張子優先度 [{priority}] がこのグループをカバーしていないため、フォールバック順に戻ります: {order}',
        "dedupe.reason": '同じディレクトリで同名のため、--ext-priority {priority} に従い {name} を保持',
        "dedupe.both_dirs": '  [重複除去] 二重ディレクトリを検出、{dir} を保持',
        "dedupe.auto_fallback": '  [重複除去] 二重ディレクトリ、mobi8 が空のため mobi7 に自動フォールバック',
        "dedupe.prefer_empty_fallback": '  [重複除去] {prefer} を指定したが画像なし、{fallback} に自動フォールバック',
        # ---- 目录对齐 ----
        "align.drop": '  [情報] ディレクトリ内の未収集画像 {count} 枚を --drop-extra により破棄{names}',
        "align.append": '  [情報] ディレクトリ内の未収集画像 {count} 枚を末尾に追加{names}',
        # ---- 【转换】转换流程 ----
        "convert.skip_exists": '  [スキップ] 対象は既に存在: {name}',
        "convert.flatten_conflict_skip": '  [警告] フラット同名衝突: {src} は既存の {name} と同名のためスキップ（flatten）。上書きする場合は --overwrite を指定してください',
        "convert.skip_corrupt_reconvert": '  [情報] 対象 {name} は存在しますが検証に失敗したため（{reason}）、自動的に再変換します',
        "convert.overwrite": '  [上書き] 古いファイルを上書きし再生成: {name}',
        "convert.spine": '  [ソート] OPF spine 順に抽出（{count} 枚）',
        "convert.spine_empty": '  [ソート] spine 抽出が空のため、ファイル名順にフォールバック（{count} 枚）',
        "convert.dedup_physical": '  [重複排除] 物理的に重複する {count} ファイルをスキップ（同一ファイルが重複出現、CBZ に書き込みません）',
        "convert.no_opf": '  [ソート] OPF が見つからないため、ファイル名順にフォールバック（{count} 枚）',
        "convert.multi_opf": '  [ソート] OPF ファイルが {count} 個検出、最初のものを使用: {first}',
        "convert.no_images": '  [失敗] 画像が見つかりません: {name}',
        "convert.drm_hint": '  [情報] DRM 暗号化された Kindle 漫画の可能性があります。mobi ライブラリでは復号できないため、DRM を除去してから再変換してください',
        "convert.drm_hint_epub": '  [情報] この EPUB から画像を解析できませんでした。漫画画像が含まれ、暗号化されていないことを確認してください',
        "convert.count_mismatch": '  [情報] ディレクトリ内の画像は {total} 枚、収集は {collected} 枚で不一致',
        "convert.done": '  [完了] {name} ({count} 枚の画像, {size} MB)',
        "convert.verify_fail": '  [検証失敗] {name}: {msg}、元ファイルを保持しました',
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
        "inspect.drm_marked_try": '  ヒント: ヘッダーに DRM フラグあり、解凍を継続して試行',
        "inspect.drm_hint": '  ヒント: ヘッダーに DRM フラグがあり解凍に失敗。内容が暗号化されている可能性があるため、先に DRM を除去してください',
        "inspect.drm_but_readable": '  DRM: あり（ヘッダーフラグ）だが読み取り可能（画像 {count} 枚）',
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
        "inspect.nav_count": '  目次(EPUB3 nav): {count} エントリ | プレビュー: {preview}',
        "inspect.nav_missing": '  目次(EPUB3 nav): 見つからない',
        "inspect.dir_images": '  ディレクトリ内の全画像: {count} 枚',
        "inspect.drm_suspected": '  DRM: 疑いあり（ヘッダーフラグなし、画像 0 枚）',
        "inspect.cover_missing": '  カバー画像が見つかりません',
        "inspect.fmt_none": '  画像形式統計: 集計できる画像なし',
        "inspect.drm_bad_hint": '  ヒント: DRM 暗号化または内容破損の疑い。変換は失敗するため先に DRM を除去してください',
        "inspect.drm_none": '  DRM: なし（ヘッダーフラグなし、画像 {count} 枚）',
        "inspect.cover_src_guide": 'OPF guide 公式参照',
        "inspect.cover_src_filename": 'ファイル名一致',
        "inspect.cover_found": '  カバー画像が見つかりました: {name}（{src}）{dim} {size}',
        "inspect.fmt_stats": '  画像形式統計（合計 {total} 枚）: {parts}',
        "inspect.res_main_h": '主な高さ {height} ({count}枚, {pct}%)',
        "inspect.res_w_range": '幅 {min}~{max}',
        "inspect.res_main_w": '主な幅 {width} ({count}枚, {pct}%)',
        "inspect.res_h_range": '高さ {min}~{max}',
        "inspect.res_line": '  解像度: {parts}',
        "inspect.res_summary": '  解像度サマリー: 主解像度 {w}x{h} 計 {count} 枚 ({pct}%)；異常小図 {small} 枚',
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
        "run.no_ebooks": '電子書籍ファイル（.mobi/.azw/.azw3/.epub）が見つかりません: {path}',
        "run.precheck_header": 'プリチェックで {count} ファイルをスキップ：',
        "run.none_convertible": '変換できる有効な電子書籍ファイルがありません（すべてプリチェックまたは同名重複で除外）',
        "run.found": '有効な電子書籍 {total} ファイルを検出（プリチェックで {pre} 除外、同名重複で {dedup} 除外）\n',
        "run.dryrun_banner": '[試運転] --dry-run モード：スキャンしてフローを表示するのみ。解凍・パッキング・出力ディレクトリ作成は行いません',
        "dryrun.output_not_writable": '  [警告] 出力ディレクトリが書き込み不可です: {path}。正式な変換は失敗します',
        "run.plan_output_dir": '出力予定ディレクトリ: {path}（正式変換時のみ自動作成）',
        "run.dryrun_precheck": '試運転でプリチェックにより {count} ファイルをスキップ：',
        "run.dryrun_end": '試運転終了。出力ファイルやフォルダは作成されませんでした',
        "run.stale_tmp": "  [ヒント] 前回の中断・異常で残った不完全な一時ファイル *.cbz.tmp が {count} 個あります。確認後手動で削除してください（自動削除はしません）",
        "run.start": '{count} ファイルの変換を開始...\n',
        "run.timeout": '  [タイムアウト] {name}: 変換が {seconds} 秒を超えたためスキップ（失敗に計上）',
        "run.timeout_residue": '  [ヒント] 変換がタイムアウトしました。基盤の展開スレッドが残っている可能性があります。多数発生時はスクリプトを再起動してください',
        "run.elapsed": '  [経過時間] {name}: {seconds} 秒',
        "rename.preview": '  [リネーム] {old} -> {new}',
        "run.ctrl_c": '\nCtrl+C を検出、変換を中断し現在の進捗サマリーを表示：',
        "run.done": '\n変換完了: {success}/{total} 成功',
        "run.interrupted_note": '（タスクは中断されました。上記は処理済み部分のサマリーで、残りは未処理です）',
        "run.stats": '変換統計: 成功 {success} 件, スキップ {skip} 件, 失敗 {fail} 件',
        "run.failed_reasons": '失敗の内訳: {summary}',
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
    # ---- 【変更】CBZ ComicInfo 変更モード ----
    "modify.header": '  [変更] 合計 {count} 個の CBZ の ComicInfo.xml を更新します',
    "modify.plan": '  [変更予定] {name}',
    "modify.plan_add": '    + {field}: {value}（新規）',
    "modify.plan_change": '    ~ {field}: {old} → {new}',
    "modify.done": '  [変更] {name}: ComicInfo.xml を更新しました',
    "modify.nochange": '  [変更] {name}: フィールド変更なし、変更なし',
    "modify.fail": '  [失敗] {name}: {err}',
    "modify.stats": '  変更完了：成功 {success}、変更なし {nochange}、失敗 {fail}',
    "modify.failed_reasons": '変更失敗理由: {summary}',
    "modify.dryrun_end": '  試行終了：実際にはどの CBZ も変更されていません',
    "progress.desc.modify": '変更中',
    "rename_cbz.header": '  [リネーム] 合計 {count} 個の CBZ のファイル名をリネームします',
    "rename_cbz.done": '  [リネーム] {name} -> {new}',
    "rename_cbz.nochange": '  [リネーム] {name}: ファイル名の変更は不要です',
    "rename_cbz.skip_existing": '  [スキップ] {name}: 対象ファイルは既に存在します: {target}（上書きする場合は --overwrite を指定してください）',
    "rename_cbz.skip_conflict": '  [スキップ] {name}: リネーム後にこのバッチ内の別ファイルと衝突します: {target}（命名テンプレートの調整をお勧めします）',
    "rename_cbz.fail": '  [失敗] {name}: {err}',
    "rename_cbz.failed_reasons": 'リネーム失敗理由: {summary}',
    "rename_cbz.stats": '  リネーム完了：成功 {success}、変更なし {nochange}、スキップ {skip}（ディスク同名 {existing}、バッチ内撞名 {conflict}）、失敗 {fail}',
    "rename_cbz.skipped_existing_header": '  スキップ（ディスクに同名が既に存在）{count} 件：',
    "rename_cbz.skipped_conflict_header": '  スキップ（バッチ内で名前が重複）{count} 件：',
    "rename_cbz.dryrun_end": '  試行終了：実際にはどの CBZ もリネームされていません',
    "progress.desc.rename": 'リネーム中',
    "tag.rename_preview": '[リネームプレビュー]',
    "setinfo.whitelist_skip": '  [警告] {field} は ComicInfo ホワイトリストにありません。無視します',
    "setinfo.unknown_placeholder": '  [警告] 不明なプレースホルダ {raw}、そのまま書き込みます',
    "setinfo.invalid_manga": '  [警告] 無効な Manga 値 \'{value}\'（指定可能: Unknown/No/Yes/YesAndRightToLeft）。無視します',
    "convert.source_newer_reconvert": '  [情報] 対象 {name} は存在しますがソースが新しいため、自動的に再変換します',
    "inspect.pagecount_mismatch": '  [情報] ComicInfo の PageCount={declared} は実際の画像数 {actual} と一致しません',
    "inspect.pagecount_non_numeric": '  [警告] ComicInfo の PageCount が数値ではありません: {raw}',
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
    # 其余为 ja 前缀（日文），显式返回 ja
    return "ja"


# --language 参数容错：常见写法 → LANGUAGES 合法键（zh-CN/zh-TW/ja/en）
_UI_LANG_ALIASES = {
    "zh": "zh-CN", "cn": "zh-CN", "zhcn": "zh-CN", "chinese": "zh-CN", "zh-hans": "zh-CN",
    "zhtw": "zh-TW", "tw": "zh-TW", "hant": "zh-TW", "zh-hant": "zh-TW", "traditional": "zh-TW",
    "jp": "ja", "japanese": "ja",
    "eng": "en", "english": "en",
    "auto": "auto",
}


def _normalize_lang(lang: str) -> str:
    """把 --language 的常见写法规范化为 LANGUAGES 合法键（zh-CN/zh-TW/ja/en），无法识别回退 en。"""
    if not lang:
        return "en"
    s = lang.strip().lower().replace("_", "-").replace(".", "-")
    # 1) 直接匹配合法键（大小写不敏感）
    for key in LANGUAGES:
        if key.lower() == s:
            return key
    # 2) 去分隔符匹配（zhtw / zhcn）
    compact = s.replace("-", "")
    for key in LANGUAGES:
        if key.lower().replace("-", "") == compact:
            return key
    # 3) alias 容错表
    if s in _UI_LANG_ALIASES:
        return _UI_LANG_ALIASES[s]
    if compact in _UI_LANG_ALIASES:
        return _UI_LANG_ALIASES[compact]
    return "en"


def set_language(lang: str) -> None:
    """设置当前语言；auto 按系统 locale 判定，未知语言回退 en"""
    global CURRENT_LANGUAGE
    if lang == "auto":
        lang = _auto_language()
    else:
        lang = _normalize_lang(lang)
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
        # 开发辅助：--debug 下占位符/模板写错时打 stderr 告警，避免 i18n 静默失效；
        # globals().get 防御 t() 在模块加载早期（_debug_mode 初始化前）即被调用
        if globals().get("_debug_mode"):
            print(f"[i18n] t({key!r}) format failed: tmpl={tmpl!r} kwargs={kwargs}", file=sys.stderr)
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
# 校验 CBZ 时只读 ZIP 尾部多少字节即可命中 EOCD 记录（> 单条 EOCD 最大长度 65557 字节）
ZIP_EOCD_READ_TAIL = 70000
OPF_NS = {"opf": "http://www.idpf.org/2007/opf"}

# 支持的电子书输入扩展名（大小写不敏感）；同名去重未覆盖时的兜底优先级
SUPPORTED_INPUT_EXTENSIONS = {".mobi", ".azw", ".azw3", ".epub"}
# 单文件转换超时默认值（秒），0 表示不限制
DEFAULT_TIMEOUT = 600
KEEP_EXT_ORDER = (".azw3", ".epub", ".mobi", ".azw")  # --ext-priority 未覆盖时的兜底顺序

# 头部探测缓冲区大小：读取文件头/条目前部用于搜索 EXTH 魔数、图片尺寸探测等。
# 65536 字节（64KB）覆盖 EXTH 记录常见偏移与 PNG/JPEG 头尾对齐，远超实际需要；
# 统一收敛为常量避免 5 处魔数散布。
HEAD_READ_BYTES = 65536
# 安全下限：EXTH 记录位置必须落在 (0, HEAD_READ_BYTES-12) 区间，
# 12 = 8 字节文件头 + 4 字节记录头，越界即判定无 EXTH。
EXTH_MAX_OFFSET = HEAD_READ_BYTES - 12


def parse_ext_priority(value: str) -> list[str]:
    """解析 --ext-priority：逗号分隔、仅接受 mobi/azw/azw3/epub、顺序即优先级（高→低）。

    输入：命令行传入的原始字符串（如 "azw3,mobi"）。
    输出：规范化后的扩展名优先级列表（如 ["azw3", "mobi"]）；
    为空或含非法扩展名时抛 argparse.ArgumentTypeError（文案经 t() 多语言化）。
    """
    parts = [p.strip().lower() for p in value.split(",") if p.strip()]
    if not parts:
        raise argparse.ArgumentTypeError(t("error.ext_priority_empty"))
    for p in parts:
        if p not in ("mobi", "azw", "azw3", "epub"):
            raise argparse.ArgumentTypeError(t("error.ext_priority_invalid", p=p))
    return parts



class ConvStatus(str, Enum):
    """ebook_to_cbz 返回状态枚举，替代魔法字符串 ok/skip/fail，减少拼写错误"""
    OK = "ok"
    SKIP = "skip"
    FAIL = "fail"


class InspectStatus(str, Enum):
    """inspect_ebook 返回状态枚举，替代魔法字符串 ok/invalid/drm/noimg/fail"""
    OK = "ok"
    INVALID = "invalid"
    DRM = "drm"
    NOIMG = "noimg"
    FAIL = "fail"


# 输出标签不再定义常量，统一经 t("tag.xxx") 获取（多语言文案表在顶部 LANGUAGES）


def norm_path(p: Path) -> str:
    """路径归一化：resolve 后转小写，兼容 Windows 不区分大小写的文件系统，
    避免同名仅大小写差异的文件在对比时被误判为不同/重复。"""
    return str(p.resolve()).lower()


    # 输入：目标函数 func、超时秒数 timeout 及透传参数；输出：(timed_out, result) 二元组：
    # 超时 → (True, None)，正常 → (False, func 的返回值)
def estimate_expanded_size(path: Path) -> int:
    """估算解包后体积：zip 容器（epub/cbz）读中央目录求和；mobi/azw 无法预读按源大小粗估。"""
    if path.suffix.lower() in (".epub", ".cbz"):
        try:
            with zipfile.ZipFile(str(path)) as zf:
                return sum(i.file_size for i in zf.infolist())
        except Exception:
            pass
    return path.stat().st_size


# 磁盘可用空间缓存：批内 Output/Temp 目录固定不变，每文件预检只查询一次系统调用
_disk_free_cache: dict[str, int] = {}


def _disk_free(d: Path) -> int:
    """按目录缓存 shutil.disk_usage 可用字节（同一目录批内只查一次）。"""
    key = str(d)
    if key not in _disk_free_cache:
        _disk_free_cache[key] = shutil.disk_usage(d).free
    return _disk_free_cache[key]


def check_disk_space(target_dir: Path, temp_dir: Path, required_bytes: int) -> str | None:
    """磁盘空间预检：目标盘与临时盘可用空间是否足够（估算解包 + 输出，×2 余量）。

    任一目录无法检查（如网络盘）时跳过该项；返回 None=充足，否则返回不足提示文案。
    disk_usage 按目录缓存，批量场景不重复系统调用。"""
    need = required_bytes * 2
    for label, d in (("Output", target_dir), ("Temp", temp_dir)):
        try:
            free = _disk_free(d)
        except Exception:
            continue
        if free < need:
            return t("warn.disk_space", label=label, path=d, free_mb=free // (1024 * 1024), need_mb=need // (1024 * 1024))
    return None


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
    except (TimeoutError, concurrent.futures.TimeoutError):
        # Python 3.10 中 concurrent.futures.TimeoutError 为独立类，
        # 3.11 起才成为内置 TimeoutError 别名，两者都捕获保证跨版本一致
        return True, None
    finally:
        # wait=False：不等待可能永久阻塞的工作线程
        executor.shutdown(wait=False)

# 全局输出控制：--quiet 抑制 info 输出，--log 将输出同时写入文件，
# --short-summary 精简汇总（不逐条罗列成功/跳过文件路径），
# --compress 设置 zip 压缩级别（0=不压缩，1-9=deflate）
_debug_mode = False
_quiet_mode = False
_log_path = None
_log_write_failed = False
_short_summary = False
_compress_level = 0
_json_stdout = False
_json_out_path = None


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
    # 输出级别着色（仅 TTY 生效；日志写 _strip_ansi、JSON 人类文本走 stderr 均不受影响）：error=红 / warning=黄 / summary=青
    if _color_enabled:
        if level == "error":
            line = _c(31, line)
        elif level == "warning":
            line = _c(33, line)
        elif level == "summary":
            line = _c(36, line)
    if _log_path:
        try:
            with open(_log_path, "a", encoding="utf-8") as f:
                f.write(_strip_ansi(line) + "\n")
        except Exception as e:
            if not _log_write_failed:
                _log_write_failed = True
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + t("error.log_write_failed", err=e, path=_log_path))
    if level == "debug":
        # --debug：调试行仅在显式开启时输出到 stderr（--quiet 不压制显式调试意图；stdout 始终不输出，保护 --json）
        if _debug_mode:
            print(line, file=sys.stderr)
        return
    if _json_stdout:
        # --json 模式：stdout 只留 JSON，人类可读文本抑制（仍写日志文件）；错误/警告/汇总走 stderr
        if level in ("summary", "error", "warning"):
            print(line, file=sys.stderr)
    elif not _quiet_mode or level in ("summary", "error", "warning"):
        print(line)


def emit_json(files: list, success: int, skipped: int, failed: int, interrupted: bool, total_elapsed: float) -> None:
    """--json / --json-out 统一结果输出：构造结构化结果并输出到 stdout 或落盘。"""
    result = {
        "version": __version__,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "success": success,
            "skipped": skipped,
            "failed": failed,
            "interrupted": interrupted,
            "total_elapsed_sec": round(total_elapsed, 2),
        },
        "files": files,
    }
    if _json_out_path:
        try:
            with open(_json_out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            emit(t("json.written", path=_json_out_path), level="summary")
        except Exception as e:
            emit(t("error.json_write_failed", err=e, path=_json_out_path), level="error")
    if _json_stdout:
        # 单行紧凑 JSON；人类可读文本已被 emit 抑制（走 stderr），stdout 只留 JSON
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


def truncate_name(name: str, max_len: int = 40) -> str:
    """截断文件名用于进度条展示：超过 max_len 时保留尾部、前缀省略号"""
    if len(name) <= max_len:
        return name
    return "..." + name[-(max_len - 3):]


def should_show_progress(args, final_files: list) -> bool:
    """进度条显示策略（--progress auto|on|off，默认 off）：
    off → 不显示（默认）；on → 强制显示（非 TTY 也显示）；
    auto → stderr 为 TTY 且有效文件数 >= 2 且未用 --json/--json-out 时显示。
    旧 --no-progress 隐藏别名仍强制关闭（优先级最高）。
    """
    if args.no_progress:
        return False
    mode = args.progress
    if mode == "on":
        return True
    if mode == "off":
        return False
    # auto
    if args.json or args.json_out:
        return False
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
    def _try_int(s: str):
        try:
            return int(s)
        except ValueError:
            # 超长数字串（Python int 有最大位数限制）保留原字符串，避免中断排序
            return s.lower()
    return [_try_int(s) if s.isdigit() else s.lower() for s in re.split(r"(\d+)", p.name)]


    # 输入：cbz 文件路径；输出：(是否通过完整性校验, 校验结果消息)
def validate_cbz(cbz_path: Path, require_comicinfo: bool = False) -> tuple[bool, str]:
    """校验 cbz 文件完整性：检查 EOCD 记录存在且所有条目可正常读取。

    require_comicinfo=True 时追加 ComicInfo 校验：ComicInfo.xml 存在、
    可被标准 XML parser 解析、根节点为 ComicInfo。ComicInfo.xml 大小写
    按 ComicInfo 规范固定匹配（不做大小写模糊），避免误收非标准命名。

    返回 (ok, msg)：ok=True 时 msg 为 verify.ok（含条目数）；ok=False 时
    msg 为对应失败文案（no_eocd / bad_entry / badzip / exception）。

    边界说明：文件总大小 ≤ ZIP_EOCD_READ_TAIL（70000 字节）时读全文件，
    EOCD 必完整位于其中；更大文件只 seek 读末尾 70000 字节，内存峰值 O(70KB)。
    """
    # EOCD（End of Central Directory）位于 ZIP 文件末尾，只读尾部 ZIP_EOCD_READ_TAIL 字节即可命中；
    # 该值远大于单条 EOCD 记录的最大长度（约 65557 字节 = 64KB 注释 + 固定头部）。
    try:
        size = cbz_path.stat().st_size
        if size <= ZIP_EOCD_READ_TAIL:
            data = cbz_path.read_bytes()
        else:
            with open(cbz_path, "rb") as f:
                f.seek(-ZIP_EOCD_READ_TAIL, os.SEEK_END)
                data = f.read()
        if EOCD_SIGNATURE not in data:
            return False, t("verify.no_eocd")
        with zipfile.ZipFile(str(cbz_path)) as zf:
            bad = zf.testzip()  # 逐条目解压校验 CRC，返回首个损坏条目名（None=全部完好）
            if bad is not None:
                return False, t("verify.bad_entry", name=bad)
            if require_comicinfo:
                # ComicInfo 三连校验：存在 → 可被标准 XML parser 解析 → 根节点正确，
                # 任一不满足即视为无效（缺失用 err=missing 标识，区别于解析失败）。
                if "ComicInfo.xml" not in zf.namelist():
                    return False, t("comicinfo.invalid", err="missing")
                try:
                    parsed = safe_et_parse(zf.read("ComicInfo.xml")).getroot()
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
def collect_ebook_files(target: Path | str, include_cbz: bool = False, top_only: bool = False) -> list[Path]:
    """收集所有待转换的电子书文件（.mobi/.azw/.azw3/.epub），按路径排序保证处理顺序可预测。

    target 含 glob 通配符（* 或 ?）时按模式展开（如 "*.epub"、"卷*/001.mobi"），
    命中多个文件时按扩展名过滤后全量返回，作为平铺文件列表处理；
    include_cbz=True 时（--inspect / --unpack / --setinfo 模式）额外收集 .cbz，供检查或修改；
    top_only=True 时仅收集 target 目录顶层文件，不递归子目录。
    注意：递归遍历时会跳过以 '.' 开头的隐藏目录（如 .git/.hidden）——若用户漫画
    文件夹名以 '.' 开头，该目录会被静默排除；这是有意为之的默认行为。
    """
    exts = SUPPORTED_INPUT_EXTENSIONS | ({".cbz"} if include_cbz else set())
    tstr = str(target)
    # 通配符展开：只认 * 和 ? 为 magic（[] 字符类易与文件名中的方括号字面量冲突，不支持）
    if any(c in tstr for c in "*?"):
        matches = []
        for p in glob.glob(tstr, recursive=False):
            pp = Path(p)
            if pp.is_file() and pp.suffix.lower() in exts:
                matches.append(pp)
        return sorted(matches)
    target = Path(target)
    if target.is_file():
        if target.suffix.lower() in exts:
            return [target]
        return []
    if top_only:
        # 仅 target 目录顶层文件，不递归子目录
        try:
            with os.scandir(target) as it:
                return sorted(
                    (Path(e.path) for e in it
                     if e.is_file() and Path(e.name).suffix.lower() in exts),
                    key=lambda p: str(p),
                )
        except OSError:
            return []
    ebook_files = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if Path(f).suffix.lower() in exts:
                ebook_files.append(Path(root) / f)
    return sorted(ebook_files)


def precheck_ebook(p: Path, min_bytes: int) -> str | None:
    """预处理检查电子书文件（.mobi/.azw/.azw3/.epub），返回跳过原因；正常返回 None。

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
        if p.suffix.lower() in (".cbz", ".epub"):
            # CBZ/EPUB 为 zip 容器，无 BOOKMOBI 魔数；仍做大小下限与 0 字节检查
            size = p.stat().st_size
            if min_bytes > 0 and size < min_bytes:
                return t("precheck.small", size=size, min=min_bytes)
            if size == 0:
                return t("precheck.zero")
            return None
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
      KEEP_EXT_ORDER（azw3→epub→mobi→azw）。
    返回 (kept, skipped)：skipped 为 [(path, reason)]。
    """
    groups: dict[tuple, list[Path]] = {}
    kept: list[Path] = []
    skipped: list[tuple[Path, str]] = []
    for p in files:
        # .cbz 是转换产物，不参与 mobi/azw/azw3/epub 的同名去重，直接保留
        if p.suffix.lower() == ".cbz":
            kept.append(p)
            continue
        groups.setdefault((p.parent.resolve(), p.stem.lower()), []).append(p)

    priority_exts = [f".{e.lstrip('.')}" for e in ext_priority]
    priority_desc = " > ".join(ext_priority)

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


def sanitize_filename_component(name: str) -> str:
    """替换 Windows 文件名非法字符（<>:"/\\|?*）与 ASCII 控制字符（\x00-\x1f\x7f）为下划线，
    并去除 Windows 资源管理器会隐藏的尾部点/空格，保证各平台文件名可写"""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f]', "_", name)
    return re.sub(r"[. ]+$", "", name)


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


def target_cbz_path(ebook_path: Path, output_dir: Path | None, flatten: bool = False, input_root: Path | None = None) -> Path:
    """计算目标 cbz 路径。

    - output_dir 为 None：与源电子书同目录（历史行为）
    - output_dir + flatten=False：保留相对 input_root 的子目录结构；
      相对路径计算失败（跨盘符等）时回退 output_dir/stem.cbz 并输出 warning
    - output_dir + flatten=True：平铺到 output_dir 根下，返回首选目标名
      output_dir/base.cbz（不唯一化）；同名文件由上层按 SKIP/--overwrite 处理
    """
    if output_dir is None:
        return ebook_path.with_suffix(".cbz")
    if flatten:
        base = flat_base_name(ebook_path, input_root)
        return output_dir / (base + ".cbz")
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
    """在目录下递归查找 .opf 文件；存在多个时优先 content.opf / package.opf
    （EPUB/漫画 CBZ 的约定命名），无法区分才输出 warning 并取第一个"""
    found = list(base_dir.rglob("*.opf"))
    if not found:
        return None
    if len(found) > 1:
        for pref in ("content.opf", "package.opf"):
            for f in found:
                if f.name.lower() == pref:
                    return f
        emit(t("convert.multi_opf", count=len(found), first=found[0].name), level="warning")
    return found[0]


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
        if srcs:
            # 与 HtmlImgParser 兜底路径一致：unquote 处理 %XX 后再补一轮 HTML 实体解码
            # （正则本身不自动解码实体，畸形 HTML 中 &amp; 等实体 src 需手动还原，避免与 parser 路径结果不一致）
            srcs = [unescape(unquote(s)) for s in srcs]
        else:
            # 兜底：HtmlImgParser（实体自动解码 + unquote 处理 %XX），
            # 覆盖正则难以处理的属性顺序/换行/实体编码场景
            srcs = extract_img_srcs_with_parser(content)
        base_dir = html_path.parent
        result = []
        for src in srcs:
            if src.startswith(("data:", "http://", "https://", "//")):
                continue
            # 兼容带 query/fragment 的 src（如 image.jpg?width=800 / image.jpg#page1）
            clean = src.split("?", 1)[0].split("#", 1)[0]
            img_path = (base_dir / clean).resolve()
            if img_path.exists() and img_path.suffix.lower() in IMAGE_EXTENSIONS:
                result.append(img_path)
        return result
    except Exception:
        return []


def safe_et_parse(source: str | bytes | Path) -> ET.ElementTree:
    """安全解析 XML：拒绝实体声明（XXE / billion-laughs 防护），字符串路径防穿越。

    输入为路径或字节（与 ET.parse 的路径/文件对象入参不同，本函数
    主动读取字节并在解析前做实体声明检查）。返回类型与 ET.parse 一致
    （ElementTree），业务侧调用方式不变（tree.getroot()）。
    防护要点：
      - 拒绝含 <!ENTITY 的输入（XXE 与 billion-laughs 真正载体）；裸
        <!DOCTYPE（无实体声明）放行——Python ET 默认不加载外部 DTD，
        OPF/NCX 等规范文档常带合法 DOCTYPE，不应误杀元数据
      - 字符串路径拒绝路径穿越（含 .. 的相对路径）
      - 解析器禁用参数实体解析（XML_PARAM_ENTITY_PARSING_NEVER）
    """
    if isinstance(source, str):
        sp = Path(source)
        # 拒绝 .. 穿越；放行 ./ 前缀与纯相对路径（解包内 OPF/NCX 引用可能带 ./）
        if not sp.is_absolute() and ".." in sp.parts:
            raise ValueError(f"Unsafe path: {source}")
    raw = Path(source).read_bytes() if not isinstance(source, bytes) else source
    if re.search(rb"<!\s*ENTITY", raw, re.I):
        raise ET.ParseError("ENTITY declaration is not allowed (XXE protection)")
    parser = ET.XMLParser()
    try:
        parser._parser.SetParamEntityParsing(0)
    except Exception:
        pass
    return ET.ElementTree(ET.fromstring(raw, parser=parser))


def extract_images_by_spine(opf_path: Path) -> list[Path] | None:
    """按 OPF spine 顺序提取图片。成功返回图片路径列表，失败返回 None"""
    try:
        tree = safe_et_parse(opf_path)
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


def align_images_with_dir(images: list[Path], base_dir: Path, drop_extra) -> tuple[list[Path], str | None]:
    """目录对齐兜底：把目录中存在但未被收集的图片补齐到末尾。

    drop_extra: --drop-extra 过滤表达式（parse_drop_expr 结果），None=关闭；
                条件中含 extra（丢弃多余图）时放弃追加，否则默认追加到末尾。

    返回 (处理后的图片列表, 处理说明文本或 None)：
    - 无多余图片：原样返回，说明为 None
    - 有多余图片且 drop_extra 含 extra：放弃追加并返回说明
    - 有多余图片且 drop_extra 不含 extra（或关闭）：追加到末尾并返回说明
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
    names_suffix = ": " + ", ".join(p.name for p in extras) if not _short_summary else ""
    drop_all_extra = bool(drop_extra) and any(("extra",) in g for g in drop_extra)
    if drop_all_extra:
        return images, t("align.drop", count=len(extras), names=names_suffix)
    return images + extras, t("align.append", count=len(extras), names=names_suffix)


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
    """根据 prefer 参数选择 mobi7 或 mobi8 目录；如果只有一份则返回那一份。

    prefer: "auto"（默认）双目录时优先 mobi8，mobi8 为空壳（无图片）自动回退 mobi7；
            明确指定 mobi7/mobi8 时，若指定目录为空但另一份有图片，warning 后回退到另一份。
    """
    mobi7_dir = tempdir / "mobi7"
    mobi8_dir = tempdir / "mobi8"

    has7 = mobi7_dir.is_dir()
    has8 = mobi8_dir.is_dir()

    def _has_images(d: Path) -> bool:
        return any(p.suffix.lower() in IMAGE_EXTENSIONS for p in d.rglob("*") if p.is_file())

    if has7 and has8:
        chosen = mobi7_dir if prefer == "mobi7" else mobi8_dir
        fallback = mobi8_dir if chosen is mobi7_dir else mobi7_dir
        if not _has_images(chosen) and _has_images(fallback):
            if prefer == "auto":
                emit(t("dedupe.auto_fallback"), level="warning")
            else:
                emit(t("dedupe.prefer_empty_fallback",
                       prefer="mobi7" if chosen is mobi7_dir else "mobi8",
                       fallback="mobi8" if chosen is mobi7_dir else "mobi7"), level="warning")
            chosen = fallback
        emit(t("dedupe.both_dirs", dir="mobi7" if chosen is mobi7_dir else "mobi8"))
        return chosen
    if has8:
        return mobi8_dir
    if has7:
        return mobi7_dir
    # 都没有子目录，直接用 tempdir
    return tempdir


    # 输入：电子书路径与转换选项（delete/prefer/drop_extra/overwrite/output_dir/compress）；输出：(cbz 路径或 None, ConvStatus, 原因, 来源)
def ebook_to_cbz(ebook_path: Path, delete_original: bool = False, prefer: str = "mobi8", drop_expr: object | None = None, overwrite: bool = False, output_dir: Path | None = None, compress: int = 0, flatten: bool = False, input_root: Path | None = None, comicinfo: bool = True, setinfo_args: list | None = None, double_page: float | None = None, rename_template: str | None = None) -> tuple[Path | None, ConvStatus, str | None, dict | None]:
    """将单个电子书文件转换为 cbz

    prefer: "auto"（默认）双目录时优先 mobi8，mobi8 为空壳（无图片）自动回退 mobi7
    drop_expr: 统一丢弃表达式（parse_drop_expr 结果，即 --drop/--drop-extra/--drop-small 合并后的
               组列表）；None=关闭。条件含 extra 时放弃追加多余图片；small 比例从表达式提取；
               其余条件在过滤阶段按格式/分辨率/大小/方向/模式/位深/标记丢弃
    overwrite: 目标 cbz 已存在时强制重新生成（默认跳过）
    output_dir: 指定 CBZ 输出目录（自动创建），默认与源 mobi 同目录
    flatten: 与 output_dir 联用时平铺到输出目录根下（默认保留相对子目录结构）
    input_root: target 为目录时作为相对子目录结构计算的基准
    comicinfo: 是否生成 ComicInfo.xml（默认生成，--no-comicinfo 关闭）
    double_page: 双页检测阈值（宽/高 >= 该值判为跨页），None 表示关闭（--double-page off）
    小图丢弃: 面积口径（宽×高 < 中位面积×比例），比例来自 drop_expr 内 small 条件（--drop small）
    rename_template: --rename 模板；None=关闭（保持原名），"default"=默认模板（系列名+自动标记前缀），
                其余为自定义模板（%series/%number/%volume 等占位符，自动补标记前缀）

    返回 (结果, 状态, 原因, 来源)：状态为 ConvStatus 枚举，
    - OK: 转换成功，结果为 cbz 路径，原因为 None，来源为 {series_source/number_source/cover_source/dropped_small} 字典
    - SKIP: 目标已存在且未指定 --overwrite，结果为 None，原因为 None，来源为 None
    - FAIL: 转换失败，结果为 None，原因为失败分类（no_images/drm/comicinfo/verify/other），来源为 None
    """
    rename_info = None
    if rename_template:
        new_stem, rename_info = _build_rename_basename(ebook_path, rename_template)
        cbz_path = _apply_rename_to_target(
            target_cbz_path(ebook_path, output_dir, flatten=flatten, input_root=input_root), new_stem)
        if rename_info["new_stem"] != rename_info["old_stem"]:
            emit(t("rename.preview", old=ebook_path.name, new=new_stem + ".cbz"), level="summary")
    else:
        cbz_path = target_cbz_path(ebook_path, output_dir, flatten=flatten, input_root=input_root)
    # 断点续跑：目标已存在（磁盘）且未指定 --overwrite 时，校验有效才跳过；损坏自动重转
    if cbz_path.exists() and not overwrite:
        ok, err = validate_cbz(cbz_path, require_comicinfo=comicinfo)
        if ok:
            # 源文件比目标新时也重转（mtime 比较），避免旧转换结果残留
            try:
                src_newer = ebook_path.stat().st_mtime > cbz_path.stat().st_mtime
            except OSError:
                src_newer = False
            if src_newer:
                emit(t("convert.source_newer_reconvert", name=cbz_path.name), level="warning")
            else:
                emit(t("convert.skip_exists", name=cbz_path.name))
                if flatten:
                    emit(t("convert.flatten_conflict_skip", name=cbz_path.name, src=ebook_path.name), level="warning")
                return None, ConvStatus.SKIP, None, None
        else:
            emit(t("convert.skip_corrupt_reconvert", name=cbz_path.name, reason=err), level="warning")
    # SKIP 判断之后才创建输出目录，避免为跳过文件产生空目录
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
    cbz_path.parent.mkdir(parents=True, exist_ok=True)
    if cbz_path.exists():
        emit(t("convert.overwrite", name=cbz_path.name))

    extract_temp_paths = []  # 记录mobi库自动生成的临时文件夹
    tmp_cbz = None  # 转换分支原子写入的临时文件（v2.2.1 原子替换）

    try:
        # mobi.extract 不支持 output_dir，仅传输入文件；epub 为 zip 容器走 zipfile 安全解包
        if ebook_path.suffix.lower() == ".epub":
            tempdir = extract_epub_to_temp(ebook_path)
        else:
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
            if ebook_path.suffix.lower() == ".epub":
                emit(t("convert.drm_hint_epub"), level="error")
            else:
                emit(t("convert.drm_hint"), level="error")
            return None, ConvStatus.FAIL, "no_images", None

        # 确保封面在第一位（兼容 cover/front 命名，封面可能未被 spine 引用）
        images = ensure_cover_first(images, base_dir)

        # 目录对齐兜底：目录图片数 vs 收集数不一致时，多出的图片追加到末尾
        # drop 表达式含 extra 条件时放弃追加（否则多余图默认追加，符合历史 --drop-extra 语义）
        total_in_dir = count_images_in_dir(base_dir)
        drop_extra_hit = bool(drop_expr and any(a[0] == "extra" for grp in drop_expr for a in grp))
        # P0-1 修复：传入原始 drop 表达式列表（函数内自行判定是否含 extra），不再传 bool，
        #           否则 --drop extra 且有多余图时 any(... for g in True) 抛 TypeError
        images, align_msg = align_images_with_dir(images, base_dir, drop_expr)
        # 小图比例从统一丢弃表达式提取（--drop small[=比例]）；None=关闭
        drop_small = extract_small_ratio(drop_expr)
        if align_msg:
            emit(f"  {align_msg}")
        elif total_in_dir != len(images):
            emit(t("convert.count_mismatch", total=total_in_dir, collected=len(images)))

        # 物理去重提前：PageCount 与打包均用去重后列表，保证一致性
        # （Step 4 打包仍保留 seen_paths 去重作防御，此时恒不触发）
        deduped = []
        seen_paths = set()
        for img in images:
            norm = norm_path(img)
            if norm in seen_paths:
                continue
            seen_paths.add(norm)
            deduped.append(img)
        if len(deduped) != len(images):
            emit(t("convert.dedup_physical", count=len(images) - len(deduped)))
        images = deduped

        # 丢弃小图（--drop small）：面积口径 宽×高 < 中位面积×比例 判为小图（封面缩略图等）
        dropped_small = 0
        if drop_small is not None:
            images, dropped_names = drop_small_images(images, drop_small)
            dropped_small = len(dropped_names)
            if dropped_names:
                names_suffix = ": " + ", ".join(dropped_names) if not _short_summary else ""
                emit(t("convert.drop_small", count=dropped_small, names=names_suffix))

        # 丢弃过滤（--drop 非 extra 条件）：格式/分辨率/大小/方向/模式/位深/标记
        # 与 --list-images 共用 build_image_attrs/eval_filter_atoms 同一引擎
        dropped_filter = 0
        if drop_expr and any(a[0] != "extra" for grp in drop_expr for a in grp):
            dropped_filter_names = []
            kept = []
            # 封面路径集合（OPF guide 优先，文件名关键词兜底），供 cover 原子过滤
            cover_paths = set()
            if opf_path:
                gc = get_opf_guide_cover_href(opf_path)
                if gc:
                    clean = gc.split("#", 1)[0]
                    cand = (opf_path.parent / clean).resolve()
                    if not cand.is_file():
                        cand = (base_dir / clean).resolve()
                    cover_paths.add(norm_path(cand))
            for img in images:
                if any(k in img.name.lower() for k in COVER_KEYWORDS):
                    cover_paths.add(norm_path(img))
            # 先构建全量 attrs 并回填 small/overscale 标记（与 --list-images 侧一致），
            # 使 --drop-extra 的 small/超大页/疑似旋转跨页/异常 等标记条件在转换链路同样生效
            attrs_list = []
            for img in images:
                attrs = build_image_attrs(img, double_page)
                if norm_path(img) in cover_paths:
                    attrs["cover"] = True
                attrs_list.append(attrs)
            _fill_small_mark(attrs_list, drop_small)
            _fill_overscale_mark(attrs_list)
            for img, attrs in zip(images, attrs_list):
                # drop 表达式为二维组列表（组间 OR、组内 AND），需逐组求值
                if any(eval_filter_atoms(attrs, g) for g in drop_expr):
                    dropped_filter += 1
                    dropped_filter_names.append(img.name)
                else:
                    kept.append(img)
            images = kept
            if dropped_filter_names:
                names_suffix = ": " + ", ".join(dropped_filter_names) if not _short_summary else ""
                emit(t("convert.drop_filter", count=dropped_filter, names=names_suffix))

        # 封面来源判定（json/inspect 来源标注用）：OPF guide > 文件名关键字 > spine > first
        cover_source = None
        if images:
            first = images[0]
            guide_cover = None
            if opf_path:
                guide_cover = get_opf_guide_cover_href(opf_path)
            if guide_cover:
                try:
                    clean = guide_cover.split("#", 1)[0]
                    # href 相对 OPF 所在目录（epub 的 OPF 常在 OEBPS/ 子目录）
                    cand = (opf_path.parent / clean).resolve()
                    if not cand.is_file():
                        cand = (base_dir / clean).resolve()
                    if norm_path(cand) == norm_path(first):
                        cover_source = "OPF guide"
                except Exception:
                    pass
            if cover_source is None and any(k in first.name.lower() for k in COVER_KEYWORDS):
                cover_source = "filename"
            if cover_source is None:
                cover_source = "spine" if opf_path else "first"

        # arcname 预计算：重名图加序号前缀（与打包一致），ComicInfo Page Image 与打包共用
        arcnames, _ = _compute_arcnames(images)

        # Step 3.6: 生成 ComicInfo.xml（默认启用，--no-comicinfo 关闭）
        comicinfo_xml = None
        conv_sources = None
        if comicinfo:
            build_err = None
            try:
                opf_meta = read_opf_metadata(opf_path) if opf_path else {}
                exth_meta = read_exth_metadata(ebook_path)
                meta = collect_comicinfo_meta(opf_meta, exth_meta, ebook_path)
                inferred = infer_series_number(ebook_path)
                setinfo = parse_setinfo_args(setinfo_args, meta, inferred, ebook_path)
                built = build_comicinfo(meta, images, inferred, setinfo, cover_source=cover_source, double_page=double_page, arcnames=arcnames)
                if built is not None:
                    comicinfo_xml, conv_sources = built
                else:
                    comicinfo_xml = None
            except Exception as e:
                comicinfo_xml = None
                build_err = e  # 保留具体异常，供生成失败分级文案展示
            if comicinfo_xml is None:
                emit(t("comicinfo.build_fail", err=build_err if build_err is not None else "build"), level="error")
                # 不删除已有目标：元数据生成失败不应毁掉磁盘上原有的有效 CBZ
                return None, ConvStatus.FAIL, "comicinfo", None
            emit(t("comicinfo.generating"))

        # Step 4: 打包为 cbz（默认 ZIP 无压缩，图片本身已压缩；--compress 1-9 启用 deflate）
        # v2.2.1 原子替换：先写 cbz.tmp，全部成功后 os.replace，避免中途崩溃残留残缺 CBZ
        tmp_cbz = cbz_path.with_name(cbz_path.name + ".tmp")
        seen_paths = set()  # 归一化路径集合：判物理重复（同一物理文件重复出现则跳过不写入）
        skipped_dup = 0
        comicinfo_failed = None
        if compress > 0:
            zf_obj = zipfile.ZipFile(str(tmp_cbz), "w", zipfile.ZIP_DEFLATED, compresslevel=compress)
        else:
            zf_obj = zipfile.ZipFile(str(tmp_cbz), "w", zipfile.ZIP_STORED)
        with zf_obj as zf:
            for idx, img in enumerate(images, 1):
                norm = norm_path(img)
                if norm in seen_paths:
                    # 物理重复：同一物理文件（含大小写差异等归一化后相同）再次出现，跳过不写入
                    skipped_dup += 1
                    continue
                seen_paths.add(norm)
                # arcname 由 _compute_arcnames 预计算（重名加序号前缀），与 ComicInfo Page Image 共用
                arcname = arcnames[img]
                zf.write(str(img), arcname)
            # Step 4b: 写入 ComicInfo.xml（并入同一次 zip 写入，避免二次打开）
            if comicinfo_xml is not None:
                try:
                    zf.writestr("ComicInfo.xml", comicinfo_xml.encode("utf-8"))
                    emit(t("comicinfo.created"))
                except Exception as e:
                    comicinfo_failed = e
        if skipped_dup:
            emit(t("convert.dedup_physical", count=skipped_dup))
        if comicinfo_failed is not None:
            tmp_cbz.unlink(missing_ok=True)
            emit(t("comicinfo.write_fail", err=comicinfo_failed), level="error")
            return None, ConvStatus.FAIL, "comicinfo", None

        # 完整性校验：先对 tmp 校验，通过后才 os.replace 覆盖目标。
        # 校验失败只删 tmp，旧 CBZ 原样保留（修复"先覆盖后校验、校验失败删旧包"导致新旧全丢）
        ok, msg = validate_cbz(tmp_cbz, require_comicinfo=(comicinfo_xml is not None))
        if not ok:
            tmp_cbz.unlink(missing_ok=True)
            emit(t("convert.verify_fail", name=cbz_path.name, msg=msg), level="error")
            return None, ConvStatus.FAIL, "verify", None
        emit(t("convert.verify_ok", msg=msg))

        # 原子替换：校验通过后才覆盖目标 cbz
        os.replace(str(tmp_cbz), str(cbz_path))
        size_mb = cbz_path.stat().st_size / (1024 * 1024)
        emit(t("convert.done", name=cbz_path.name, count=len(images), size=f"{size_mb:.1f}"))

        # Step 5: 可选删除原始 mobi
        if delete_original:
            ebook_path.unlink()
            emit(t("convert.deleted_original", name=ebook_path.name))

        # 来源字典补丢弃小图计数（即使 --no-comicinfo 也带回，供 --json / 汇总统计）
        conv_sources = dict(conv_sources or {})
        conv_sources["dropped_small"] = dropped_small
        conv_sources["dropped_filter"] = dropped_filter
        if rename_info:
            conv_sources["renamed"] = rename_info

        return cbz_path, ConvStatus.OK, None, conv_sources
    except Exception as e:
        # 转换失败仅清理半成品 tmp，目标 cbz 保持原子性（旧文件不受影响）
        if tmp_cbz is not None and tmp_cbz.exists():
            tmp_cbz.unlink(missing_ok=True)
        emit(t("convert.error", name=ebook_path.name, err=e), level="error")
        err = str(e).lower()
        if any(k in err for k in ("drm", "encrypt", "decrypt", "protected", "kfx")):
            emit(t("convert.error_drm_hint"), level="error")
            return None, ConvStatus.FAIL, "drm", None
        if any(k in err for k in ("corrupt", "bad", "invalid", "truncat", "eof", "zipfile", "not a zip")):
            return None, ConvStatus.FAIL, "corrupt", None
        return None, ConvStatus.FAIL, "other", None
    finally:
        # 无论正常/异常，强制删除 mobi 解压出来的临时目录，解决 Ctrl+C 残留
        for p in extract_temp_paths:
            if p.exists():
                try:
                    shutil.rmtree(p)
                except Exception as e:
                    emit(t("warn.cleanup_tmp_fail", path=p, err=e), level="warning")
        # KeyboardInterrupt（Ctrl+C）不被 except Exception 捕获，此处兜底清理半成品 tmp_cbz
        if tmp_cbz is not None and tmp_cbz.exists():
            tmp_cbz.unlink(missing_ok=True)


def _safe_zip_extract(zf: zipfile.ZipFile, out_dir: Path) -> None:
    """将 zip 内条目安全解压到 out_dir（含 zip-slip 路径穿越防护）。

    cbz / epub 共用；拒绝绝对路径与 .. 跳转条目，目录条目仅建目录。"""
    for member in zf.infolist():
        name = member.filename
        # 路径穿越防护：拒绝绝对路径、驱动器相对路径（如 C:foo）与 .. 跳转
        # Path('C:foo').is_absolute() 为 False 但 .drive 非空，拼接时 drive 会
        # 替换左侧逃逸 out_dir，故需显式检查 .drive
        norm_name = name.replace("\\", "/")
        if (norm_name.startswith("/") or Path(norm_name).is_absolute()
                or Path(norm_name).drive
                or ".." in norm_name.split("/")):
            src_name = Path(zf.filename).name if zf.filename else (getattr(zf.fp, "name", None) or "<memory>")
            emit(t("unpack.path_skip", name=src_name, entry=name), level="warning")
            continue
        if member.is_dir() or norm_name.endswith("/"):
            (out_dir / norm_name).mkdir(parents=True, exist_ok=True)
            continue
        target = out_dir / norm_name
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(member) as src, open(target, "wb") as dst:
            shutil.copyfileobj(src, dst)


def extract_epub_to_temp(epub_path: Path) -> Path:
    """将 EPUB（zip 容器）安全解包到临时目录，返回临时目录路径。

    与 mobi.extract 的临时目录同等待遇，由调用方在 finally 中清理。
    损坏 zip 由 zipfile.BadZipFile 抛出（走转换失败分类 corrupt）。
    解包中途异常时自行清理本次 mkdtemp 的临时目录再上抛，避免目录泄漏。"""
    tempdir = Path(tempfile.mkdtemp(prefix="manga_mobi2cbz_epub_"))
    try:
        with zipfile.ZipFile(str(epub_path)) as zf:
            _safe_zip_extract(zf, tempdir)
    except Exception:
        shutil.rmtree(tempdir, ignore_errors=True)
        raise
    return tempdir


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
            head = f.read(HEAD_READ_BYTES)
        idx = head.find(b"EXTH")
        if idx < 0 or idx > EXTH_MAX_OFFSET:
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
            type_id = struct.unpack(">I", head[pos:pos + 4])[0]
            l = struct.unpack(">I", head[pos + 4:pos + 8])[0]
            if l < 8 or pos + l > len(head):
                break
            val = head[pos + 8:pos + l].decode("utf-8", errors="replace").strip("\x00")
            key = key_map.get(type_id)
            if key and val and key not in meta:
                meta[key] = val
            pos += l
        return meta
    except Exception:
        return {}


# 输入：OPF 文件路径；输出：dc:metadata 字段字典（title/creator/publisher/date/language/description）
def _clean_volume_number(raw: str) -> str | None:
    """从卷数字符串中剥离卷标记，提取纯数字（可含小数）。

    '卷12'->'12'、'Vol. 12'->'12'、'12巻'->'12'、'第5册'->'5'、'7.5'->'7.5'；
    无法提取返回 None。
    """
    if not raw:
        return None
    m = re.search(r"\d+(?:\.\d+)?", raw)
    return m.group(0) if m else None


def read_opf_metadata(opf_path: Path) -> dict:
    """读取 OPF 的 dc:metadata 元数据（title/creator/publisher/date/language/description/series/number）。

    Series 来源优先级：dc:series → EPUB3 meta[property=belongs-to-collection]
    → meta[name=calibre:series]；Number 来源优先级：dc:number → EPUB3
    group-position → meta[name=calibre:series_index]。dc:number 等原始值
    （如 "卷12"/"Vol. 12"/"12巻"）会剥离卷标记提取纯数字。
    仅返回实际存在的字段，供 ComicInfo.xml 字段映射使用。
    """
    try:
        tree = safe_et_parse(opf_path)
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

        # --- Series / Number：EPUB3 标准 + 常见厂商扩展 ---
        el = root.find(".//dc:series", ns)
        if el is not None and el.text and el.text.strip():
            out["series"] = el.text.strip()
        el = root.find(".//dc:number", ns)
        if el is not None and el.text and el.text.strip():
            num = _clean_volume_number(el.text)
            if num is not None:
                out["number"] = num

        # 遍历 meta：belongs-to-collection / group-position / calibre 系列
        series_fallback = None
        number_fallback = None
        for m in root.iter():
            tag = m.tag.rsplit("}", 1)[-1]
            if tag != "meta":
                continue
            prop = m.get("property")
            name = m.get("name")
            text = (m.text or "").strip()
            content = (m.get("content") or "").strip() or text
            if prop == "belongs-to-collection" and series_fallback is None and content:
                series_fallback = content
            elif prop == "group-position" and number_fallback is None and content:
                num = _clean_volume_number(content)
                if num is not None:
                    number_fallback = num
            elif name and name.lower() in ("calibre:series", "series") and series_fallback is None and content:
                series_fallback = content
            elif name and name.lower() in ("calibre:series_index", "series_index") and number_fallback is None and content:
                num = _clean_volume_number(content)
                if num is not None:
                    number_fallback = num

        if "series" not in out and series_fallback:
            out["series"] = series_fallback
        if "number" not in out and number_fallback:
            out["number"] = number_fallback
        return out
    except Exception:
        return {}


# 输入：日期字符串；输出：严格提取的 4 位年份，无法高置信度判定返回 None
def _extract_year(date_str: str) -> str | None:
    """从日期字符串严格提取年份（宁缺勿错）。

    优先完整日期字段（YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD 等）；
    范围/多值（如 2001-2005、2001/2002）无法高置信度判定时返回 None。
    """
    if not date_str:
        return None
    s = date_str.strip()
    # 完整日期：YYYY-MM-DD 等，取开头 4 位年份
    m = re.match(r"^(19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2}", s)
    if m:
        return m.group(0)[:4]
    # 其余情况：出现多个年份视为范围/多值，宁缺勿错
    years = re.findall(r"(?:19|20)\d{2}", s)
    if len(years) == 1:
        return years[0]
    return None


# 输入：OPF 元数据 + EXTH 元数据 + 源电子书路径；输出：ComicInfo 字段字典（仅含可靠来源的键）
def collect_comicinfo_meta(opf_meta: dict, exth_meta: dict, ebook_path: Path) -> dict:
    """按优先级聚合 ComicInfo 字段：Title/Writer/Publisher/Year/Language/Summary。

    Title=OPF title→EXTH title→文件名 stem；Writer=OPF creator→EXTH author；
    Publisher=OPF publisher→EXTH publisher；Year=PublicationDate 年份；
    LanguageISO=电子书自身语言（不按文件名猜）；Summary=OPF description；
    Date=原始日期字符串原样保留（供 %date 占位符，ComicInfo 无对应字段）。
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
        # %date 占位符用：保留原始日期字符串（如 "2024-01-15"）原样
        meta["date"] = date_str.strip()
        year = _extract_year(date_str)
        if year:
            meta["year"] = year
    lang_src = opf_meta.get("language") or exth_meta.get("language")
    if lang_src:
        norm = normalize_language(lang_src)
        if norm:
            meta["language"] = norm
    if opf_meta.get("description"):
        meta["summary"] = opf_meta["description"]
    # Series/Number：优先 OPF 元数据（用户显式指定优先于两者，见 build_comicinfo）
    if opf_meta.get("series"):
        meta["series"] = opf_meta["series"]
    if opf_meta.get("number"):
        meta["number"] = opf_meta["number"]
    return meta


# ISO 639-1 全量 184 个两位代码白名单（LanguageISO 只接受白名单内代码）
_ISO639_1 = {
    "aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az",
    "ba", "be", "bg", "bh", "bi", "bm", "bn", "bo", "br", "bs",
    "ca", "ce", "ch", "co", "cr", "cs", "cu", "cv", "cy",
    "da", "de", "dv", "dz",
    "ee", "el", "en", "eo", "es", "et", "eu",
    "fa", "ff", "fi", "fj", "fo", "fr", "fy",
    "ga", "gd", "gl", "gn", "gu", "gv",
    "ha", "he", "hi", "ho", "hr", "ht", "hu", "hy", "hz",
    "ia", "id", "ie", "ig", "ii", "ik", "io", "is", "it", "iu",
    "ja", "jv",
    "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn", "ko", "kr", "ks", "ku", "kv", "kw", "ky",
    "la", "lb", "lg", "li", "ln", "lo", "lt", "lu", "lv",
    "mg", "mh", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my",
    "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr", "nv", "ny",
    "oc", "oj", "om", "or", "os",
    "pa", "pi", "pl", "ps", "pt",
    "qu",
    "rm", "rn", "ro", "ru", "rw",
    "sa", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su", "sv", "sw",
    "ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw", "ty",
    "ug", "uk", "ur", "uz",
    "ve", "vi", "vo",
    "wa", "wo",
    "xh",
    "yi", "yo",
    "za", "zh", "zu",
}

# 常见非标准写法别名（jp/cn/tw、3 位全称、无分隔符区域写法等）
_LANG_ALIASES = {
    "jp": "ja", "cn": "zh", "tw": "zh",
    "jpn": "ja", "japanese": "ja",
    "chi": "zh", "zho": "zh", "cmn": "zh", "chinese": "zh",
    "eng": "en", "english": "en",
    "zhtw": "zh", "zhcn": "zh", "zhhans": "zh", "zhhant": "zh",
}


# 输入：语言代码字符串；输出：ISO 639-1 两位小写代码，无法识别返回 None
def normalize_language(code: str) -> str | None:
    """把常见语言代码标准化为 ISO 639-1 两位小写。

    支持 2 位（en/ja/zh...，须在白名单内）、3 位（eng/jpn/chi...）、
    带区域后缀（en-US/zh-CN/ja-jp...）及常见别名（jp/cn/zhtw...）等写法；
    非 ISO 639-1 白名单或无法高置信度识别时返回 None（宁缺勿错）。
    """
    if not code:
        return None
    seg = code.strip().split("-")[0].split("_")[0].split(".")[0].lower()
    if not seg or not seg.isalpha():
        return None
    # 1) 2 位：白名单校验，未命中再查别名（jp→ja / cn→zh / tw→zh）
    if len(seg) == 2:
        if seg in _ISO639_1:
            return seg
        return _LANG_ALIASES.get(seg)
    # 2) 别名（3/4 位常见写法：zhtw→zh / zhcn→zh / japanese→ja...）
    if seg in _LANG_ALIASES:
        return _LANG_ALIASES[seg]
    # 3) 3 位 ISO 639-2 → 639-1
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
_VOLUME_MARKERS = {"vol", "volume", "v", "第", "巻", "卷", "册", "冊"}


def _is_volume_marker(series: str) -> bool:
    """判断 series 是否为纯卷标记词或纯数字（无实际系列名，宁缺勿错）。"""
    s = series.strip().lower()
    return s in _VOLUME_MARKERS or s.isdigit()


# 中文数字（零/一/…/十/百/千/万/两）转阿拉伯数字，无法解析返回 None
_CN_DIGITS = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CN_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10000}


def _cn_to_int(s: str) -> int | None:
    """中文数字转阿拉伯数字（一/二/…/十/百/千/万/两），无法解析返回 None。"""
    s = s.strip()
    if not s or not all(c in "一二三四五六七八九十百零两" for c in s):
        return None
    total = section = num = 0
    for c in s:
        if c in _CN_DIGITS:
            num = _CN_DIGITS[c]
        else:
            u = _CN_UNITS[c]
            if u == 10000:
                section = (section + num) * u
                total += section
                section = num = 0
            else:
                if num == 0:
                    num = 1
                section += num * u
                num = 0
    total += section + num
    return total or None


# 卷/章标记词表（小写；长词在前；单字母 v/t/s/c 放末尾，紧贴数字由前缀式处理）
_VOL_WORDS = ("volume", "season", "เล่มที่", "тома", "tome", "том", "시즌", "vol",
              "เล่ม", "第", "권", "巻", "卷", "册", "冊", "季", "장", "v", "t", "s")
# 章标记词（长词在前：chap>chp>ch>c；話数/话数 先于 話/话）
_CH_WORDS = ("chapter", "episode", "話数", "话数", "บทที่", "ตอนที่", "глава",
             "chap", "chp", "ch", "c", "話", "话", "화", "회", "回", "集", "ep")

_CN_NUM = r"[一二三四五六七八九十百零两]+"
_NUM = r"\d{1,4}(?:\.\d+)?"
_RANGE = rf"{_NUM}-{_NUM}"
_VAL = rf"(?:{_RANGE}|{_NUM})"
# 方括号打分：组名/扫描组特征词（含即强烈倾向组名，-3；决策点3 内置固定词表）
_GROUP_NAME_WORDS = ("汉化", "字幕", "scanlation", "工作室", "扫图", "掃圖", "汉化组",
                     "漫画组", "制作组", "修图", "嵌字", "校对", "team", "组", "社")


def _fmt_num(s: str) -> str | None:
    """数值规范化：去前导零；整数 '0001'->'1'，小数 '025.5'->'25.5'。"""
    if not s:
        return None
    if "." in s:
        ip, fp = s.split(".", 1)
        return (str(int(ip)) if ip else "0") + "." + fp
    return str(int(s))


def _parse_value(s: str) -> str | None:
    """解析数值 token：整数/小数/区间(x 倍数)/尾字母 b(半话)；区间取起始值。"""
    s = s.strip().lstrip(".")
    if not s:
        return None
    v = re.sub(r"x\d+$", "", s)
    if not v:
        return None
    if v.endswith("b"):
        v = v[:-1] + ".5"
    m = re.fullmatch(rf"({_NUM})-({_NUM})", v)
    if m:
        return _fmt_num(m.group(1))
    m = re.fullmatch(rf"({_NUM})", v)
    if m:
        return _fmt_num(m.group(1))
    return None


def _parse_naming_token(tok: str) -> tuple[str | None, str | None]:
    """解析单个命名 token -> (kind, value)。kind: 'vol'/'ch'/None(裸数字)；value 可为 None(纯标记)。"""
    if not tok:
        return None, None
    t = tok.strip()
    if not t:
        return None, None
    low = t.lower()
    # 1) 完整词（容忍尾点：vol. / ch. / chp.）
    lw = low.rstrip(".")
    for w in _VOL_WORDS:
        if lw == w:
            return "vol", None
    for w in _CH_WORDS:
        if lw == w:
            return "ch", None
    # 2) 第 + 数字/中文数字 + [卷巻話话章册回集季화회] 尾（第23巻/第1話/第一卷/第3章/第5册/第6回/第8集/第2季/第5화）
    mm = re.fullmatch(rf"第(?P<n>{_CN_NUM}|{_VAL})(?P<tail>[卷巻話话章册冊回集季화회])?", t)
    if mm:
        tail = mm.group("tail") or ""
        g = mm.group("n")
        num = _cn_to_int(g) if all(c in "一二三四五六七八九十百零两" for c in g) else _parse_value(g)
        if num is None:
            return None, None
        if tail in ("話", "话", "章", "回", "集", "화", "회"):
            return "ch", str(num)
        return "vol", str(num)
    # 3) 前缀式复合：标记 + 数值（v01/vol.7.5/t3/S01/권2/巻2/話005/c003/chp02/卷三/v16-17）
    for w in _VOL_WORDS:
        if low.startswith(w):
            rest = t[len(w):]
            if rest and not rest.startswith(("_", "-", " ")):
                v = _parse_value(rest)
                if v is None and all(c in "一二三四五六七八九十百零两" for c in rest):
                    v = str(_cn_to_int(rest))
                if v is not None:
                    return "vol", v
    for w in _CH_WORDS:
        if low.startswith(w):
            rest = t[len(w):]
            if rest and not rest.startswith(("_", "-", " ")):
                v = _parse_value(rest)
                if v is None and all(c in "一二三四五六七八九十百零两" for c in rest):
                    v = str(_cn_to_int(rest))
                if v is not None:
                    return "ch", v
    # 4) 单字母紧贴数字：c003 / v01 / t3 / S01 / s1（含区间）
    mm = re.fullmatch(r"[CcVvTtSs]\d{1,4}(?:\.\d+)?(?:-\d{1,4}(?:\.\d+)?)?", t)
    if mm:
        kind = "ch" if mm.group(0)[0].lower() == "c" else "vol"
        return kind, _parse_value(mm.group(0)[1:])
    # 5) 后缀式：数值 + 标记（2巻/1권/5話/12卷/3册/24回/6集/2季）
    mm = re.fullmatch(rf"({_NUM})([卷巻권册冊話话화회回集季])", t)
    if mm:
        num, mark = mm.group(1), mm.group(2)
        kind = "ch" if mark in ("話", "话", "화", "회", "回", "集") else "vol"
        return kind, _fmt_num(num)
    # 6) 纯数值（裸数字：整数/小数/区间）
    v = _parse_value(t)
    if v is not None:
        return None, v
    return None, None


def _score_bracket(inner: str) -> int | None:
    """方括号内容打分（供系列名候选选取，决策点3 词表+规则）。

    含卷/章标记的方括号（如 [第2卷]/[vol.3]/[c4]）直接排除返回 None；
    其余按规则计分：含 CJK +2、含组名特征词 -3、纯 ASCII -1、长度异常 -1。
    最高分 > 0 才采用（决策点2）。"""
    inner = inner.strip()
    if not inner:
        return -1
    for tok in re.split(r"[\s_]+", inner):
        if _parse_naming_token(tok)[0] in ("vol", "ch"):
            return None
    has_cjk = bool(re.search(r"[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]", inner))
    score = 2 if has_cjk else 0
    low = inner.lower()
    if any(w in low for w in _GROUP_NAME_WORDS):
        score -= 3
    elif not has_cjk and re.fullmatch(r"[\w\s\.,\-_:\+&'!?()%#~]{1,}", inner, re.ASCII):
        score -= 1
    if len(inner) < 2 or len(inner) > 30:
        score -= 1
    return score


# 输入：电子书文件路径；输出：(series, number, volume) 高置信度推断结果，无法判断返回 (None, None, None)
def infer_series_number(path: Path) -> tuple[str | None, str | None, str | None]:
    """从文件名高置信度推断漫画 Series/Number（Kavita 语义对齐）。

    卷标记：v/vol/volume/Vol 7.5/tome/t/T3/S01/Season/卷N/第N卷/中文数字卷/
    N巻/第N巻/册N/第N册/권N/1권/시즌N/第N季/季N/เล่ม N/เล่มที่ N/Том N/Тома N/卷区间 v16-17。
    章标记：c1/ch1/ch.1/chap/chp/Chapter/Episode/話N/话N/第N話/話数N/第N回/回N/第N集/集N/
    話N-M 区间/小数 025.5/尾字母 b；含多语言（화/회/回/集/บทที่/ตอนที่/Глава）。
    裸数字结尾（如 "Sample Series 108"）视为高置信度章/卷；4 位年份（19xx/20xx）
    与纯数字文件名会被排除，宁缺勿错。括号/方括号注释、卷/章标记之后的
    其余内容（扫描组名等）不参与推断。
    返回三元组 (series, number, volume)（卷/章拆分 v3.0.0）：
    - 仅卷无章：Number=卷号、Volume=None；
    - 仅章无卷：Number=章号、Volume=None；
    - 卷+章并存：Number=章号、Volume=卷号；
    - 无系列名的纯标记（如 "Vol.01"/"第 01 卷"）返回 (None, 卷号, None)。
    """
    name = path.name
    if not name:
        return None, None, None
    # 用 name 而非 stem：Path.stem 会把 "Vol.01" 的 ".01" 当扩展名吞掉
    stem = name
    for ext in SUPPORTED_INPUT_EXTENSIONS | {".cbz", ".cbr", ".cb7", ".cbt",
                                             ".7z", ".zip", ".rar", ".pdf",
                                             ".png", ".jpg", ".jpeg"}:
        if name.lower().endswith(ext):
            stem = name[:-len(ext)]
            break
    s = stem.strip()
    # --- 系列名优先提取：书名号《》 > 方括号打分（决策点1/4/5）---
    pre_series = None
    # 1) 书名号：全局识别取第一个，去《》符号、保留内部原文（决策点1 A）
    m = re.search(r"《([^》]*)》", s)
    if m:
        pre_series = m.group(1).strip()
    # 2) 方括号：仅当无书名号时逐个切分打分，选最高分(>0)者为系列名（决策点2 A/4 A/5 A）
    if pre_series is None:
        best_b, best_sc = None, 0
        for b in re.findall(r"\[[^\]]*\]", s):
            sc = _score_bracket(b[1:-1])
            if sc is not None and sc > best_sc:
                best_sc, best_b = sc, b[1:-1]
        if best_sc > 0 and best_b is not None:
            pre_series = best_b.strip()
    # 3) 剥除书名号与所有方括号（命中的方括号内容已定为 series，一并剥除避免重复）
    s = re.sub(r"《[^》]*》", "", s)
    s = re.sub(r"\[[^\]]*\]", "", s)
    # 圆括号：内含卷/章标记的保留内层为锚点，纯注释剥除
    segs = []
    for seg in re.split(r"(\([^)]*\))", s):
        if seg.startswith("(") and seg.endswith(")") and len(seg) > 2:
            inner = seg[1:-1].strip()
            toks_in = [t for t in re.split(r"[\s_]+", inner) if t]
            if any(_parse_naming_token(t)[0] for t in toks_in):
                segs.append(inner)
        else:
            segs.append(seg)
    s = " ".join(x for x in segs if x).strip()
    toks = [t for t in re.split(r"[\s_]+", s) if t]
    n = len(toks)
    parsed = [_parse_naming_token(t) for t in toks]
    kind_of = [p[0] for p in parsed]
    val_of = [p[1] for p in parsed]
    used = set()
    vol = ch = bare = None
    seen_marker = False
    i = 0
    while i < n:
        k, v = kind_of[i], val_of[i]
        if k in ("vol", "ch") and v is None:
            used.add(i)
            seen_marker = True
            if i + 1 < n and kind_of[i + 1] is None and val_of[i + 1] is not None:
                num = val_of[i + 1]
                used.add(i + 1)
                i += 2
            else:
                num = None
                i += 1
            if num is not None:
                if k == "vol" and vol is None:
                    vol = num
                elif k == "ch" and ch is None:
                    ch = num
            continue
        if k in ("vol", "ch") and v is not None:
            used.add(i)
            seen_marker = True
            if k == "vol" and vol is None:
                vol = v
            elif k == "ch" and ch is None:
                ch = v
            i += 1
            continue
        if k is None and v is not None:
            if seen_marker and ch is None:
                ch = v
            bare = v
            used.add(i)
            i += 1
            continue
        if seen_marker:
            used.add(i)
        i += 1
    kept = []
    for i, t in enumerate(toks):
        if i not in used:
            kept.append(t)
    series = " ".join(kept).strip()
    series = re.sub(r"\s+", " ", series).strip(" -_.")
    # 书名号/方括号优先提取的系列名覆盖拼接结果（优先级1/2 > 3）
    if pre_series:
        series = re.sub(r"\s+", " ", pre_series).strip(" -_.")
    # 年份误判防护
    num = ch if ch is not None else (vol if vol is not None else bare)
    # 卷/章拆分：仅"卷+章并存"时 Volume=卷号；其余情况 Volume=None
    vol_out = vol if (ch is not None and vol is not None) else None
    if num is not None and re.fullmatch(r"\d{4}", num):
        y = int(num)
        if 1900 <= y <= 2100:
            if ch is not None and ch != num:
                num = ch
            elif vol is not None and vol != num:
                num = vol
                vol_out = None
            else:
                return (series if series else None), None, None
    if num is None:
        return (series if series else None), None, None
    if not series:
        return None, num, vol_out
    return series, num, vol_out


# 输入：聚合后的元数据字典 + 最终图片列表 + (series, number, volume) 推断结果；输出：ComicInfo.xml 文本或 None
def _resolve_setinfo_value(raw: str, series, number, volume, title, stem,
                           writer=None, publisher=None, date=None,
                           language=None, description=None) -> str | None:
    """解析 --setinfo 值中的占位符：%series/%number/%volume/%title/%writer/%publisher/
    %date/%language/%description/%filename/%leftN/%rightN/%subN_M。

    两种语义：
    - 整段恰好是单个已知占位符：对应值缺失时返回 None（该字段不写入），保持原语义；
    - 占位符与固定文本混用（如 '%writer·重制'、'第%number话'）：与 --rename 一致做全局替换，
      缺失值渲染为空串，未知占位符原样保留。"""
    if not raw:
        return raw
    if raw.startswith("%"):
        token = raw[1:]
        if token == "series":
            return series
        if token == "number":
            return number
        if token == "volume":
            return volume
        if token == "title":
            return title
        if token == "writer":
            return writer
        if token == "publisher":
            return publisher
        if token == "date":
            return date
        if token == "language":
            return language
        if token == "description":
            return description
        if token == "filename":
            return stem
        m = re.match(r"^(left|right)(\d+)$", token)
        if m:
            side, n = m.group(1), int(m.group(2))
            if side == "left":
                return stem[:n]
            return stem[-n:] if n > 0 else ""
        m = re.match(r"^sub(\d+)_(\d+)$", token)
        if m:
            start, length = int(m.group(1)), int(m.group(2))
            # 1-based：第 start 个字符起取 length 个；越界/非法时该字段不写入
            if start < 1 or length < 1 or start > len(stem):
                return None
            return stem[start - 1:start - 1 + length]
    # 固定文本，或占位符与固定文本混用（如 '%writer·重制'、'第%number话'）：
    # 与 --rename 一致做全局替换（缺值渲染空串、未知占位符原样保留）
    return _render_name_template(raw, series, number, volume, title, stem,
                                 writer=writer, publisher=publisher, date=date,
                                 language=language, description=description)


# ---- --rename 文件重命名支持（默认关闭，--rename 开启） ----
def _norm_num(s: str) -> str:
    """数字字符串规范化：去前导零，整数去小数尾（'005'->'5'、'7.0'->'7'、'5.5'->'5.5'）。"""
    if not s:
        return s
    try:
        f = float(s)
        return str(int(f)) if f.is_integer() else str(f)
    except ValueError:
        return s


def _detect_episode_range(stem: str) -> tuple[str, str] | None:
    """检测连话区间（話005-006 / ch5-6 / 第5-6話 / ep5~6 等），返回 (起始, 结束) 或 None。

    仅在紧邻章标记（話/话/ch/chap/chapter/ep/episode/第）处出现「数字-数字」才判定，
    避免把普通连字符（如标题中的 A-B）误判为连话。"""
    m = re.search(
        r"(?:話|话|ch|chap|chapter|ep|episode|第)\s*[. ]?\s*(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)",
        stem, re.IGNORECASE,
    )
    if m:
        a, b = _norm_num(m.group(1)), _norm_num(m.group(2))
        if a and b:
            return a, b
    return None


def _render_name_template(raw: str, series, number, volume, title, stem,
                          writer=None, publisher=None, date=None,
                          language=None, description=None) -> str:
    """渲染 --rename 模板占位符：%series/%number/%volume/%title/%writer/%publisher/
    %date/%language/%description/%filename/%leftN/%rightN/%subN_M；
    支持 %0<N>number 补零（如 %03number -> '005'）；缺失值渲染为空串，未知占位符原样保留。"""
    if not raw:
        return raw

    def repl(m):
        token = m.group(1)
        if token == "series":
            return series or ""
        if token == "number":
            return number or ""
        if token == "volume":
            return volume or ""
        if token == "title":
            return title or ""
        if token == "writer":
            return writer or ""
        if token == "publisher":
            return publisher or ""
        if token == "date":
            return date or ""
        if token == "language":
            return language or ""
        if token == "description":
            return description or ""
        if token == "filename":
            return stem or ""
        mm = re.match(r"^(left|right)(\d+)$", token)
        if mm:
            side, n = mm.group(1), int(mm.group(2))
            if side == "left":
                return (stem or "")[:n]
            return (stem or "")[-n:] if n > 0 else ""
        mm = re.match(r"^sub(\d+)_(\d+)$", token)
        if mm:
            start, length = int(mm.group(1)), int(mm.group(2))
            if start < 1 or length < 1:
                return ""
            return (stem or "")[start - 1:start - 1 + length]
        mm = re.match(r"^0(\d+)number$", token)
        if mm:
            if not number:
                return ""
            try:
                return str(int(float(number))).zfill(int(mm.group(1)))
            except ValueError:
                return number
        return m.group(0)  # 未知占位符原样保留

    # P1 修复：token 字符类排除下划线，且 subN_M / 0<N>number 特殊占位符在交替中优先匹配，
    #           避免 %series_%03number 中 %series_ 被贪婪吞并（原正则含下划线致粘连）
    return re.sub(r"%((?:sub\d+_\d+)|(?:0\d+number)|[A-Za-z0-9]+)", repl, raw)


def _read_rename_meta(ebook_path: Path) -> dict:
    """从 zip 类源（.cbz/.epub/.zip）内部读取 OPF / ComicInfo.xml 元数据，供 --rename 兜底。

    mobi 等无法不解包读取的格式返回 {}（仅靠文件名推断）。OPF 经 safe_et_parse
    安全解析（XXE 防护），读取 dc:series/dc:number/dc:title/dc:creator/
    dc:publisher/dc:date/dc:language/dc:description 兜底；ComicInfo.xml
    直接映射 Series/Number/Volume/Title/Writer/Publisher/LanguageISO/Summary。"""
    if ebook_path.suffix.lower() not in (".cbz", ".epub", ".zip"):
        return {}
    try:
        import zipfile as _zipfile
        with _zipfile.ZipFile(ebook_path) as zf:
            names = set(zf.namelist())
            meta: dict = {}
            opf = next((n for n in names if n.lower().endswith(".opf")), None)
            if opf:
                try:
                    tree = safe_et_parse(zf.read(opf))
                    root = tree.getroot()
                    dc = "http://purl.org/dc/elements/1.1/"
                    el = root.find(f".//{{{dc}}}series")
                    if el is not None and el.text and el.text.strip():
                        meta["series"] = el.text.strip()
                    el = root.find(f".//{{{dc}}}number")
                    if el is not None and el.text and el.text.strip():
                        num = _clean_volume_number(el.text)
                        if num is not None:
                            meta["number"] = num
                    el = root.find(f".//{{{dc}}}title")
                    if el is not None and el.text and el.text.strip():
                        meta["title"] = el.text.strip()
                    el = root.find(f".//{{{dc}}}creator")
                    if el is not None and el.text and el.text.strip():
                        meta["writer"] = el.text.strip()
                    el = root.find(f".//{{{dc}}}publisher")
                    if el is not None and el.text and el.text.strip():
                        meta["publisher"] = el.text.strip()
                    el = root.find(f".//{{{dc}}}date")
                    if el is not None and el.text and el.text.strip():
                        meta["date"] = el.text.strip()
                    el = root.find(f".//{{{dc}}}language")
                    if el is not None and el.text and el.text.strip():
                        lang = normalize_language(el.text)
                        meta["language"] = lang or el.text.strip()
                    el = root.find(f".//{{{dc}}}description")
                    if el is not None and el.text and el.text.strip():
                        meta["description"] = el.text.strip()
                    for node in root.iter():
                        tag = node.tag.rsplit("}", 1)[-1]
                        if tag != "meta":
                            continue
                        prop, name = node.get("property"), node.get("name")
                        content = (node.get("content") or "").strip() or (node.text or "").strip()
                        if prop == "belongs-to-collection" and "series" not in meta and content:
                            meta["series"] = content
                        elif prop == "group-position" and "number" not in meta and content:
                            num = _clean_volume_number(content)
                            if num is not None:
                                meta["number"] = num
                        elif name and name.lower() in ("calibre:series", "series") and "series" not in meta and content:
                            meta["series"] = content
                        elif name and name.lower() in ("calibre:series_index", "series_index") and "number" not in meta and content:
                            num = _clean_volume_number(content)
                            if num is not None:
                                meta["number"] = num
                except Exception:
                    pass
            cinfo = next((n for n in names if n.lower().endswith("comicinfo.xml")), None)
            if cinfo:
                try:
                    tree = safe_et_parse(zf.read(cinfo))
                    root = tree.getroot()
                    for tag in ("Series", "Number", "Volume", "Title",
                                "Writer", "Publisher", "LanguageISO", "Summary"):
                        el = root.find(tag)
                        if el is not None and el.text and el.text.strip():
                            if tag == "Series":
                                meta.setdefault("series", el.text.strip())
                            elif tag == "Number":
                                meta.setdefault("number", _norm_num(el.text.strip()))
                            elif tag == "Volume":
                                meta.setdefault("volume", _norm_num(el.text.strip()))
                            elif tag == "Title":
                                meta.setdefault("title", el.text.strip())
                            elif tag == "Writer":
                                meta.setdefault("writer", el.text.strip())
                            elif tag == "Publisher":
                                meta.setdefault("publisher", el.text.strip())
                            elif tag == "LanguageISO":
                                meta.setdefault("language", el.text.strip())
                            elif tag == "Summary":
                                meta.setdefault("description", el.text.strip())
                except Exception:
                    pass
            return meta
    except Exception:
        return {}


def _build_rename_basename(ebook_path: Path, template: str) -> tuple[str, dict]:
    """计算 --rename 重命名后的文件名主干（不含扩展名）。

    来源优先级：文件名推断 > 文件自带元数据(OPF/ComicInfo.xml) 兜底；setinfo 解耦不参与。
    连话区间（話005-006）识别为 [Ch.5-6]，ComicInfo Number 仍进起始值（排序稳定），
    仅文件名标记体现区间。返回 (new_stem, info)，info 供 dry-run 预览与 --json。"""
    stem = ebook_path.stem
    series, number, volume = infer_series_number(ebook_path)
    ep_range = _detect_episode_range(stem)
    used_meta = False
    meta = _read_rename_meta(ebook_path)
    # 逐字段来源标注：文件名推断优先，文件自带元数据仅在推断缺失时兜底（setinfo 解耦不参与）
    src_series = "filename" if series else None
    src_number = "filename" if number else None
    src_volume = "filename" if volume else None
    if meta:
        if not series and meta.get("series"):
            series, used_meta = meta["series"], True
            src_series = "metadata"
        if not number and meta.get("number"):
            number, used_meta = meta["number"], True
            src_number = "metadata"
        if not volume and meta.get("volume"):
            volume, used_meta = meta["volume"], True
            src_volume = "metadata"
    title = meta.get("title") if meta else None
    # 扩展占位符：writer/publisher/date/language/description 均从聚合元数据兜底
    writer = meta.get("writer") if meta else None
    publisher = meta.get("publisher") if meta else None
    date = meta.get("date") if meta else None
    language = meta.get("language") if meta else None
    description = meta.get("description") if meta else None
    # 标记类型：按原始文件名中的卷/章标记词判定（中文卷『第7巻』/英文『Vol.7』；章『話005』/『Ch.5』）
    # 章标记要求后跟数字或为独立词（避免误中 Bleach 等单词内 ch）；v+数字视为卷区间（v16-17）
    has_ch_token = bool(re.search(r"(?:話|话)", stem)) or bool(
        re.search(r"(?:\bch(?:ap(?:ter)?)?|episode|ep)\s*[. ]?\s*\d", stem, re.IGNORECASE))
    has_vol_token = bool(re.search(r"(?:vol|巻|卷|册|book)", stem, re.IGNORECASE)) or bool(
        re.search(r"(?<![a-z])v\s*[. ]?\s*\d", stem, re.IGNORECASE))
    if volume and number:
        ch = f"{ep_range[0]}-{ep_range[1]}" if ep_range else _norm_num(number)
        mark = f"[Vol.{_norm_num(volume)}][Ch.{ch}]"
        mtype = "vol_ch"
    elif volume:
        mark = f"[Vol.{_norm_num(volume)}]"
        mtype = "vol"
    elif has_vol_token:
        mark = f"[Vol.{_norm_num(number)}]" if number else ""
        mtype = "vol"
    elif has_ch_token:
        ch = f"{ep_range[0]}-{ep_range[1]}" if ep_range else (_norm_num(number) if number else "")
        mark = f"[Ch.{ch}]" if ch else ""
        mtype = "ch"
    elif number:
        mark = f"[x.{_norm_num(number)}]"
        mtype = "x"
    else:
        mark = ""
        mtype = "none"
    if template in (None, "default"):
        base = series if series else ""
        new_stem = (f"{base} {mark}".strip() if mark else (base or stem))
    else:
        # 占位符自动兜底：%volume 空且文件名含卷标记→取 number（单卷场景 number 即卷号）；%number 空→取 volume
        ren_volume = volume or (number if has_vol_token else None)
        ren_number = number or (volume if not ren_volume else None)
        rendered = _render_name_template(template, series or "", ren_number, ren_volume,
                                         title, stem, writer, publisher, date,
                                         language, description)
        # P2 修复：自定义模板不再自动追加 [Vol]/[Ch] mark（默认模板仍追加；需要 mark 可在模板中显式用 %volume/%number 拼写）
        new_stem = rendered or stem
    # P1 修复：new_stem 统一消毒（Windows 非法文件名字符 → 下划线），空结果回退原 stem
    if new_stem != stem:
        _cleaned = sanitize_filename_component(new_stem)
        if _cleaned:
            new_stem = _cleaned
    info = {
        "old_stem": stem, "new_stem": new_stem, "series": series,
        "number": number, "volume": volume, "range": ep_range,
        "mark": mark, "type": mtype, "used_meta": bool(used_meta),
        "series_source": src_series, "number_source": src_number, "volume_source": src_volume,
        "template": template,
    }
    return new_stem, info


def _apply_rename_to_target(target: Path, new_stem: str) -> Path:
    """把 target_cbz_path 计算出的目标路径的文件名替换为重命名后的主干（目录结构不变）。"""
    return target.with_name(new_stem + ".cbz")


# ComicInfo.xml v2.0/v2.1 标准简单字段白名单（41 个；Pages 为复杂结构不纳入；
# PageCount 由脚本按实际图片数强制计算，不在白名单避免 --setinfo 覆盖）
COMICINFO_WHITELIST = {
    "Title", "Series", "Number", "Count", "Volume", "AlternateSeries",
    "AlternateNumber", "AlternateCount", "StoryArc", "StoryArcNumber",
    "SeriesGroup", "Genre", "Tags", "Writer", "Penciller", "Inker",
    "Colorist", "Letterer", "CoverArtist", "Editor", "Publisher",
    "Imprint", "Web", "LanguageISO", "Format", "AgeRating",
    "Manga", "Characters", "Teams", "Locations", "ScanInformation",
    "Summary", "Notes", "Year", "Month", "Day", "BlackAndWhite", "GTIN",
    "CommunityRating", "MainCharacterOrTeam", "Review",
}
# 大小写不敏感映射：小写 → 标准名
_COMICINFO_WHITELIST_LOWER = {f.lower(): f for f in COMICINFO_WHITELIST}


def parse_setinfo_args(setinfo_args: list, meta: dict, inferred: tuple, ebook_path: Path) -> dict:
    """解析 --setinfo 参数为 {ComicInfo标签: 值} 字典（可多次，后出现覆盖先出现）。

    智能拆分：仅当逗号后紧跟"字段名="时才拆分，否则逗号视为值的一部分
    （如 Summary=hello, world 不拆分）。VALUE 支持固定值与占位符。"""
    result: dict = {}
    if not setinfo_args:
        return result
    series, number, volume = inferred if isinstance(inferred, tuple) else (None, None, None)
    # CBZ 内显式 ComicInfo 值优先于文件名推断（setinfo 场景 CBZ 是权威）
    series = meta.get("series") or series
    number = meta.get("number") or number
    volume = meta.get("volume") or volume
    stem = ebook_path.stem
    title = meta.get("title") or stem
    # 扩展占位符：writer/publisher/date/language 直接取聚合值；description 用 summary 键
    writer = meta.get("writer")
    publisher = meta.get("publisher")
    date = meta.get("date")
    language = meta.get("language")
    # description 键兼容：_read_rename_meta 存 description，collect_comicinfo_meta 存 summary
    description = meta.get("description") or meta.get("summary")
    for arg in setinfo_args:
        # 智能拆分：逗号后紧跟"字段名="才拆
        parts = []
        cur = ""
        i = 0
        while i < len(arg):
            ch = arg[i]
            if ch == ",":
                rest = arg[i + 1:]
                if re.match(r"^\s*[A-Za-z]+=", rest):
                    parts.append(cur)
                    cur = ""
                    i += 1
                    continue
            cur += ch
            i += 1
        parts.append(cur)
        for part in parts:
            if "=" not in part:
                continue
            field, _, raw = part.partition("=")
            field = field.strip()
            raw = raw.strip()
            if not field:
                continue
            # 白名单校验：大小写不敏感，白名单外字段 warning 忽略
            std = _COMICINFO_WHITELIST_LOWER.get(field.lower())
            if std is None:
                emit(t("setinfo.whitelist_skip", field=field), level="warning")
                continue
            field = std
            value = _resolve_setinfo_value(raw, series, number, volume, title, stem,
                                           writer, publisher, date, language, description)
            if value is None:
                continue
            # Manga 枚举校验（官方 v2.0：Unknown/No/Yes/YesAndRightToLeft），非法值 warning 忽略
            if field == "Manga" and value not in ("Unknown", "No", "Yes", "YesAndRightToLeft"):
                emit(t("setinfo.invalid_manga", value=value), level="warning")
                continue
            result[field] = value
    return result


class _HtmlTextExtractor(HTMLParser):
    """HTMLParser 子类：剥离标签并收集纯文本（Summary 字段用）。

    convert_charrefs=True 时字符实体（&amp;、&#x20; 等）由 HTMLParser 自动解码。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _strip_html(text: str | None) -> str | None:
    """去除 HTML 标签与常见实体，返回纯文本（Summary 字段用）；异常时原样返回"""
    if not text:
        return text
    try:
        parser = _HtmlTextExtractor()
        parser.feed(text)
        parser.close()
        return re.sub(r"\s+", " ", "".join(parser.parts)).strip()
    except Exception:
        return text


def _compute_arcnames(images: list) -> tuple[dict, int]:
    """预计算打包 arcname：同名图加 {idx:04d}_ 前缀，物理重复跳过。

    返回 (img -> arcname 映射, 物理重复跳过数)。逻辑与打包循环保持完全一致，
    供 ComicInfo.xml <Page Image> 与 zip 条目名共用（重名场景一致）。"""
    seen = {}
    seen_paths = set()
    arcnames: dict = {}
    skipped = 0
    for idx, img in enumerate(images, 1):
        norm = norm_path(img)
        if norm in seen_paths:
            skipped += 1
            continue
        seen_paths.add(norm)
        if img.name in seen:
            arcnames[img] = f"{idx:04d}_{img.name}"
        else:
            seen[img.name] = img.name
            arcnames[img] = img.name
    return arcnames, skipped


def build_comicinfo(meta: dict, images: list, inferred: tuple, setinfo: dict | None = None,
                    cover_source: str | None = None, double_page: float | None = None,
                    arcnames: dict | None = None) -> tuple[str, dict] | None:
    """用 xml.etree.ElementTree 生成 ComicInfo.xml（禁止手工拼接字符串）。

    PageCount 必写（=最终写入 CBZ 的实际图片数）；其余字段有可靠来源
    才写入，无来源直接省略，不生成空标签。setinfo 为 --setinfo 解析结果，
    优先级最高（覆盖 meta 与 inferred）。
    double_page 非 None 时为双页检测阈值（图片宽/高 >= 该值判为跨页）：
    生成 <Pages> 逐页 DoublePage 标记；Manga 声明不再自动写入（改由 --setinfo
    Manga= 显式指定，官方 v2.0 枚举 Unknown/No/Yes/YesAndRightToLeft）；
    None 时不生成 <Pages>。
    CoverSource 不再写入 Notes（来源改由 --inspect / --json 展示，避免污染 ComicInfo）。

    返回 (xml 文本, sources)：sources 记录 series/number/volume/cover 来源
    （series_source/number_source: setinfo/opf/inferred；volume_source: setinfo/inferred；
    cover_source: OPF guide/filename/spine/first），
    供 --json 输出；xml 生成失败返回 None。
    """
    try:
        root = ET.Element("ComicInfo")
        setinfo = setinfo or {}
        inferred_s, inferred_n, inferred_v = inferred if isinstance(inferred, tuple) else (None, None, None)
        # 优先级：setinfo（用户指定）> meta（OPF 元数据）> inferred（文件名推测）
        series = setinfo.get("Series") or meta.get("series") or inferred_s
        number = setinfo.get("Number") or meta.get("number") or inferred_n
        # Volume 仅来源：setinfo + 卷章并存推断（OPF 卷不进 Volume，v3.0.0 定稿）
        volume = setinfo.get("Volume") or inferred_v
        series_source = ("setinfo" if setinfo.get("Series")
                         else ("opf" if meta.get("series") else ("inferred" if inferred_s else None)))
        number_source = ("setinfo" if setinfo.get("Number")
                         else ("opf" if meta.get("number") else ("inferred" if inferred_n else None)))
        volume_source = ("setinfo" if setinfo.get("Volume")
                         else ("inferred" if inferred_v else None))
        notes = setinfo.get("Notes")
        ordered = [
            ("Title", setinfo.get("Title", meta.get("title"))),
            ("Series", series),
            ("Number", number),
            # 官方 v2.1 字段补齐：以下字段仅 setinfo 显式指定时写入，
            # 无来源省略不生成空标签（与 Manga 等语义一致，覆盖前 14 字段白名单缺口）
            ("Count", setinfo.get("Count")),
            ("Volume", volume),
            ("AlternateSeries", setinfo.get("AlternateSeries")),
            ("AlternateNumber", setinfo.get("AlternateNumber")),
            ("AlternateCount", setinfo.get("AlternateCount")),
            ("StoryArc", setinfo.get("StoryArc")),
            ("StoryArcNumber", setinfo.get("StoryArcNumber")),
            ("SeriesGroup", setinfo.get("SeriesGroup")),
            ("Genre", setinfo.get("Genre")),
            ("Tags", setinfo.get("Tags")),
            ("Writer", setinfo.get("Writer", meta.get("writer"))),
            ("Penciller", setinfo.get("Penciller")),
            ("Inker", setinfo.get("Inker")),
            ("Colorist", setinfo.get("Colorist")),
            ("Letterer", setinfo.get("Letterer")),
            ("CoverArtist", setinfo.get("CoverArtist")),
            ("Editor", setinfo.get("Editor")),
            ("Imprint", setinfo.get("Imprint")),
            ("Web", setinfo.get("Web")),
            ("Publisher", setinfo.get("Publisher", meta.get("publisher"))),
            ("Year", setinfo.get("Year", meta.get("year"))),
            ("LanguageISO", setinfo.get("LanguageISO", meta.get("language"))),
            ("PageCount", str(len(images))),
            ("Format", setinfo.get("Format")),
            ("AgeRating", setinfo.get("AgeRating")),
            ("Characters", setinfo.get("Characters")),
            ("Teams", setinfo.get("Teams")),
            ("Locations", setinfo.get("Locations")),
            ("ScanInformation", setinfo.get("ScanInformation")),
            ("Summary", _strip_html(setinfo.get("Summary", meta.get("summary")))),
            ("Notes", notes),
            # 官方简单字段：仅 setinfo 显式指定时写入（Manga 默认不写，避免无跨页也声明）
            ("Manga", setinfo.get("Manga")),
            ("BlackAndWhite", setinfo.get("BlackAndWhite")),
            ("Month", setinfo.get("Month")),
            ("Day", setinfo.get("Day")),
            ("GTIN", setinfo.get("GTIN")),
            ("CommunityRating", setinfo.get("CommunityRating")),
            ("MainCharacterOrTeam", setinfo.get("MainCharacterOrTeam")),
            ("Review", setinfo.get("Review")),
        ]
        # 双页检测：#25 开启时生成 <Pages> 逐页 DoublePage 标记（Manga 已改由 --setinfo 指定）
        for tag, val in ordered:
            if val is None:
                continue
            el = ET.SubElement(root, tag)
            el.text = str(val)
        if double_page is not None:
            pages_el = ET.SubElement(root, "Pages")
            for img in images:
                page = ET.SubElement(pages_el, "Page")
                page.set("Image", (arcnames or {}).get(img, img.name))
                dim = image_dimensions(img)
                if dim and dim[0] > 0 and dim[1] > 0 and dim[0] / dim[1] >= double_page:
                    page.set("Type", "DoublePage")
        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        sources = {
            "series_source": series_source,
            "number_source": number_source,
            "volume_source": volume_source,
            "cover_source": cover_source,
        }
        return xml_bytes.decode("utf-8"), sources
    except Exception:
        return None


def get_drm_flag(p: Path) -> bool:
    """判断 mobi/azw 是否 DRM 加密。

    旧实现读 PalmDB 头偏移 12 的 2 字节，该位置落在 PalmDB name 字段
    内（偏移 0-31），文件名/书名含 '-'、'_' 等字符会误报为 DRM。正确判据：
    1. PalmDB attributes（偏移 32）的 copy-protection 位（0x0040）；
    2. PalmDOC header 的 encryption type（偏移 78+8*nrec+0x0E，
       0=无、1=旧格式、2=新格式），为权威判据。
    """
    if p.suffix.lower() == ".epub":
        return False
    try:
        with open(p, "rb") as f:
            head = f.read(78)
            if len(head) < 78:
                return False
            attrs = struct.unpack(">H", head[32:34])[0]
            if attrs & 0x0040:
                return True
            nrec = struct.unpack(">H", head[76:78])[0]
            if nrec == 0:
                return False
            f.seek(78 + 8 * nrec + 14)
            return struct.unpack(">H", f.read(2))[0] != 0
    except Exception:
        return False


def image_dimensions_bytes(head: bytes) -> tuple[int, int] | None:
    """从图片文件头 bytes 读取宽高（不加载整图），支持 png/jpeg/gif/webp/bmp，失败返回 None。

    JPEG 的 SOF 段可能被 APP0/APP1(EXIF) 等大段标记推后到几 KB 处，
    因此需传入足够大的头部（如 64KB）用于扫描，避免只读到前 64 字节而解析失败。"""
    try:
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


def image_dimensions(img: Path) -> tuple[int, int] | None:
    """从图片文件读取宽高（不加载整图），支持 png/jpeg/gif/webp/bmp，失败返回 None。"""
    try:
        with open(img, "rb") as f:
            head = f.read(HEAD_READ_BYTES)
    except Exception:
        return None
    return image_dimensions_bytes(head)


def inspect_res_summary(res_list, t) -> str | None:
    """--inspect 分辨率分布摘要：最频繁分辨率组合 + 异常小图数。

    异常小图判定与 --drop-small 一致：宽和高均 < 对应中位数 × 0.5（恒用 0.5 默认比例做常态统计）。"""
    if not res_list:
        return None
    total = len(res_list)
    main_dim, main_cnt = Counter(res_list).most_common(1)[0]
    med_w = statistics.median(d[0] for d in res_list)
    med_h = statistics.median(d[1] for d in res_list)
    small_n = sum(1 for w, h in res_list if w < med_w * 0.5 and h < med_h * 0.5)
    return t(
        "inspect.res_summary",
        w=main_dim[0], h=main_dim[1],
        count=main_cnt, pct=f"{main_cnt / total * 100:.0f}",
        small=small_n,
    )


def _opf_cover_href_scan(text: str) -> str | None:
    """从 OPF 文本中解析封面引用 href（纯文本正则扫描，兼容属性顺序互换、无命名空间 OPF）。

    命中优先级：
    1. <guide><reference type="cover" href="...">
    2. <manifest><item properties="cover-image" href="...">（EPUB3 约定）
    3. <meta name="cover" content="{id}"> 对应的 manifest item href（EPUB2 约定）
    均未命中返回 None。"""
    # 1) guide reference type=cover
    m = re.search(
        r'<reference\s+[^>]*type=["\']cover["\'][^>]*href=["\']([^"\']+)["\']',
        text, re.I,
    )
    if not m:
        m = re.search(
            r'<reference\s+[^>]*href=["\']([^"\']+)["\'][^>]*type=["\']cover["\']',
            text, re.I,
        )
    if m:
        return m.group(1)
    # 2) manifest item properties 含 cover-image
    m = re.search(
        r'<item\b[^>]*properties=["\'][^"\']*cover-image[^"\']*["\'][^>]*href=["\']([^"\']+)["\']',
        text, re.I,
    )
    if not m:
        m = re.search(
            r'<item\b[^>]*href=["\']([^"\']+)["\'][^>]*properties=["\'][^"\']*cover-image[^"\']*["\']',
            text, re.I,
        )
    if m:
        return m.group(1)
    # 3) meta name=cover content={id} → 查 manifest 对应 item 的 href
    m = re.search(
        r'<meta\b[^>]*name=["\']cover["\'][^>]*content=["\']([^"\']+)["\']',
        text, re.I,
    )
    if not m:
        m = re.search(
            r'<meta\b[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']cover["\']',
            text, re.I,
        )
    if m:
        cover_id = m.group(1)
        for it in re.finditer(
            r'<item\b[^>]*id=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\']',
            text, re.I,
        ):
            if it.group(1) == cover_id:
                return it.group(2)
        for it in re.finditer(
            r'<item\b[^>]*href=["\']([^"\']+)["\'][^>]*id=["\']([^"\']+)["\']',
            text, re.I,
        ):
            if it.group(2) == cover_id:
                return it.group(1)
    return None


def get_opf_guide_cover_href(opf_path: Path) -> str | None:
    """解析 OPF 文件中的封面引用（返回 href 字符串），委托 _opf_cover_href_scan。"""
    try:
        text = opf_path.read_text("utf-8", errors="replace")
    except Exception:
        return None
    return _opf_cover_href_scan(text)


def find_ncx(base_dir: Path) -> Path | None:
    """定位 NCX 目录文件。

    优先级：
    1. OPF manifest 中 media-type 为 application/x-dtbncx+xml 的 item（兼容
       把 NCX 命名为 vol.nav / *.nav 等非 .ncx 扩展名的封装）；
    2. OPF spine 的 toc 属性指向的 id 对应 item；
    3. 兜底按 *.ncx 文件名递归搜索。
    找不到返回 None。"""
    try:
        opf_path = find_opf(base_dir)
        if opf_path is not None:
            tree = safe_et_parse(opf_path)
            root = tree.getroot()
            toc_id = None
            spine = root.find(".//opf:spine", OPF_NS)
            if spine is not None:
                toc_id = spine.get("toc")
            for item in root.findall(".//opf:manifest/opf:item", OPF_NS):
                if "dtbncx" in (item.get("media-type") or "").lower():
                    href = item.get("href")
                    if href:
                        cand = (opf_path.parent / href.split("#", 1)[0]).resolve()
                        if cand.exists():
                            return cand
            if toc_id:
                for item in root.findall(".//opf:manifest/opf:item", OPF_NS):
                    if item.get("id") == toc_id:
                        href = item.get("href")
                        if href:
                            cand = (opf_path.parent / href.split("#", 1)[0]).resolve()
                            if cand.exists():
                                return cand
    except Exception:
        pass
    for f in base_dir.rglob("*.ncx"):
        return f
    return None


def parse_ncx_toc(base_dir: Path) -> tuple[int, list[str]]:
    """解析 toc.ncx 目录条目数并预览前 3 条标题。

    返回 (条目数, 标题预览列表)；找不到 ncx 或解析失败返回 (0, [])。"""
    ncx = find_ncx(base_dir)
    if ncx is None:
        return 0, []
    try:
        text = ncx.read_text("utf-8", errors="replace")
        titles = []
        for m in re.finditer(r"<navLabel>\s*<text>(.*?)</text>", text, re.I | re.S):
            t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if t:
                titles.append(t)
        return len(titles), titles[:3]
    except Exception:
        return 0, []


def parse_nav_toc(base_dir: Path) -> tuple[int, list[str]]:
    """解析 EPUB3 nav 目录条目数并预览前 3 条标题。

    优先从 OPF manifest properties="nav" 定位 nav 文档（EPUB3 官方
    约定），解析 <nav epub:type="toc"> 内 <a> 文本（含多级嵌套展开）；
    找不到时兜底按文件名 *nav*.xhtml 递归搜索。
    返回 (条目数, 标题预览列表)；找不到或解析失败返回 (0, [])。"""
    try:
        opf_path = find_opf(base_dir)
        nav = None
        if opf_path:
            tree = safe_et_parse(opf_path)
            root = tree.getroot()
            for item in root.findall(".//opf:manifest/opf:item", OPF_NS):
                if "nav" in (item.get("properties") or "").split():
                    href = item.get("href")
                    if href:
                        cand = (opf_path.parent / href.split("#", 1)[0]).resolve()
                        if cand.exists():
                            nav = cand
                            break
        if nav is None:
            for f in base_dir.rglob("*.xhtml"):
                if "nav" in f.stem.lower():
                    nav = f
                    break
        if nav is None:
            return 0, []
        text = nav.read_text("utf-8", errors="replace")
        nav_blocks = re.findall(r"<nav\b[^>]*>.*?</nav>", text, re.I | re.S)
        block = None
        for nb in nav_blocks:
            if re.search(r"epub:type\s*=\s*[\"']toc[\"']", nb, re.I):
                block = nb
                break
        if block is None and nav_blocks:
            block = nav_blocks[0]
        if block is None:
            return 0, []
        titles = re.findall(r"<a\b[^>]*>(.*?)</a>", block, re.I | re.S)
        titles = [re.sub(r"<[^>]+>", "", t).strip() for t in titles]
        titles = [t for t in titles if t]
        return len(titles), titles[:3]
    except Exception:
        return 0, []



    # 输入：电子书文件路径、最小字节数过滤与 prefer；输出：状态字符串 ok/invalid/noimg/drm/fail（供汇总计数）
def _inspect_img_summary(fmt_counter: dict) -> dict:
    """inspect 图片级汇总（JSON 输出用）：格式分布。

    与人类可读输出的 fmt_stats 同源同口径，供 --json 在精简行携带，
    避免 JSON 丢失人类可见的格式分布信息。
    """
    return {"formats": dict(fmt_counter) if fmt_counter else None}


def inspect_ebook(p: Path, min_bytes: int, prefer: str = "mobi8", setinfo_args: list | None = None, drop_small: float | None = None, filter_expr: list | None = None, double_ratio: float | None = None) -> tuple:
    """检查单个电子书内部信息（--inspect 模式核心）。

    流程：头部基础检查（魔数/大小/DRM）→ EXTH 元数据 → 解包 →
    目录结构/OPF/spine/NCX/图片数/封面/格式分布/分辨率统计 → 压缩建议。
    DRM 处理：头部标记仅作信息提示，不再跳过解包；解出图片→正常检查并标注可读；
    解包失败/0 图且带标记→判 DRM；无标记+0 图→疑似。
    只解包不打包，结束后自动清理临时目录。

    filter_expr：--inspect [MODE][,FILTER] 的过滤表达式；命中条件的图片输出数量+文件名清单
    （复用过滤引擎与面积口径，small 比例取自表达式本身）。
    drop_small：--drop 表达式中的 small 比例，用于小图预览。

    返回 (状态, 结构化信息 dict)：
    - 状态为 InspectStatus 枚举（OK / INVALID / NOIMG / DRM / FAIL）
    - info 含 source / status / series / number / volume / series_source /
      number_source / volume_source / page_count / drm / spine / toc / filter_hits 等字段
      （spine/toc 为 --json-out 全量字段）
    """
    size = p.stat().st_size
    size_mb = size / (1024 * 1024)
    emit(t("inspect.file_line", name=p.name, size=f"{size_mb:.1f}"), level="info")

    # 结构化输出收集器：--json / --json-out 时写入结果；无则保持默认值
    info: dict = {
        "source": str(p),
        "status": None,
        "series": None,
        "number": None,
        "volume": None,
        "series_source": None,
        "number_source": None,
        "volume_source": None,
        "page_count": None,
        "drm": None,
        "spine": None,
        "toc": None,
        "filter_hits": None,
        "formats": None,
    }

    # CBZ 分支：纯 zipfile 读取，不解压
    if p.suffix.lower() == ".cbz":
        try:
            with zipfile.ZipFile(str(p)) as zf:
                names = zf.namelist()
                img_names = [n for n in names if Path(n).suffix.lower() in IMAGE_EXTENSIONS]
                total_in_dir = len(img_names)
                emit(t("inspect.dir_images", count=total_in_dir))
                if total_in_dir == 0:
                    emit(t("inspect.drm_suspected"))
                    emit(t("inspect.cover_missing"))
                    emit(t("inspect.fmt_none"))
                    emit(t("inspect.drm_bad_hint"), level="info")
                    info["status"] = "noimg"
                    info["page_count"] = 0
                    return InspectStatus.NOIMG, info
                emit(t("inspect.drm_none", count=total_in_dir))

                # 封面检测：文件名扫描
                cover = None
                for n in img_names:
                    if any(k in Path(n).name.lower() for k in COVER_KEYWORDS):
                        cover = n
                        break
                if cover:
                    try:
                        cdata = zf.read(cover)[:HEAD_READ_BYTES]
                    except Exception:
                        cdata = b""
                    dim = image_dimensions_bytes(cdata)
                    dim_str = f"{dim[0]}x{dim[1]}" if dim else "?"
                    size_str = f"{zf.getinfo(cover).file_size / 1024:.0f}KB"
                    emit(t("inspect.cover_found", name=Path(cover).name, src=t("inspect.cover_src_filename"), dim=dim_str, size=size_str))
                else:
                    emit(t("inspect.cover_missing"))

                # 格式分布 + 分辨率统计（zip 内 bytes 读取，不落盘）
                fmt_counter = {}
                res_list = []
                for n in img_names:
                    ext = Path(n).suffix.lower().lstrip(".")
                    if ext == "jpeg":
                        ext = "jpg"
                    fmt_counter[ext] = fmt_counter.get(ext, 0) + 1
                    try:
                        data = zf.read(n)[:HEAD_READ_BYTES]
                    except Exception:
                        data = b""
                    dim = image_dimensions_bytes(data)
                    if dim:
                        res_list.append(dim)

                total_fmt = sum(fmt_counter.values())
                fmt_parts = [
                    f"{k} {v} ({v / total_fmt * 100:.1f}%)"
                    for k, v in sorted(fmt_counter.items(), key=lambda x: -x[1])
                ]
                emit(t("inspect.fmt_stats", total=total_fmt, parts=" | ".join(fmt_parts)))

                if res_list:
                    total_res = len(res_list)
                    w_counter = Counter(d[0] for d in res_list)
                    h_counter = Counter(d[1] for d in res_list)
                    main_w, main_wc = w_counter.most_common(1)[0]
                    main_h, main_hc = h_counter.most_common(1)[0]
                    if main_hc >= main_wc:
                        w_sub = [d[0] for d in res_list if d[1] == main_h]
                        res_parts = [
                            t("inspect.res_main_h", height=main_h, count=main_hc, pct=f"{main_hc / total_res * 100:.0f}"),
                            t("inspect.res_w_range", min=min(w_sub), max=max(w_sub)),
                        ]
                    else:
                        h_sub = [d[1] for d in res_list if d[0] == main_w]
                        res_parts = [
                            t("inspect.res_main_w", width=main_w, count=main_wc, pct=f"{main_wc / total_res * 100:.0f}"),
                            t("inspect.res_h_range", min=min(h_sub), max=max(h_sub)),
                        ]
                    emit(t("inspect.res_line", parts=" | ".join(res_parts)))
                    res_summary = inspect_res_summary(res_list, t)
                    if res_summary:
                        emit(res_summary)

                # 压缩建议
                jpeg_ratio = (fmt_counter.get("jpg", 0) + fmt_counter.get("jpeg", 0)) / total_fmt
                png_ratio = fmt_counter.get("png", 0) / total_fmt
                if png_ratio >= 0.5:
                    emit(t("inspect.adv_png"))
                elif jpeg_ratio >= 0.8:
                    emit(t("inspect.adv_jpeg"))
                else:
                    emit(t("inspect.adv_mixed"))
                info.update(_inspect_img_summary(fmt_counter))

                # --inspect FILTER：命中条件的图片输出数量+清单（CBZ zip 内直读，不落盘）
                if filter_expr:
                    c_attrs = [build_cbz_image_attrs(zf, n, double_ratio) for n in img_names]
                    _fill_small_mark(c_attrs, extract_small_ratio(filter_expr))
                    c_hits = [a for a in c_attrs if any(eval_filter_atoms(a, g) for g in filter_expr)]
                    info["filter_hits"] = [Path(a["zname"]).name for a in c_hits]
                    if c_hits:
                        emit(t("inspect.filter_hits", count=len(c_hits)), level="summary")
                        for a in c_hits:
                            dim = f"{a['w']}x{a['h']}" if a.get("w") and a.get("h") else "?"
                            emit(f"    {Path(a['zname']).name}  {dim}", level="summary")
                    else:
                        emit(t("inspect.filter_no_hit"), level="info")

                # ComicInfo.xml 预览（若存在）
                if "ComicInfo.xml" in names:
                    try:
                        root = safe_et_parse(zf.read("ComicInfo.xml")).getroot()
                        emit("ComicInfo.xml:")
                        for tag in ("Title", "Series", "Number", "Volume", "Writer", "Publisher", "Year", "LanguageISO", "PageCount", "Summary"):
                            node = root.find(tag)
                            if node is not None and node.text:
                                emit(f"  {tag}: {node.text}")
                        # 结构化字段：从已有 ComicInfo.xml 读取 Series/Number/Volume
                        sn = root.find("Series")
                        nm = root.find("Number")
                        vm = root.find("Volume")
                        if sn is not None and sn.text:
                            info["series"] = sn.text
                            info["series_source"] = "comicinfo"
                        if nm is not None and nm.text:
                            info["number"] = nm.text
                            info["number_source"] = "comicinfo"
                        if vm is not None and vm.text:
                            info["volume"] = vm.text
                            info["volume_source"] = "comicinfo"
                        # PageCount 一致性：ComicInfo 声明页数 vs 实际图片数
                        pc_node = root.find("PageCount")
                        if pc_node is not None and pc_node.text:
                            try:
                                declared = int(pc_node.text.strip())
                                if declared != total_in_dir:
                                    emit(t("inspect.pagecount_mismatch", declared=declared, actual=total_in_dir), level="warning")
                            except ValueError:
                                emit(t("inspect.pagecount_non_numeric", raw=pc_node.text.strip()), level="warning")
                    except Exception:
                        pass
                info["status"] = "ok"
                info["page_count"] = total_in_dir
                info["drm"] = False
                info["spine"] = img_names
                info["toc"] = []
                return InspectStatus.OK, info
        except Exception as e:
            emit(t("inspect.unpack_fail", err=e), level="summary")
            info["status"] = "fail"
            return InspectStatus.FAIL, info

    reason = precheck_ebook(p, min_bytes)
    if reason:
        if "BOOKMOBI" in reason:
            emit(t("inspect.base_invalid_magic"))
        else:
            emit(t("inspect.base_reason", reason=reason))
        emit(t("inspect.invalid_hint"))
        info["status"] = "invalid"
        return InspectStatus.INVALID, info

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
    # DRM 标记不再阻断：降级为信息项，仍继续尝试解包（打位≠真加密，解出图即可正常检查）
    if drm:
        emit(t("inspect.drm_marked_try"), level="info")

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
        if p.suffix.lower() == ".epub":
            tempdir = extract_epub_to_temp(p)
        else:
            tempdir_raw, _ = mobi.extract(str(p))
            tempdir = Path(tempdir_raw)
        extract_temp_paths.append(tempdir)

        has7 = (tempdir / "mobi7").is_dir()
        has8 = (tempdir / "mobi8").is_dir()
        emit(t("inspect.both_dirs", mobi7=has7, mobi8=has8))
        base_dir = select_mobi_dir(tempdir, prefer)

        opf_path = find_opf(base_dir)
        emit(t("inspect.opf_exists") if opf_path else t("inspect.opf_missing"))
        # EPUB 无 EXTH 头：改从 OPF dc:metadata 补充标题/作者/语言等（复用已有 i18n 键）
        if opf_path and p.suffix.lower() == ".epub":
            opf_meta = read_opf_metadata(opf_path)
            opf_parts = []
            if opf_meta.get("title"):
                opf_parts.append(t("inspect.meta_title", value=opf_meta["title"]))
            if opf_meta.get("creator"):
                opf_parts.append(t("inspect.meta_author", value=opf_meta["creator"]))
            if opf_meta.get("language"):
                opf_parts.append(t("inspect.meta_language", value=opf_meta["language"]))
            if opf_meta.get("date"):
                opf_parts.append(t("inspect.meta_publish_date", value=opf_meta["date"]))
            if opf_meta.get("publisher"):
                opf_parts.append(t("inspect.meta_publisher", value=opf_meta["publisher"]))
            if opf_parts:
                emit(t("inspect.meta_line", parts=" | ".join(opf_parts)))
        spine_count = 0
        spine_images = []
        if opf_path:
            spine_images = extract_images_by_spine(opf_path) or []
            spine_count = len(spine_images)
        emit(t("inspect.spine_count", count=spine_count))
        for s_img in spine_images[:5]:
            dim = image_dimensions(s_img)
            dim_str = f"{dim[0]}x{dim[1]}" if dim else "?"
            emit(f"    {s_img.name}  {dim_str}")
        if len(spine_images) > 5:
            emit(f"    ... (共 {spine_count} 张)")

        ncx_count, ncx_preview = parse_ncx_toc(base_dir)
        if ncx_count:
            ncx_str = " | ".join(ncx_preview)
            if len(ncx_preview) < ncx_count:
                ncx_str += " | ..."
            emit(t("inspect.ncx_count", count=ncx_count, preview=ncx_str))
        else:
            emit(t("inspect.ncx_missing"))
        nav_count, nav_preview = parse_nav_toc(base_dir)
        if nav_count:
            nav_str = " | ".join(nav_preview)
            if len(nav_preview) < nav_count:
                nav_str += " | ..."
            emit(t("inspect.nav_count", count=nav_count, preview=nav_str))
        else:
            emit(t("inspect.nav_missing"))

        total_in_dir = count_images_in_dir(base_dir)
        emit(t("inspect.dir_images", count=total_in_dir))

        if total_in_dir == 0:
            if drm:
                emit(t("inspect.drm_hint"), level="info")
                info["status"] = "drm"
                info["drm"] = True
                info["page_count"] = 0
                return InspectStatus.DRM, info
            emit(t("inspect.drm_suspected"))
            emit(t("inspect.cover_missing"))
            emit(t("inspect.fmt_none"))
            emit(t("inspect.drm_bad_hint"), level="info")
            info["status"] = "noimg"
            info["page_count"] = 0
            return InspectStatus.NOIMG, info
        if drm:
            emit(t("inspect.drm_but_readable", count=total_in_dir), level="info")
        else:
            emit(t("inspect.drm_none", count=total_in_dir))

        # 封面检测：OPF guide type=cover 引用优先，未命中回退文件名扫描
        cover = None
        cover_src = ""
        if opf_path:
            href = get_opf_guide_cover_href(opf_path)
            if href:
                # href 相对 OPF 所在目录（epub 的 OPF 常在 OEBPS/ 子目录），未命中回退解压根目录
                cand = (opf_path.parent / href).resolve()
                if not (cand.is_file() and cand.suffix.lower() in IMAGE_EXTENSIONS):
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
            dim = image_dimensions(cover)
            dim_str = f"{dim[0]}x{dim[1]}" if dim else "?"
            size_str = f"{cover.stat().st_size / 1024:.0f}KB"
            emit(t("inspect.cover_found", name=cover.name, src=cover_src, dim=dim_str, size=size_str))
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
        emit(t("inspect.fmt_stats", total=total_fmt, parts=" | ".join(fmt_parts)))

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
            res_summary = inspect_res_summary(res_list, t)
            if res_summary:
                emit(res_summary)

        # 丢弃小图预览：开启 --drop small 时会丢弃多少张（仅提示，不改变转换；面积口径）
        if drop_small is not None and len(res_list) > 1:
            med_area = _median_area(res_list)
            small_n = sum(1 for w, h in res_list if w * h < med_area * drop_small)
            if small_n:
                emit(t("inspect.drop_small_preview", count=small_n))

        # --inspect FILTER：命中条件的图片输出数量+清单（复用过滤引擎与面积口径）
        if filter_expr:
            f_attrs = [build_image_attrs(fp, double_ratio) for fp in all_imgs]
            _fill_small_mark(f_attrs, extract_small_ratio(filter_expr))
            f_hits = [a for a in f_attrs if any(eval_filter_atoms(a, g) for g in filter_expr)]
            info["filter_hits"] = [a["path"].name for a in f_hits]
            if f_hits:
                emit(t("inspect.filter_hits", count=len(f_hits)), level="summary")
                for a in f_hits:
                    dim = f"{a['w']}x{a['h']}" if a.get("w") and a.get("h") else "?"
                    emit(f"    {a['path'].name}  {dim}", level="summary")
            else:
                emit(t("inspect.filter_no_hit"), level="info")

        # 压缩建议
        jpeg_ratio = (fmt_counter.get("jpg", 0) + fmt_counter.get("jpeg", 0)) / total_fmt
        png_ratio = fmt_counter.get("png", 0) / total_fmt
        if png_ratio >= 0.5:
            emit(t("inspect.adv_png"))
        elif jpeg_ratio >= 0.8:
            emit(t("inspect.adv_jpeg"))
        else:
            emit(t("inspect.adv_mixed"))
        info.update(_inspect_img_summary(fmt_counter))

        # ComicInfo.xml 预览块（inspect 不写文件，仅展示即将生成的元数据）
        opf_meta = read_opf_metadata(opf_path) if opf_path else {}
        cmeta = collect_comicinfo_meta(opf_meta, meta, p)
        # 来源标注与 build_comicinfo 优先级一致：setinfo > OPF 元数据 > 文件名推断
        cinf_s, cinf_n, cinf_v = infer_series_number(p)
        csetinfo = parse_setinfo_args(setinfo_args or [], cmeta, (cinf_s, cinf_n, cinf_v), p)
        series_src = "setinfo" if "Series" in csetinfo else ("opf" if cmeta.get("series") else ("inferred" if cinf_s else None))
        number_src = "setinfo" if "Number" in csetinfo else ("opf" if cmeta.get("number") else ("inferred" if cinf_n else None))
        volume_src = "setinfo" if "Volume" in csetinfo else ("inferred" if cinf_v else None)
        cseries = csetinfo.get("Series") or cmeta.get("series") or cinf_s
        cnumber = csetinfo.get("Number") or cmeta.get("number") or cinf_n
        cvolume = csetinfo.get("Volume") or cinf_v
        emit("ComicInfo.xml:")
        if csetinfo.get("Title") or cmeta.get("title"):
            emit(f"  Title: {csetinfo.get('Title') or cmeta.get('title')}")
        if cseries:
            emit(f"  Series: {_c(36, str(cseries))} [{_c(33, t('comicinfo.src.' + series_src))}]")
        if cnumber:
            emit(f"  Number: {_c(32, str(cnumber))} [{_c(33, t('comicinfo.src.' + number_src))}]")
        if cvolume:
            emit(f"  Volume: {_c(35, str(cvolume))} [{_c(33, t('comicinfo.src.' + volume_src))}]")
        if csetinfo.get("Writer") or cmeta.get("writer"):
            emit(f"  Writer: {csetinfo.get('Writer') or cmeta.get('writer')}")
        if csetinfo.get("Publisher") or cmeta.get("publisher"):
            emit(f"  Publisher: {csetinfo.get('Publisher') or cmeta.get('publisher')}")
        if csetinfo.get("Year") or cmeta.get("year"):
            emit(f"  Year: {csetinfo.get('Year') or cmeta.get('year')}")
        if csetinfo.get("LanguageISO") or cmeta.get("language"):
            emit(f"  LanguageISO: {csetinfo.get('LanguageISO') or cmeta.get('language')}")
        emit(f"  PageCount: {len(all_imgs)}")
        if csetinfo.get("Summary") or cmeta.get("summary"):
            emit(f"  Summary: {csetinfo.get('Summary') or cmeta.get('summary')}")
        # 结构化字段：series/number 来源标注与人类输出一致（setinfo > opf > inferred）
        info["status"] = "ok"
        info["series"] = cseries or cinf_s
        info["number"] = cnumber or cinf_n
        info["volume"] = cvolume or cinf_v
        info["series_source"] = series_src or ("inferred" if cinf_s else None)
        info["number_source"] = number_src or ("inferred" if cinf_n else None)
        info["volume_source"] = volume_src or ("inferred" if cinf_v else None)
        info["page_count"] = len(all_imgs)
        info["drm"] = drm
        info["spine"] = [str(x) for x in spine_images]
        info["toc"] = list(ncx_preview) + (list(nav_preview) if nav_count else [])
        return InspectStatus.OK, info
    except Exception as e:
        emit(t("inspect.unpack_fail", err=e), level="summary")
        err = str(e).lower()
        if drm or any(k in err for k in ("drm", "encrypt", "decrypt", "protected", "kfx")):
            emit(t("inspect.drm_hint"), level="info")
            info["status"] = "drm"
            info["drm"] = True
            return InspectStatus.DRM, info
        info["status"] = "fail"
        return InspectStatus.FAIL, info
    finally:
        for tp in extract_temp_paths:
            if tp.exists():
                try:
                    shutil.rmtree(tp)
                except Exception as e:
                    emit(t("warn.cleanup_tmp_fail", path=tp, err=e), level="warning")


def modify_cbz_comicinfo(cbz_path: Path, setinfo_args: list) -> bool:
    """修改已有 CBZ 的 ComicInfo.xml：读原 XML → 未指定字段保留原值 → setinfo 覆盖 → 原子替换。

    无 ComicInfo.xml 时新建（PageCount 由 CBZ 实际图片数决定）。
    返回是否实际发生修改；白名单外字段已在 parse_setinfo_args 过滤。
    """
    # 第一遍仅扫描元信息（不读图片数据）：定位 ComicInfo.xml（KB 级小文件，读入无妨）并统计图片数
    with zipfile.ZipFile(str(cbz_path)) as zf:
        infos = zf.infolist()
        img_count = sum(1 for it in infos if Path(it.filename).suffix.lower() in IMAGE_EXTENSIONS)
        existing_data = None
        for it in infos:
            if it.filename == "ComicInfo.xml":
                existing_data = zf.read(it)
                break

    if existing_data:
        root = safe_et_parse(existing_data).getroot()
    else:
        root = ET.Element("ComicInfo")
        pc = ET.SubElement(root, "PageCount")
        pc.text = str(img_count)

    # 解析 setinfo：占位符从已有 ComicInfo.xml 元数据取值（无 XML 时保持空 dict，%number 等文件名推断仍可用）
    meta = _meta_from_comicinfo_root(root) if existing_data else {}
    setinfo = parse_setinfo_args(setinfo_args, meta, infer_series_number(cbz_path), cbz_path)
    changed = False
    for field, value in setinfo.items():
        # Summary 与转换模式一致：剥离 HTML 标签保留纯文本（.text 序列化时自动转义特殊字符）
        if field == "Summary" and value:
            cleaned = _strip_html(str(value))
            if cleaned is not None:
                value = cleaned
        node = root.find(field)
        if node is None:
            node = ET.SubElement(root, field)
        if node.text != str(value):
            node.text = str(value)
            changed = True

    if not changed:
        return False

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    # 重建 zip：流式复制原包全部条目（内存 O(单条目)），仅替换 ComicInfo.xml；
    # 保留各条目原始压缩方式与属性
    tmp = cbz_path.with_name(cbz_path.name + ".tmp")
    try:
        with zipfile.ZipFile(str(cbz_path)) as zin, zipfile.ZipFile(str(tmp), "w") as zout:
            wrote_xml = False
            for it in zin.infolist():
                if it.filename == "ComicInfo.xml":
                    zi = zipfile.ZipInfo("ComicInfo.xml")
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zi.date_time = tuple(datetime.now().timetuple()[:6])
                    zout.writestr(zi, xml_bytes)
                    wrote_xml = True
                    continue
                zi = zipfile.ZipInfo(it.filename)
                zi.compress_type = it.compress_type
                zi.date_time = it.date_time
                zi.external_attr = it.external_attr
                zi.internal_attr = it.internal_attr
                zi.create_system = it.create_system
                with zin.open(it) as src, zout.open(zi, "w") as dst:
                    shutil.copyfileobj(src, dst, length=1024 * 1024)
            if not wrote_xml:
                # 原 zip 无 ComicInfo.xml：追加新建的 XML
                zi = zipfile.ZipInfo("ComicInfo.xml")
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.date_time = tuple(datetime.now().timetuple()[:6])
                zout.writestr(zi, xml_bytes)
        os.replace(str(tmp), str(cbz_path))
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise
    return True


def _meta_from_comicinfo_root(root) -> dict:
    """从 ComicInfo.xml 根元素提取占位符所需 meta 键（series/number/volume/writer/
    publisher/language/summary/date 等）。

    供 --setinfo 修改/预览已有 CBZ 时解析 %series/%number/%volume/%writer/%publisher/
    %language/%description/%date 占位符；无对应字段时省略（与转换链路语义一致，不生成空值）。
    """
    meta: dict = {}
    for tag, key in (("Title", "title"), ("Series", "series"), ("Number", "number"),
                     ("Volume", "volume"), ("Writer", "writer"), ("Publisher", "publisher"),
                     ("LanguageISO", "language"), ("Summary", "summary")):
        el = root.find(tag)
        if el is not None and el.text and el.text.strip():
            meta[key] = el.text.strip()
    y = root.find("Year")
    if y is not None and y.text and y.text.strip():
        date = y.text.strip()
        mo = root.find("Month")
        if mo is not None and mo.text and mo.text.strip():
            date += "-" + mo.text.strip().zfill(2)
            d = root.find("Day")
            if d is not None and d.text and d.text.strip():
                date += "-" + d.text.strip().zfill(2)
        meta["date"] = date
    return meta


def _read_existing_comicinfo(cbz_path: Path):
    """读取 CBZ 内已有 ComicInfo.xml 的根元素；无则返回 None。"""
    try:
        with zipfile.ZipFile(str(cbz_path)) as zf:
            for it in zf.infolist():
                if it.filename == "ComicInfo.xml":
                    return safe_et_parse(zf.read(it)).getroot()
    except Exception:
        pass
    return None


def _preview_modify_changes(cbz_path: Path, setinfo_args: list) -> list:
    """dry-run 预览：读原 ComicInfo.xml 对比待写值，返回 [字段, 旧值, 新值] 列表。

    仅返回有变化的字段；省略值不变字段。无 ComicInfo.xml 时全部视为新增。
    """
    old_root = _read_existing_comicinfo(cbz_path)
    old_text = {n.tag: n.text for n in old_root.iter()} if old_root is not None else {}
    meta = _meta_from_comicinfo_root(old_root) if old_root is not None else {}
    new_values = parse_setinfo_args(setinfo_args, meta, infer_series_number(cbz_path), cbz_path)
    changes = []
    for field, new_val in new_values.items():
        # Summary 预览值同样做 HTML 清理，与实际写入保持一致
        if field == "Summary" and new_val:
            cleaned = _strip_html(str(new_val))
            if cleaned is not None:
                new_val = cleaned
        old_val = old_text.get(field)
        if old_val != str(new_val):
            changes.append((field, old_val, str(new_val)))
    return changes


def rename_cbz_mode(cbz_files: list[Path], args) -> None:
    """--rename 独立批量重命名已有 CBZ 模式入口（不转换，只改文件名）。

    复用 _build_rename_basename 计算新文件名；纳入 --dry-run / 进度条 / 汇总统计 / --log / --json。
    JSON schema：source / renamed{old,new} / series / number / volume / *_source / type / dry_run。
    目标同名已存在时跳过（不覆盖），与转换链路 will_skip 语义一致。
    """
    total_start = time.perf_counter()
    emit(t("rename_cbz.header", count=len(cbz_files)), level="summary")
    if args.dry_run:
        pbar = create_progress_if_needed(args, cbz_files, t("progress.desc.rename"))
        used_names: set = set()
        json_files: list = []
        try:
            for mf in cbz_files:
                if pbar is not None:
                    pbar.set_postfix_str(truncate_name(mf.name))
                new_stem, info = _build_rename_basename(mf, args.rename)
                out = _apply_rename_to_target(mf, new_stem)
                will_skip = (out.exists() or str(out) in used_names) and not args.overwrite
                skip_reason = None
                if will_skip:
                    skip_reason = "conflict" if str(out) in used_names else "existing"
                # dry-run 预览着色：skip 状态按撞名类别区分（A 类磁盘同名=黄 33 / B 类本批撞名=品红 35）
                if will_skip:
                    state_tag = _c(33, t("tag.will_skip")) if skip_reason == "existing" else _c(35, t("tag.will_skip"))
                else:
                    state_tag = t("tag.pending")
                if not will_skip:
                    used_names.add(str(out))
                # rename 预览着色（颜色③）：主干青色、自动标记前缀绿色（仅 TTY 且未 --no-color 时生效）
                if info["new_stem"] != info["old_stem"]:
                    mark = info.get("mark") or ""
                    new_stem = info["new_stem"]
                    head = new_stem[:-len(mark)] if mark and new_stem.endswith(mark) else new_stem
                    out_disp = _c(36, head) + (_c(32, mark) if mark else "") + ".cbz"
                    emit(f"  {state_tag} {mf.name} -> {out_disp}", level="summary")
                else:
                    emit(f"  {state_tag} {mf.name} -> {out.name}", level="summary")
                if will_skip and info["new_stem"] != info["old_stem"]:
                    if skip_reason == "conflict":
                        emit(t("rename_cbz.skip_conflict", name=mf.name, target=out.name), level="warning")
                    else:
                        emit(t("rename_cbz.skip_existing", name=mf.name, target=out.name), level="warning")
                json_files.append({
                    "source": str(mf),
                    "renamed": {"old": mf.name, "new": out.name} if info["new_stem"] != info["old_stem"] else None,
                    "series": info.get("series"),
                    "number": info.get("number"),
                    "volume": info.get("volume"),
                    "series_source": info.get("series_source"),
                    "number_source": info.get("number_source"),
                    "volume_source": info.get("volume_source"),
                    "type": info.get("type"),
                    "status": "will_skip" if will_skip else "pending",
                    "reason": skip_reason,
                    "target": str(out),
                    "dry_run": True,
                })
                if pbar is not None:
                    pbar.update(1)
        finally:
            if pbar is not None:
                pbar.close()
        emit(t("rename_cbz.dryrun_end"), level="summary")
        emit_json(json_files, success=0, skipped=sum(1 for x in json_files if x["status"] == "will_skip"),
                  failed=0, interrupted=False, total_elapsed=time.perf_counter() - total_start)
        return

    success = 0
    nochange = 0
    skipped_existing = []
    skipped_conflict = []
    failed_files = []
    failed_reasons = Counter()
    used_names: set = set()
    json_files: list = []
    pbar = create_progress_if_needed(args, cbz_files, t("progress.desc.rename"))
    try:
        for mf in cbz_files:
            if pbar is not None:
                pbar.set_postfix_str(truncate_name(mf.name))
            try:
                new_stem, info = _build_rename_basename(mf, args.rename)
                out = _apply_rename_to_target(mf, new_stem)
                if new_stem == info["old_stem"]:
                    nochange += 1
                    emit(t("rename_cbz.nochange", name=mf.name), level="summary")
                    json_status = "nochange"
                    json_target = None
                elif (out.exists() or str(out) in used_names) and not args.overwrite:
                    if str(out) in used_names:
                        skipped_conflict.append(mf)
                        json_skip_reason = "conflict"
                        emit(t("rename_cbz.skip_conflict", name=mf.name, target=out.name), level="warning")
                    else:
                        skipped_existing.append(mf)
                        json_skip_reason = "existing"
                        emit(t("rename_cbz.skip_existing", name=mf.name, target=out.name), level="warning")
                    json_status = "skip"
                    json_target = str(out)
                else:
                    os.replace(str(mf), str(out))
                    success += 1
                    used_names.add(str(out))
                    emit(t("rename_cbz.done", name=mf.name, new=out.name), level="summary")
                    json_status = "ok"
                    json_target = str(out)
                json_files.append({
                    "source": str(mf),
                    "renamed": {"old": mf.name, "new": out.name} if json_status == "ok" else None,
                    "series": info.get("series"),
                    "number": info.get("number"),
                    "volume": info.get("volume"),
                    "series_source": info.get("series_source"),
                    "number_source": info.get("number_source"),
                    "volume_source": info.get("volume_source"),
                    "type": info.get("type"),
                    "status": json_status,
                    "reason": json_skip_reason if json_status == "skip" else None,
                    "target": json_target,
                    "dry_run": False,
                })
            except Exception as e:
                failed_files.append(mf)
                failed_reasons[str(e)] += 1
                emit(t("rename_cbz.fail", name=mf.name, err=e), level="error")
                json_files.append({
                    "source": str(mf), "renamed": None, "status": "fail",
                    "target": None, "reason": str(e), "dry_run": False,
                })
            if pbar is not None:
                pbar.update(1)
    finally:
        if pbar is not None:
            pbar.close()
    emit(t("rename_cbz.stats", success=success, nochange=nochange,
          existing=len(skipped_existing), conflict=len(skipped_conflict),
          skip=len(skipped_existing) + len(skipped_conflict), fail=len(failed_files)), level="summary")
    if skipped_existing:
        emit(t("rename_cbz.skipped_existing_header", count=len(skipped_existing)), level="summary")
        for f in skipped_existing:
            emit(f"  {f}", level="summary")
    if skipped_conflict:
        emit(t("rename_cbz.skipped_conflict_header", count=len(skipped_conflict)), level="summary")
        for f in skipped_conflict:
            emit(f"  {f}", level="summary")
    if failed_files:
        emit(t("run.failed_header", count=len(failed_files)), level="summary")
        for f in failed_files:
            emit(f"  {f}", level="summary")
    if failed_reasons:
        parts = ", ".join(f"{k}={v}" for k, v in failed_reasons.items())
        emit(t("rename_cbz.failed_reasons", summary=parts), level="summary")
    emit_json(json_files, success=success, skipped=len(skipped_existing) + len(skipped_conflict) + nochange,
              failed=len(failed_files), interrupted=False, total_elapsed=time.perf_counter() - total_start)


def modify_cbz_mode(cbz_files: list[Path], args) -> None:
    """--setinfo 修改已有 CBZ 的 ComicInfo.xml 模式入口。

    纳入 --dry-run / 进度条 / 汇总统计 / --log。
    """
    total_start = time.perf_counter()
    emit(t("modify.header", count=len(cbz_files)), level="summary")
    if args.dry_run:
        pbar = create_progress_if_needed(args, cbz_files, t("progress.desc.modify"))
        json_files: list = []
        try:
            for mf in cbz_files:
                if pbar is not None:
                    pbar.set_postfix_str(truncate_name(mf.name))
                emit(t("modify.plan", name=mf.name), level="summary")
                for field, old_val, new_val in _preview_modify_changes(mf, args.setinfo):
                    if old_val is None:
                        emit(t("modify.plan_add", field=field, value=new_val), level="summary")
                    else:
                        emit(t("modify.plan_change", field=field, old=old_val, new=new_val), level="summary")
                json_files.append({
                    "source": str(mf),
                    "status": "pending",
                    "target": str(mf),
                    "reason": None,
                    "elapsed_sec": None,
                    "dry_run": True,
                })
                if pbar is not None:
                    pbar.update(1)
        finally:
            if pbar is not None:
                pbar.close()
        emit(t("modify.dryrun_end"), level="summary")
        emit_json(json_files, success=0, skipped=0, failed=0,
                  interrupted=False, total_elapsed=time.perf_counter() - total_start)
        return

    # 处理前清单：逐文件列出将修改的字段变更（与 dry-run 分支一致）
    for mf in cbz_files:
        emit(t("modify.plan", name=mf.name), level="summary")
        for field, old_val, new_val in _preview_modify_changes(mf, args.setinfo):
            if old_val is None:
                emit(t("modify.plan_add", field=field, value=new_val), level="summary")
            else:
                emit(t("modify.plan_change", field=field, old=old_val, new=new_val), level="summary")

    success = 0
    nochange = 0
    failed_files = []
    failed_reasons = Counter()
    json_files: list = []
    pbar = create_progress_if_needed(args, cbz_files, t("progress.desc.modify"))
    try:
        for mf in cbz_files:
            if pbar is not None:
                pbar.set_postfix_str(truncate_name(mf.name))
            try:
                if modify_cbz_comicinfo(mf, args.setinfo):
                    success += 1
                    emit(t("modify.done", name=mf.name), level="summary")
                    json_status = "modified"
                else:
                    nochange += 1
                    emit(t("modify.nochange", name=mf.name), level="summary")
                    json_status = "nochange"
                json_files.append({
                    "source": str(mf),
                    "status": json_status,
                    "target": str(mf),
                    "reason": None,
                    "elapsed_sec": None,
                })
            except Exception as e:
                failed_files.append(mf)
                failed_reasons[str(e)] += 1
                emit(t("modify.fail", name=mf.name, err=e), level="error")
                json_files.append({
                    "source": str(mf),
                    "status": "fail",
                    "target": str(mf),
                    "reason": str(e),
                    "elapsed_sec": None,
                })
            if pbar is not None:
                pbar.update(1)
    finally:
        if pbar is not None:
            pbar.close()

    emit(t("modify.stats", success=success, nochange=nochange, fail=len(failed_files)), level="summary")
    if failed_files:
        emit(t("run.failed_header", count=len(failed_files)), level="summary")
        for mf in failed_files:
            emit(f"  {mf}", level="summary")
    if failed_reasons:
        parts = ", ".join(f"{k}={v}" for k, v in failed_reasons.items())
        emit(t("modify.failed_reasons", summary=parts), level="summary")
    total_elapsed = time.perf_counter() - total_start
    emit_json(json_files, success=success, skipped=nochange,
              failed=len(failed_files), interrupted=False,
              total_elapsed=total_elapsed)


def _unpack_dir_parts(name: str) -> tuple[str, str, str]:
    """把解包目录名拆成 (还原stem, 序号后缀, 来源扩展名)。

    vol_cbz → ("vol", "", "cbz")；vol_cbz (2) → ("vol", " (2)", "cbz")
    vol_mobi → ("vol", "", "mobi")；非解包目录名返回 (name, "", "")。
    供 --repack 识别 `_cbz` 来源并还原输出名。
    """
    num = ""
    m = re.match(r"^(.*?)(\s*\(\d+\))?$", name)
    base = m.group(1) if m else name
    num = (m.group(2) if m else "") or ""
    for ext in (".cbz", ".mobi", ".epub"):
        suf = "_" + ext.lstrip(".")
        if base.lower().endswith(suf):
            return base[: -len(suf)], num, ext.lstrip(".")
    return name, "", ""


def _is_unpack_cbz_dir(name: str) -> bool:
    """目录名是否为 cbz 解包目录（以 _cbz 结尾，允许带 (N) 序号）。"""
    return _unpack_dir_parts(name)[2] == "cbz"


def unpack_ebook(p: Path, out_root: Path) -> Path:
    """解包电子书到 out_root 下的同名子目录（默认 源名_扩展名，撞名时再以 (N) 序号避让）。

    目录名为 `源名_扩展名`（如 vol.cbz → vol_cbz/，vol.mobi → vol_mobi/），
    统一来源标签且与源文件不撞名；--repack 按 _cbz 结尾识别 cbz 解包目录。
    mobi 走 mobi.extract 保留完整结构（mobi7/mobi8 等），cbz/epub 逐条目
    安全解压（含 zip-slip 路径穿越防护）。返回实际解包到的目录。
    """
    base = f"{p.stem}_{p.suffix.lstrip('.')}"
    out_dir = out_root / base
    n = 2
    while out_dir.exists():
        out_dir = out_root / f"{base} ({n})"
        n += 1
    out_dir.mkdir(parents=True, exist_ok=True)
    if p.suffix.lower() in (".cbz", ".epub"):
        with zipfile.ZipFile(str(p)) as zf:
            _safe_zip_extract(zf, out_dir)
    else:
        tempdir_raw, _ = mobi.extract(str(p))
        tempdir = Path(tempdir_raw)
        try:
            for item in tempdir.iterdir():
                shutil.move(str(item), str(out_dir / item.name))
        finally:
            try:
                shutil.rmtree(str(tempdir))
            except Exception as e:
                emit(t("warn.cleanup_tmp_fail", path=tempdir, err=e), level="warning")
    return out_dir


def unpack_mode(ebook_files: list[Path], args) -> None:
    """--unpack 模式入口：只解包不转换，输出到各源文件所在目录的「源名_扩展名」子目录。

    执行前先列出待解包文件清单，逐个解包后输出完成汇总。
    """
    if not ebook_files:
        emit(t("inspect_mode.none"), level="error")
        sys.exit(0)
    # 处理清单：先列出将解包的文件
    emit(t("unpack.plan", count=len(ebook_files)), level="summary")
    for i, mf in enumerate(ebook_files, 1):
        emit(f"  {i}. {mf}", level="summary")
    ok_n = fail_n = 0
    for mf in ebook_files:
        try:
            out_dir = unpack_ebook(mf, mf.parent)
            emit(t("unpack.done", name=mf.name, dir=out_dir))
            ok_n += 1
        except Exception as e:
            emit(t("inspect.unpack_fail", err=e), level="error")
            fail_n += 1
    emit(t("unpack.done_summary", ok=ok_n, fail=fail_n), level="summary")
    sys.exit(1 if fail_n else 0)


def repack_one(src_dir: Path, args) -> bool:
    """把单个 cbz 解包目录（目录名以 _cbz 结尾，允许带 (N) 序号）打包回 CBZ。

    忠实打包：只收白名单图片（jpg/jpeg/png/gif/webp/bmp/tiff），自然排序，
    ZIP_STORED 不二次压缩，跨子目录重名自动加序号前缀（_compute_arcnames）。
    ComicInfo.xml：--no-comicinfo 关闭；目录内有则原样带回（--setinfo 叠加
    覆盖）；无则生成基础版（页数=实际图数，标题/卷号从还原后的源文件名
    推断，如 vol_cbz → vol）。输出到解包目录旁，文件名还原为源文件
    （vol_cbz → vol.cbz，vol_cbz (2) → vol (2).cbz），已存在默认跳过，
    --overwrite 强制覆盖；--output-dir 指定目录。
    校验通过才原子替换，失败只删 .tmp 半成品，不碰已有目标。
    """
    recon_stem, num_suffix, _ext = _unpack_dir_parts(src_dir.name)
    # 还原后的虚拟源文件名（vol_cbz → vol.cbz），供元数据推断按源文件语义走
    virtual_src = src_dir.with_name(recon_stem + num_suffix + ".cbz")
    images: list[Path] = []
    for root, _dirs, files in os.walk(src_dir):
        for fn in files:
            if Path(fn).suffix.lower() in IMAGE_EXTENSIONS:
                images.append(Path(root) / fn)
    images.sort(key=natural_key)
    if not images:
        emit(t("repack.no_images", dir=src_dir), level="error")
        return False

    # arcname 预计算（跨子目录重名加序号前缀），与 ComicInfo Page Image 共用
    arcnames, skipped_dup = _compute_arcnames(images)

    # ComicInfo.xml：--no-comicinfo 关闭；有则原样带回（--setinfo 叠加）；无则生成基础版
    xml_bytes: bytes | None = None
    existing_ci = src_dir / "ComicInfo.xml"
    if args.no_comicinfo:
        xml_bytes = None
    elif existing_ci.exists():
        try:
            root = safe_et_parse(existing_ci.read_bytes()).getroot()
        except Exception as e:
            emit(t("comicinfo.invalid", err=e), level="error")
            root = None
        if root is not None:
            meta = _meta_from_comicinfo_root(root)
            inferred = infer_series_number(virtual_src)
            setinfo = parse_setinfo_args(args.setinfo, meta, inferred, virtual_src)
            for field, value in setinfo.items():
                if field == "Summary" and value:
                    cleaned = _strip_html(str(value))
                    if cleaned is not None:
                        value = cleaned
                node = root.find(field)
                if node is None:
                    node = ET.SubElement(root, field)
                node.text = str(value)
            xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    else:
        # 无 ComicInfo：生成基础版，标题兜底用还原后的源文件名（vol_cbz → vol）
        meta = {"title": recon_stem + num_suffix}
        inferred = infer_series_number(virtual_src)
        built = build_comicinfo(meta, images, inferred,
                                parse_setinfo_args(args.setinfo, meta, inferred, virtual_src),
                                arcnames=arcnames)
        if built is not None:
            xml_bytes = built[0].encode("utf-8")

    # 输出路径：解包目录旁，文件名还原为源文件（vol_cbz → vol.cbz）；
    # --output-dir 指定目录
    out_name = recon_stem + num_suffix + ".cbz"
    if args.output_dir:
        out_file = Path(args.output_dir) / out_name
    else:
        out_file = src_dir.parent / out_name
    if out_file.exists() and not args.overwrite:
        emit(t("repack.skip_exists", path=out_file), level="warning")
        return True

    # 原子打包：先写 .tmp，校验通过后 os.replace；失败只删 .tmp 不碰已有目标
    tmp = out_file.with_name(out_file.name + ".tmp")
    try:
        with zipfile.ZipFile(str(tmp), "w", zipfile.ZIP_STORED) as zf:
            seen: set = set()
            for img in images:
                norm = norm_path(img)
                if norm in seen:
                    continue
                seen.add(norm)
                zf.write(str(img), arcnames[img])
            if xml_bytes is not None:
                zf.writestr("ComicInfo.xml", xml_bytes)
        ok, msg = validate_cbz(tmp, require_comicinfo=(xml_bytes is not None))
        if not ok:
            tmp.unlink(missing_ok=True)
            emit(t("convert.verify_fail", name=out_file.name, msg=msg), level="error")
            return False
        os.replace(str(tmp), str(out_file))
    except Exception as e:
        tmp.unlink(missing_ok=True)
        emit(t("repack.fail", dir=src_dir, err=e), level="error")
        return False
    if skipped_dup:
        emit(t("convert.dedup_physical", count=skipped_dup), level="summary")
    size_mb = out_file.stat().st_size / (1024 * 1024)
    emit(t("repack.done", name=out_file.name, count=len(images), size=f"{size_mb:.1f}"))
    return True


def repack_mode(target: Path, args) -> None:
    """--repack 模式入口：把已解包的 CBZ 解包目录（目录名以 _cbz 结尾）打包回 CBZ。

    target 自身是 _cbz 结尾目录 → 单目录；target 是普通目录 → 递归收集其下
    所有 _cbz 结尾目录批量打包（不递归进解包目录内部，避免嵌套重复）。
    执行前先列出待处理清单，逐个打包后输出完成汇总。
    """
    dirs: list[Path] = []
    if target.is_dir() and _is_unpack_cbz_dir(target.name):
        dirs = [target]
    elif target.is_dir():
        for root, dnames, _ in os.walk(target):
            for d in list(dnames):
                if _is_unpack_cbz_dir(d):
                    dirs.append(Path(root) / d)
                    dnames.remove(d)  # 不递归进解包目录内部
        dirs.sort(key=lambda p: str(p).lower())
    else:
        emit(t("error.repack_need_dir", path=target), level="error")
        sys.exit(2)
    if not dirs:
        emit(t("repack.none_found", path=target), level="error")
        sys.exit(2)
    # 处理清单：先列出将重新打包的解包目录
    if args.rename:
        emit(t("repack.rename_ignored"), level="warning")
    emit(t("repack.plan", count=len(dirs)), level="summary")
    for i, d in enumerate(dirs, 1):
        recon_stem, num_suffix, _ext = _unpack_dir_parts(d.name)
        emit(f"  {i}. {d}  →  {recon_stem + num_suffix + '.cbz'}", level="summary")
    ok_n = fail_n = 0
    for d in dirs:
        if repack_one(d, args):
            ok_n += 1
        else:
            fail_n += 1
    emit(t("repack.done_summary", ok=ok_n, fail=fail_n), level="summary")
    sys.exit(1 if fail_n else 0)


def inspect_mode(ebook_files: list[Path], precheck_skipped: list, args) -> None:
    """--inspect 模式入口：随机抽查或全量检查电子书内部信息，不生成 CBZ"""
    if precheck_skipped:
        emit(t("inspect_mode.precheck_header", count=len(precheck_skipped)), level="summary")
        for mf, reason in precheck_skipped:
            emit("  " + t("skip_entry", path=str(mf), reason=reason), level="summary")

    if not ebook_files:
        emit(t("inspect_mode.none"), level="error")
        sys.exit(0)

    if args.inspect[0] == "all":
        targets = ebook_files
        emit(t("inspect_mode.all", count=len(targets)), level="summary")
    else:
        targets = [random.choice(ebook_files)]
        emit(t("inspect_mode.random", total=len(ebook_files)), level="summary")

    total_start = time.perf_counter()
    ok = fail = invalid = noimg = drm_n = timeout_n = 0
    inspect_records: list = []
    pbar = create_progress_if_needed(args, targets, t("progress.desc.inspect"))
    try:
        for mf in targets:
            if pbar is not None:
                pbar.set_postfix_str(truncate_name(mf.name))
            timed_out, result = run_with_timeout(inspect_ebook, args.timeout, mf, args.min_size, args.prefer, args.setinfo, extract_small_ratio(args.drop), args.inspect[1], args.double_page)
            if timed_out:
                emit(t("inspect_mode.timeout", name=mf.name, seconds=args.timeout), level="error")
                emit(t("inspect_mode.timeout_residue"), level="warning")
                timeout_n += 1
                inspect_records.append({"source": str(mf), "status": "timeout"})
            else:
                status, info = result
                inspect_records.append(info)
                if status == InspectStatus.INVALID:
                    invalid += 1
                elif status == InspectStatus.DRM:
                    drm_n += 1
                elif status == InspectStatus.NOIMG:
                    noimg += 1
                elif status == InspectStatus.OK:
                    ok += 1
                else:
                    fail += 1
            # --rename 联动预览：inspect 时输出「原始 → 变更后」文件名（不落盘）
            if args.rename:
                try:
                    new_stem, rinfo = _build_rename_basename(mf, args.rename)
                    if rinfo["new_stem"] != rinfo["old_stem"]:
                        mark = rinfo.get("mark") or ""
                        ns = rinfo["new_stem"]
                        head = ns[:-len(mark)] if mark and ns.endswith(mark) else ns
                        out_disp = _c(36, head) + (_c(32, mark) if mark else "") + ".cbz"
                        emit(f"  {t('tag.rename_preview')} {mf.name} -> {out_disp}", level="summary")
                except Exception:
                    pass
            if pbar is not None:
                pbar.update(1)
    except KeyboardInterrupt:
        emit(t("inspect_mode.ctrl_c"), level="summary")
        sys.exit(130)
    finally:
        if pbar is not None:
            pbar.close()

    total_elapsed = time.perf_counter() - total_start
    if args.inspect[0] != "all":
        emit(t("inspect_mode.random_note", total=len(ebook_files)), level="summary")
    emit(
        t(
            "inspect_mode.summary",
            total=len(targets), ok=ok, invalid=invalid, drm=drm_n,
            noimg=noimg, timeout=timeout_n, elapsed=f"{total_elapsed:.1f}",
        ),
        level="summary",
    )

    # #60：inspect 模式 JSON 输出（--json 精简版 stdout / --json-out 落盘全量）
    if _json_stdout or _json_out_path:
        _emit_inspect_json(inspect_records, total_elapsed)

    # 退出码语义：inspect 检出异常（fail/invalid/timeout/drm）时退出 1，noimg 视为正常状态
    sys.exit(1 if (fail or invalid or timeout_n or drm_n) else 0)


def _emit_inspect_json(records: list, total_elapsed: float) -> None:
    """inspect 模式 JSON 输出：stdout 精简版（每文件一行）、--json-out 落盘全量。

    精简字段：source/status/series/number/volume/series_source/number_source/volume_source/page_count/drm；
    全量字段在精简基础上追加 spine/toc。status 值域：ok/drm/invalid/noimg/timeout/fail。
    """
    base_fields = ("source", "status", "series", "number", "volume", "series_source", "number_source", "volume_source", "page_count", "drm", "filter_hits", "formats")
    summary = {
        "total": len(records),
        "ok": sum(1 for r in records if r.get("status") == "ok"),
        "drm": sum(1 for r in records if r.get("status") == "drm"),
        "invalid": sum(1 for r in records if r.get("status") == "invalid"),
        "noimg": sum(1 for r in records if r.get("status") == "noimg"),
        "timeout": sum(1 for r in records if r.get("status") == "timeout"),
        "fail": sum(1 for r in records if r.get("status") == "fail"),
        "total_elapsed_sec": round(total_elapsed, 3),
    }
    if _json_out_path:
        payload = {
            "version": __version__,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "mode": "inspect",
            "summary": summary,
            "files": records,
        }
        out_p = Path(_json_out_path)
        try:
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with out_p.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            emit(t("json.written", path=out_p), level="summary")
        except Exception as e:
            emit(t("error.json_write_failed", err=e, path=out_p), level="error")
    if _json_stdout:
        for r in records:
            # 精简行统一带 mode 字段：多模式串联（unpack→inspect→list-images）+ --json 时，
            # stdout 上多段 JSON 按 mode 自描述，无拼接歧义
            slim = {"mode": "inspect", **{k: r.get(k) for k in base_fields}}
            print(json.dumps(slim, ensure_ascii=False, separators=(",", ":")))


def _attrs_marks(a: dict) -> list:
    """将 attrs 中的异常/处置标记转为 JSON 结构化 key 列表。

    mark 集合（跨页/动图/小图/缩略图/超大页/旋转跨页）+ 汇总（异常/推断）
    + 性质（多余/封面/封面补位）+ 处置（舍弃）。
    """
    ms = []
    if a.get("anom"):
        ms.append("anom")
    for k in ("double", "animated", "small", "thumbnail", "overscale", "rotated_double"):
        if k in a.get("mark", ()):
            ms.append(k)
    if a.get("inferred"):
        ms.append("inferred")
    if a.get("extra"):
        ms.append("extra")
    if a.get("cover"):
        ms.append("cover")
    if a.get("cover_extra"):
        ms.append("cover_extra")
    if a.get("extra_dropped"):
        ms.append("dropped")
    if a.get("drop_small_hit"):
        ms.append("drop_small")
    return ms


def _build_list_record(source: str, attrs_list: list[dict], has_toc: bool) -> dict:
    """由 --list-images 的 attrs_list 构建 JSON 文件级记录。

    含图片明细（images）与文件级统计（stats），供 _emit_list_json 输出。
    """
    images = []
    for a in attrs_list:
        zname = Path(a.get("zname", "")).name if a.get("zname") else None
        images.append({
            "name": Path(a.get("path", "")).name if a.get("path") else zname,
            "w": a.get("w"), "h": a.get("h"),
            "size": a.get("size"),
            "mode": a.get("mode"), "depth": a.get("depth"),
            "dir": a.get("dir"),
            "toc": a.get("toc"),
            "extra": bool(a.get("extra") or a.get("cover_extra")),
            "cover": bool(a.get("cover") or a.get("cover_extra")),
            "dropped": bool(a.get("extra_dropped") or a.get("drop_small_hit")),
            "marks": _attrs_marks(a),
        })
    stats = {
        "total": len(attrs_list),
        "double": sum(1 for a in attrs_list if "double" in a.get("mark", ())),
        "animated": sum(1 for a in attrs_list if "animated" in a.get("mark", ())),
        "small": sum(1 for a in attrs_list if "small" in a.get("mark", ())),
        "extra": sum(1 for a in attrs_list if a.get("extra") or a.get("cover_extra")),
        "dropped": sum(1 for a in attrs_list if a.get("extra_dropped") or a.get("drop_small_hit")),
    }
    return {"source": source, "ext": Path(source).suffix.lower().lstrip("."),
            "has_toc": bool(has_toc), "images": images, "stats": stats}


def _emit_list_json(records: list, total_elapsed: float) -> None:
    """--list-images JSON 输出：stdout 精简版（每文件一行）、--json-out 落盘全量。

    精简字段：mode/source/ext/pages/double/animated/small/extra/dropped/toc；
    全量字段在精简基础上追加 files[].images 图片明细。"""
    if _json_out_path:
        summary = {
            "files": len(records),
            "pages": sum(r["stats"]["total"] for r in records),
            "double": sum(r["stats"]["double"] for r in records),
            "animated": sum(r["stats"]["animated"] for r in records),
            "small": sum(r["stats"]["small"] for r in records),
            "extra": sum(r["stats"]["extra"] for r in records),
            "dropped": sum(r["stats"]["dropped"] for r in records),
        }
        payload = {
            "version": __version__,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "mode": "list-images",
            "summary": summary,
            "files": records,
        }
        out_p = Path(_json_out_path)
        try:
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with out_p.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            emit(t("json.written", path=out_p), level="summary")
        except Exception as e:
            emit(t("error.json_write_failed", err=e, path=out_p), level="error")
    if _json_stdout:
        for r in records:
            slim = {
                "mode": "list-images",
                "source": r["source"],
                "ext": r["ext"],
                "pages": r["stats"]["total"],
                "double": r["stats"]["double"],
                "animated": r["stats"]["animated"],
                "small": r["stats"]["small"],
                "extra": r["stats"]["extra"],
                "dropped": r["stats"]["dropped"],
                "toc": r["has_toc"],
            }
            print(json.dumps(slim, ensure_ascii=False, separators=(",", ":")))


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


# 双页检测默认阈值：图片宽/高 >= 该值判为跨页（ComicInfo 标准推荐 2.0）
DEFAULT_DOUBLE_PAGE_RATIO = 2.0


def _parse_double_page_arg(s: str) -> float | None:
    """--double-page 参数值解析：off/no/0/false → None（关闭）；auto 或数值 → 阈值。

    数值必须 > 0；非法值抛 ArgumentTypeError 由 argparse 统一报错。
    """
    v = (s or "").strip().lower()
    if v in ("off", "no", "0", "false", "none"):
        return None
    if v in ("auto", ""):
        return DEFAULT_DOUBLE_PAGE_RATIO
    try:
        ratio = float(v)
    except ValueError:
        raise argparse.ArgumentTypeError(t("error.double_page_invalid", value=s))
    if ratio <= 0:
        raise argparse.ArgumentTypeError(t("error.double_page_invalid", value=s))
    return ratio


# 丢弃小图默认比例：宽和高均 < 中位数×该值 判为小图（封面缩略图等杂图）
DEFAULT_DROP_SMALL_RATIO = 0.5

# --list-images 异常尺寸增强判定参数：
#   超大页 = 宽或高 ≥ 中位数×LIST_OVERSCALE_RATIO（1.3）；
#   疑似旋转跨页 = 超大页 且 宽<高 且 (宽/高 − 中位比) ≥ LIST_RATIO_DELTA（0.08）
#   （旋转跨页被旋转 90° 存储：宽<高但宽高比明显变方，普通页 ~0.65 → 异常 ~0.75）
LIST_OVERSCALE_RATIO = 1.3
LIST_RATIO_DELTA = 0.08


def _parse_drop_small_arg(s: str) -> float | None:
    """--drop-small 参数值解析：off/no/0/false → None（关闭）；auto 或数值 → 比例。

    数值须在 (0, 1]；非法值抛 ArgumentTypeError 由 argparse 统一报错。
    """
    v = (s or "").strip().lower()
    if v in ("off", "no", "0", "false", "none"):
        return None
    if v in ("auto", ""):
        return DEFAULT_DROP_SMALL_RATIO
    try:
        ratio = float(v)
    except ValueError:
        raise argparse.ArgumentTypeError(t("error.drop_small_invalid", value=s))
    if not (0 < ratio <= 1):
        raise argparse.ArgumentTypeError(t("error.drop_small_invalid", value=s))
    return ratio


def _median_area(dims: list) -> float:
    """中位面积（宽×高 的中位数），小图判定统一面积口径。"""
    return statistics.median(d[0] * d[1] for d in dims)


def drop_small_images(images: list[Path], ratio: float) -> tuple[list[Path], list[str]]:
    """丢弃尺寸明显偏小的图片：面积（宽×高）< 中位面积×ratio 判为小图（--drop-small）。

    面积口径与 [小图] 标记 / --inspect 预览 / --list-images 的 drop_small_hit 统一；
    保持原顺序返回保留列表；无法解析尺寸的图片一律保留（不误删）。
    返回 (保留列表, 被丢弃文件名列表)。
    """
    if len(images) < 2:
        return images, []
    dims = [image_dimensions(img) for img in images]
    valid = [d for d in dims if d]
    if not valid:
        return images, []
    med_area = _median_area(valid)
    kept, dropped = [], []
    for img, d in zip(images, dims):
        if d and d[0] * d[1] < med_area * ratio:
            dropped.append(img)
        else:
            kept.append(img)
    return kept, [p.name for p in dropped]


# ============================================================
# 通用过滤表达式引擎（--list-images FILTER 与 --drop-extra 共用）
# 词表：格式(裸扩展名) / extra(多余图) / res<N|>N / size<N|>N(带bkmg后缀) /
#       landscape|portrait|square(方向) / gray|rgb|index|graya|rgba(模式) /
#       8bit|16bit|24bit|32bit(位深) / cover|double|animated|thumbnail|small(标记)
# 组合：逗号=OR，'+'=AND（如 gif+res<200 = 同时满足才命中）
# ============================================================
import unicodedata  # CJK 显示宽度（列对齐），重复 import 无副作用

_EXT_WORDS = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff", "tif"}
_CLOSE_WORDS = {"off", "no", "0", "false", "none"}
_NUM_SUFFIX = {"b": 1, "k": 1024, "m": 1024 ** 2, "g": 1024 ** 3}


def _parse_num_token(s: str) -> int | None:
    """解析带 b/k/m/g 后缀的数字（50k/10m/200b/1mb/1gb），非法返回 None。
    双字母后缀（kb/mb/gb）中字母 b 为非捕获可选位，组仅捕获单字母，
    _NUM_SUFFIX 无需扩展即可命中 k/m/g。"""
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([kmg]?)(?:b)?", s.strip().lower())
    if not m:
        return None
    return int(float(m.group(1)) * _NUM_SUFFIX[m.group(2) or "b"])


# 多语言筛选别名表：四语（简中/繁中/日文/英文）别名 → 规范原子元组。
# 允许直接粘贴展示标签写法（[封面] 等，解析时剥掉方括号）；英文规范词
# 保持原样兼容。name= 文件名筛选、ext/位深/res/size 走 _parse_atom 其余分支。
_ATOM_ALIASES = {
    # —— 标记类（mark）——
    "cover": ("mark", "cover"), "封面": ("mark", "cover"), "表紙": ("mark", "cover"),
    "double": ("mark", "double"), "双页": ("mark", "double"), "雙頁": ("mark", "double"),
    "見開き": ("mark", "double"),
    "animated": ("mark", "animated"), "动图": ("mark", "animated"), "動圖": ("mark", "animated"),
    "アニメ": ("mark", "animated"),
    "thumbnail": ("mark", "thumbnail"), "thumb": ("mark", "thumbnail"),
    "疑似缩略图": ("mark", "thumbnail"), "疑似縮圖": ("mark", "thumbnail"),
    "縮小サムネ": ("mark", "thumbnail"), "サムネイル": ("mark", "thumbnail"),
    # 注：small（异常小图）已升级为独立带参条件词（('small', ratio|None)），
    #     支持 small[=比例] 与多语言别名带参（异常小图=0.6 / 極小画像 等），见 _parse_atom。
    # —— 多余 / 处置标记（非属性，按 attrs 处置状态求值）——
    "extra": ("extra",), "多余": ("extra",), "多餘": ("extra",), "余分": ("extra",),
    "filter": ("mark", "filter"), "filtered": ("mark", "filter"),
    "筛选": ("mark", "filter"), "篩選": ("mark", "filter"), "フィルタ": ("mark", "filter"),
    "append": ("mark", "append"), "追加": ("mark", "append"),
    "drop": ("mark", "drop"), "舍弃": ("mark", "drop"), "捨棄": ("mark", "drop"),
    "破棄": ("mark", "drop"),
    # —— 方向类（dir）——
    "landscape": ("dir", "landscape"), "横向": ("dir", "landscape"), "橫向": ("dir", "landscape"),
    "横向き": ("dir", "landscape"),
    "portrait": ("dir", "portrait"), "纵向": ("dir", "portrait"), "縱向": ("dir", "portrait"),
    "縦向き": ("dir", "portrait"),
    "square": ("dir", "square"), "方形": ("dir", "square"), "正方形": ("dir", "square"),
    # —— 模式类（mode）——
    "gray": ("mode", "gray"), "灰度": ("mode", "gray"), "グレー": ("mode", "gray"),
    "graya": ("mode", "graya"), "灰度a": ("mode", "graya"), "gray+alpha": ("mode", "graya"),
    "rgb": ("mode", "rgb"), "rgba": ("mode", "rgba"),
    "index": ("mode", "index"), "索引": ("mode", "index"), "インデックス": ("mode", "index"),
    # —— 异常尺寸标签（overscale / rotated_double / anom，依赖 attrs 增强字段）——
    "overscale": ("mark", "overscale"), "超大页": ("mark", "overscale"),
    "超大頁": ("mark", "overscale"), "特大ページ": ("mark", "overscale"),
    "巨大ページ": ("mark", "overscale"),
    "rotated_double": ("mark", "rotated_double"), "疑似旋转跨页": ("mark", "rotated_double"),
    "疑似旋轉跨頁": ("mark", "rotated_double"), "回転見開き": ("mark", "rotated_double"),
    "縦向き見開き": ("mark", "rotated_double"),
    "anom": ("mark", "anom"), "anomaly": ("mark", "anom"),
    "异常": ("mark", "anom"), "異常": ("mark", "anom"),
    # —— 推断性标记（inferred，独立维度：旋转跨页 / 缩略图 / 封面补位等）——
    "inferred": ("mark", "inferred"), "推断": ("mark", "inferred"), "推斷": ("mark", "inferred"),
    "推測": ("mark", "inferred"), "推定": ("mark", "inferred"),
}


def _parse_atom(atom: str):
    """解析单个条件词 → 原子元组；无法识别返回 None。
    原子: ('extra',) ('ext',fmt) ('mode',m) ('depth',n) ('dir',d)
          ('mark',m) ('res',op,n) ('size',op,n) ('name',kw) ('small',ratio|None)
    small 为独立带参条件词：无参/auto=默认比例（None→0.5），可带比例 0<r<=1；
    多语言别名通用（异常小图/異常小圖/異常小画像/極小画像 均可带参）。
    支持多语言别名与 [标签] 方括号写法（见 _ATOM_ALIASES）。"""
    al = atom.strip().strip("[]").lower()
    if not al:
        return None
    # '-' 前缀 = 取反（排除满足该条件的图片，如 -gif / -webp）：
    # 递归解析内层原子并包装为 ("neg", 内层原子)；'-' 单独或 '--' 开头视为非法
    if al.startswith("-"):
        inner = al[1:]
        if not inner or inner.startswith("-"):
            raise argparse.ArgumentTypeError(t("error.filter_token", token=atom, expr=atom))
        core = _parse_atom(inner)
        if core is None:
            raise argparse.ArgumentTypeError(t("error.filter_token", token=atom, expr=atom))
        return ("neg", core)
    # small 独立条件词：无参=默认比例（None→0.5），可带比例 0<r<=1；多语言别名通用
    sm = re.fullmatch(r"(small|異常小圖|异常小图|異常小画像|極小画像)(?:=(.+))?", al)
    if sm:
        val = sm.group(2)
        if val is None or val.lower() in ("auto", "on"):
            return ("small", None)
        try:
            r = float(val)
        except ValueError:
            raise argparse.ArgumentTypeError(t("error.drop_small_invalid", value=val))
        if not 0 < r <= 1:
            raise argparse.ArgumentTypeError(t("error.drop_small_invalid", value=val))
        return ("small", r)
    hit = _ATOM_ALIASES.get(al)
    if hit is not None:
        return hit
    # 按文件名关键词筛选：name=关键词（文件名含关键词即命中，不区分大小写）
    m = re.fullmatch(r"name=(.+)", al)
    if m and m.group(1):
        return ("name", m.group(1))
    if al in _EXT_WORDS:
        return ("ext", "jpg" if al == "jpeg" else al)
    if al in ("8bit", "16bit", "24bit", "32bit"):
        return ("depth", int(al.replace("bit", "")))
    m = re.fullmatch(r"(res|size)([<>])(\d+(?:\.\d+)?(?:[kmg]?b?))", al)
    if m:
        n = _parse_num_token(m.group(3))
        if n is not None:
            return (m.group(1), m.group(2), n)
    return None


def parse_drop_expr(value: str | None):
    """解析过滤表达式（--list-images FILTER / --drop-extra 共用）。
    逗号=OR，'+'=AND。返回条件组列表 [[atom,...],...]；
    None/空/off 词 → None（不过滤）。非法 token 抛 ArgumentTypeError。"""
    if value is None:
        return None
    v = value.strip()
    if not v or v.lower() in _CLOSE_WORDS:
        return None
    groups = []
    for part in v.split(","):
        part = part.strip()
        if not part:
            continue
        atoms = []
        for atom in part.split("+"):
            a = _parse_atom(atom)
            if a is None:
                raise argparse.ArgumentTypeError(t("error.filter_token", token=atom, expr=value))
            atoms.append(a)
        if atoms:
            groups.append(atoms)
    return groups or None


def extract_small_ratio(drop_expr) -> float | None:
    """从丢弃/过滤表达式提取 small 条件比例；无 small 条件返回 None。

    small 无参（('small', None)）返回默认比例 DEFAULT_DROP_SMALL_RATIO，
    带参返回其比例。供 list/inspect/转换三链路统一小图口径（面积判定共用）。"""
    if not drop_expr:
        return None
    for grp in drop_expr:
        for a in grp:
            if a[0] == "small":
                return a[1] if a[1] is not None else DEFAULT_DROP_SMALL_RATIO
    return None


def parse_inspect_arg(value: str | None):
    """解析 --inspect 参数 → (mode, filter)。

    值域混合解析：逗号切分后，sample/all 提取为检查范围 MODE（缺省 sample），
    其余 token 进 parse_drop_expr 作为 FILTER（None 表示无过滤）。
    例：all,small=0.6 → ('all', [[('small',0.6),],])；small → ('sample', [[('small',None),],])；
        off → ('sample', None)。非法 token 抛 ArgumentTypeError。"""
    if value is None:
        return "sample", None
    v = value.strip()
    if not v:
        return "sample", None
    mode = None
    rest = []
    for token in v.split(","):
        t = token.strip()
        if t == "sample" or t == "all":
            mode = t
        else:
            rest.append(t)
    if not rest:
        return (mode if mode else "sample"), None
    return (mode if mode else "sample"), parse_drop_expr(",".join(rest))


def image_mode_bytes(head: bytes):
    """从图片头部 bytes 解析 (模式, 每像素位深)；失败返回 None。
    模式 gray/rgb/index/graya/rgba（对齐 PNG IHDR color type 语义，
    JPEG/GIF/WebP/BMP 归并到同一组）。零依赖纯字节解析。"""
    try:
        if head.startswith(b"\x89PNG\r\n\x1a\n") and len(head) >= 26:
            bit = head[24]
            ct = head[25]
            if ct == 0:
                return "gray", bit
            if ct == 2:
                return "rgb", bit * 3
            if ct == 3:
                return "index", bit
            if ct == 4:
                return "graya", bit * 2
            if ct == 6:
                return "rgba", bit * 4
            return None
        if head.startswith(b"\xff\xd8"):
            # JPEG: SOF 段 精度(1B)+高(2B)+宽(2B)+分量数(1B)
            pos = 2
            while pos + 9 < len(head):
                if head[pos] != 0xFF:
                    pos += 1
                    continue
                marker = head[pos + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                              0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    precision = head[pos + 4]
                    comps = head[pos + 9]
                    return ("gray" if comps == 1 else "rgb"), precision * (1 if comps == 1 else 3)
                if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                    pos += 2
                else:
                    seg_len = struct.unpack(">H", head[pos + 2:pos + 4])[0]
                    pos += 2 + seg_len
            return None
        if head.startswith(b"GIF8"):
            return "index", 8
        if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
            if head[12:16] == b"VP8L":
                return "rgba", 32
            if head[12:16] in (b"VP8 ", b"VP8X"):
                return "rgb", 24
            return None
        if head.startswith(b"BM") and len(head) >= 30:
            bpp = struct.unpack("<H", head[28:30])[0]
            if bpp >= 32:
                return "rgba", bpp
            if bpp == 24:
                return "rgb", 24
            return "index", bpp or 8
        return None
    except Exception:
        return None


def gif_frame_count(head: bytes) -> int:
    """GIF 帧数：按 GIF 结构块解析图像描述符（0x2C）计数，非 GIF 返回 0。

    不依赖 PIL：头部为 6B 签名 + 7B 逻辑屏幕描述符 + 可选全局色表，
    之后为数据块流。LZW 压缩数据按子块边界整体跳过（不扫描内容），
    避免压缩数据内任意 0x2C 字节被误判为帧。head 截断时安全退出，
    返回已计数的帧数（单帧静态 GIF 恒为 1，不会误标动画）。
    """
    if not head.startswith(b"GIF8") or len(head) < 13:
        return 0
    packed = head[10]
    pos = 13
    if packed & 0x80:                      # 全局色表：3 × 2^(N+1)
        pos += 3 * (2 << (packed & 0x07))
    frames = 0
    while pos + 1 < len(head):
        block = head[pos]
        if block == 0x2C:                  # 图像描述符 = 一帧
            frames += 1
            if pos + 10 > len(head):       # 描述符未读全，截断
                break
            p2 = head[pos + 9]
            pos += 10 + (3 * (2 << (p2 & 0x07)) if p2 & 0x80 else 0)  # +局部色表
            if pos >= len(head):
                break
            pos += 1                       # LZW 最小码长
            while pos < len(head):         # 子块流，按边界跳过
                sub = head[pos]
                pos += 1
                if sub == 0:
                    break
                if pos + sub > len(head):  # 截断，停止解析
                    pos = len(head)
                    break
                pos += sub
        elif block == 0x21:                # 扩展块：label + 子块流
            pos += 1
            if pos >= len(head):
                break
            pos += 1                       # label
            while pos < len(head):
                sub = head[pos]
                pos += 1
                if sub == 0:
                    break
                if pos + sub > len(head):
                    pos = len(head)
                    break
                pos += sub
        elif block == 0x3B:                # 尾部
            break
        else:                              # 未知块，防御性退出
            break
    return frames


def disp_width(s: str) -> int:
    """字符串显示宽度：CJK/全角计 2、其余计 1（终端等宽对齐）。"""
    w = 0
    for ch in s:
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def pad_wide(s: str, width: int) -> str:
    """按显示宽度右侧补空格到 width（ANSI 色码不计入宽度）。"""
    return s + " " * max(0, width - disp_width(_strip_ansi(s)))


def trunc_wide(s: str, max_w: int) -> str:
    """按显示宽度截断，超长末尾加英文省略号 '...'。"""
    if disp_width(s) <= max_w:
        return s
    out, w = "", 0
    for ch in s:
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if w + cw > max_w - 3:
            break
        out += ch
        w += cw
    return out + "..."


def eval_filter_atoms(attrs: dict, atoms) -> bool:
    """AND 组：全部原子命中才 True（组内 '+' 语义）。"""
    for a in atoms:
        if not eval_filter_atom(attrs, a):
            return False
    return True


def eval_filter_atom(attrs: dict, a) -> bool:
    # ("neg", 内层原子)：取反语义（ATOM_ALIASES 中无 neg 键冲突）
    if a[0] == "neg":
        return not eval_filter_atom(attrs, a[1])
    t = a[0]
    if t == "extra":
        # 与 _mark_strs 的 [多余] 展示一致：封面补位图也计入
        return bool(attrs.get("extra") or attrs.get("cover_extra"))
    if t == "ext":
        return attrs.get("ext") == a[1]
    if t == "mode":
        return attrs.get("mode") == a[1]
    if t == "depth":
        return attrs.get("depth") == a[1]
    if t == "dir":
        return attrs.get("dir") == a[1]
    if t == "small":
        # small 独立条件词：读取 _fill_small_mark 按面积口径预填的 small_hit（True=小图）
        return bool(attrs.get("small_hit"))
    if t == "mark":
        m = a[1]
        if m == "cover":
            # 封面补位图（cover_extra）与 spine 内封面均可命中
            return bool(attrs.get("cover") or attrs.get("cover_extra"))
        if m == "filter":
            return bool(attrs.get("filter_hit"))
        if m == "drop":
            return attrs.get("disposition") == "drop"
        if m == "append":
            return attrs.get("disposition") == "append"
        if m == "overscale":
            return "overscale" in (attrs.get("mark") or set())
        if m == "rotated_double":
            return "rotated_double" in (attrs.get("mark") or set())
        if m == "anom":
            # 汇总标签：任一异常标记命中即算
            return bool(attrs.get("anom"))
        if m == "inferred":
            # 推断性标记：旋转跨页 / 缩略图 / 封面补位等
            return bool(attrs.get("inferred"))
        return m in (attrs.get("mark") or set())
    if t == "name":
        # 按文件名关键词子串匹配（不区分大小写），只匹配纯文件名（zname/path 均归一为文件名）
        nm = str(attrs.get("zname") or attrs.get("path") or "").replace("\\", "/")
        return a[1] in nm.rsplit("/", 1)[-1].lower()
    if t == "res":
        w, h = attrs.get("w"), attrs.get("h")
        if w is None or h is None:
            return False
        if a[1] == "<":
            return min(w, h) < a[2]  # 宽或高任一 < N 即命中
        return max(w, h) > a[2]      # 宽或高任一 > N 即命中
    if t == "size":
        sz = attrs.get("size")
        if sz is None:
            return False
        return sz < a[2] if a[1] == "<" else sz > a[2]
    return False


def _fill_small_mark(attrs_list: list[dict], ratio: float | None) -> None:
    """按全集中位面积回填小图标记与 small_hit 字段（宽×高 < 中位面积×比例）。

    面积口径：与 --drop-small / --drop small 判定（drop_small_hit / drop_small_images /
    --inspect 预览）统一同一比例；ratio 为 None 时不标，保证"标了即会丢"：
    有 [小图] 标记的图必被丢弃。small 独立条件词经 eval_filter_atom 读 small_hit 求值，
    因此 _parse_atom 产出 ('small',...) 原子后，此处预填 small_hit 即完成口径统一。"""
    if ratio is None:
        return
    dims = [(a["w"], a["h"]) for a in attrs_list if a.get("w") and a.get("h")]
    if not dims:
        return
    med_area = _median_area(dims)
    for a in attrs_list:
        if a.get("w") and a.get("h") and a["w"] * a["h"] < med_area * ratio:
            a["mark"].add("small")
            a["small_hit"] = True


def _fill_overscale_mark(attrs_list: list[dict]) -> None:
    """按全集中位数回填超大页/旋转跨页标记与异常汇总。

    overscale      = 宽或高 ≥ 中位×LIST_OVERSCALE_RATIO（默认 1.3）
    rotated_double = overscale 且 宽<高 且 (宽/高 − 中位宽高比) ≥ LIST_RATIO_DELTA（默认 0.08）
                     —— 纵向存储的旋转跨页，宽高比明显变方
    rotated_double / thumbnail 属推断性标记，同时置 a['inferred']=True
    （[推断] 独立标记）；封面页尺寸异常不豁免，照标异常并叠加 [封面] 标签；
    a['anom'] 汇总任一异常标记。"""
    dims = [(a["w"], a["h"]) for a in attrs_list if a.get("w") and a.get("h")]
    for a in attrs_list:
        a["anom"] = False
        a.setdefault("inferred", False)
    if not dims:
        return
    med_w = statistics.median(d[0] for d in dims)
    med_h = statistics.median(d[1] for d in dims)
    ratios = [d[0] / d[1] for d in dims if d[1]]
    med_ratio = statistics.median(ratios) if ratios else None
    for a in attrs_list:
        w, h = a.get("w"), a.get("h")
        if not (w and h):
            continue
        if w >= med_w * LIST_OVERSCALE_RATIO or h >= med_h * LIST_OVERSCALE_RATIO:
            a["mark"].add("overscale")
            if w < h and med_ratio and (w / h - med_ratio) >= LIST_RATIO_DELTA:
                a["mark"].add("rotated_double")
                a["inferred"] = True
        # 封面补位（cover_extra）仅"不在 spine 的多余图"，非尺寸异常，不计入 anom；
        # 尺寸异常的封面（overscale 等）走 mark 判定，自然计入。
        if ("overscale" in a["mark"] or "rotated_double" in a["mark"]
                or "small" in a["mark"] or "thumbnail" in a["mark"]
                or "animated" in a["mark"] or a.get("extra")):
            a["anom"] = True


def build_image_attrs(path: Path, double_ratio: float | None) -> dict:
    """从解包目录中的真实图片文件构建属性 dict（--list-images 用）。"""
    attrs = {"path": path, "zname": None, "ext": path.suffix.lower().lstrip("."),
             "w": None, "h": None, "mode": None, "depth": None, "size": None,
             "dir": None, "mark": set(), "extra": False, "toc": "", "dropped": None,
             "frames": 0, "inferred": False}
    if attrs["ext"] == "jpeg":
        attrs["ext"] = "jpg"
    try:
        attrs["size"] = path.stat().st_size
    except OSError:
        attrs["size"] = None
    try:
        with open(path, "rb") as f:
            head = f.read(HEAD_READ_BYTES)
    except Exception:
        head = b""
    dim = image_dimensions_bytes(head)
    if dim:
        w, h = dim
        attrs["w"], attrs["h"] = w, h
        attrs["dir"] = "landscape" if w > h else ("portrait" if h > w else "square")
        if double_ratio is not None and h > 0 and w / h >= double_ratio:
            attrs["mark"].add("double")
        if w < 200 or h < 200:
            attrs["mark"].add("thumbnail")
            attrs["inferred"] = True
    mode = image_mode_bytes(head)
    if mode:
        attrs["mode"], attrs["depth"] = mode
    attrs["frames"] = gif_frame_count(head)
    if attrs["frames"] > 1:
        attrs["mark"].add("animated")
    return attrs


def build_cbz_image_attrs(zf, name: str, double_ratio: float | None) -> dict:
    """从 CBZ zip 内条目构建属性 dict（不落盘，读条目头 bytes）。"""
    attrs = {"path": None, "zname": name, "ext": Path(name).suffix.lower().lstrip("."),
             "w": None, "h": None, "mode": None, "depth": None, "size": None,
             "dir": None, "mark": set(), "extra": False, "toc": "", "dropped": None,
             "frames": 0}
    if attrs["ext"] == "jpeg":
        attrs["ext"] = "jpg"
    try:
        attrs["size"] = zf.getinfo(name).file_size
    except Exception:
        attrs["size"] = None
    try:
        with zf.open(name) as f:
            head = f.read(HEAD_READ_BYTES)
    except Exception:
        head = b""
    dim = image_dimensions_bytes(head)
    if dim:
        w, h = dim
        attrs["w"], attrs["h"] = w, h
        attrs["dir"] = "landscape" if w > h else ("portrait" if h > w else "square")
        if double_ratio is not None and h > 0 and w / h >= double_ratio:
            attrs["mark"].add("double")
        if w < 200 or h < 200:
            attrs["mark"].add("thumbnail")
            attrs["inferred"] = True
    mode = image_mode_bytes(head)
    if mode:
        attrs["mode"], attrs["depth"] = mode
    attrs["frames"] = gif_frame_count(head)
    if attrs["frames"] > 1:
        attrs["mark"].add("animated")
    return attrs


# ============================================================
# --list-images：图片清单 + 目录标注 + 全量统计（EPUB/MOBI/CBZ）
# 与转换链路共享同一套过滤表达式引擎（--drop-extra 同源）
# ============================================================
def _atom_text(a) -> str:
    """原子条件 → 人类可读词（用于舍弃明细描述）。"""
    if a[0] == "neg":
        return "-" + _atom_text(a[1])
    t0 = a[0]
    if t0 == "extra":
        return "extra"
    if t0 == "ext":
        return a[1]
    if t0 == "mode":
        return a[1]
    if t0 == "depth":
        return f"{a[1]}bit"
    if t0 == "dir":
        return a[1]
    if t0 == "mark":
        return a[1]
    if t0 == "res":
        return f"res{a[1]}{a[2]}"
    if t0 == "size":
        return f"size{a[1]}{a[2]}"
    return str(a)


def _dropped_desc(expr, attrs: dict) -> str | None:
    """命中 expr 任一 OR 组时返回命中条件描述（AND 组用 + 连接）；未命中返回 None。"""
    if not expr:
        return None
    for g in expr:
        if eval_filter_atoms(attrs, g):
            return " + ".join(_atom_text(a) for a in g)
    return None


def _resolve_toc_href_to_image(anchor_dir: Path, href: str, base_dir: Path):
    """目录条目 href → 图片路径。href 相对 NCX/nav 所在目录解析。

    直接指向图片 → 返回该图片；指向 xhtml/html → 解析其中第一个 <img src>。
    解析失败返回 None。"""
    if not href:
        return None
    clean = href.split("#", 1)[0]
    if not clean:
        return None
    cand = (anchor_dir / clean).resolve()
    if not cand.exists():
        alt = (base_dir / clean).resolve()
        if alt.exists():
            cand = alt
    if not cand.is_file():
        return None
    if cand.suffix.lower() in IMAGE_EXTENSIONS:
        return cand
    if cand.suffix.lower() in (".xhtml", ".html", ".htm"):
        try:
            txt = cand.read_text("utf-8", errors="replace")
            m = re.search(r'<img\b[^>]*src=["\']([^"\']+)["\']', txt, re.I)
            if m:
                sub = m.group(1).split("#", 1)[0]
                subp = (cand.parent / sub).resolve()
                if subp.is_file() and subp.suffix.lower() in IMAGE_EXTENSIONS:
                    return subp
        except Exception:
            return None
    return None


def parse_ncx_entries(base_dir: Path):
    """解析 toc.ncx 全部条目（标题 + content src + 嵌套深度）。

    用栈扫描 navPoint 开/闭建树、再按文档顺序先序遍历输出：父条目
    恒在子条目之前、同层保持文档顺序；深度 1 为顶层。
    标题剥离嵌套标签并解码 HTML 实体（&amp; → &）。
    返回 (entries, ncx_path)；entries 元素为 (title, href, depth)。"""
    ncx = find_ncx(base_dir)
    if ncx is None:
        return [], None
    try:
        text = ncx.read_text("utf-8", errors="replace")
    except Exception:
        return [], None
    root = []
    stack = []
    for m in re.finditer(r"<navPoint\b|</navPoint>", text, re.I):
        if m.group(0).lower().startswith("<navpoint"):
            stack.append((m.end(), {"title": None, "href": None, "children": []}))
        else:
            if not stack:
                continue
            start, node = stack.pop()
            block = text[start:m.start()]
            tm = re.search(r"<text>(.*?)</text>", block, re.I | re.S)
            if tm:
                title = re.sub(r"<[^>]+>", "", tm.group(1))
                title = unescape(title).strip()
                node["title"] = title
            cm = re.search(r'<content\b[^>]*src=["\']([^"\']+)["\']', block, re.I)
            node["href"] = cm.group(1) if cm else None
            parent = stack[-1][1] if stack else None
            (parent["children"] if parent else root).append(node)
    entries = []

    def walk(nodes, depth):
        for node in nodes:
            if node["title"]:
                entries.append((node["title"], node["href"], depth))
            walk(node["children"], depth + 1)

    walk(root, 1)
    return entries, ncx


def parse_nav_entries(base_dir: Path):
    """解析 EPUB3 nav 目录条目（标题 + href）。

    优先从 OPF manifest properties="nav" 定位 nav 文档，兜底按 *nav*.xhtml 搜索；
    取 <nav epub:type="toc"> 内全部 <a>（含多级嵌套展开）。
    返回 (entries, nav_path)；entries 元素为 (title, href)。"""
    try:
        opf_path = find_opf(base_dir)
        nav = None
        if opf_path:
            tree = safe_et_parse(opf_path)
            root = tree.getroot()
            for item in root.findall(".//opf:manifest/opf:item", OPF_NS):
                if "nav" in (item.get("properties") or "").split():
                    href = item.get("href")
                    if href:
                        cand = (opf_path.parent / href.split("#", 1)[0]).resolve()
                        if cand.exists():
                            nav = cand
                            break
        if nav is None:
            for f in base_dir.rglob("*.xhtml"):
                if "nav" in f.stem.lower():
                    nav = f
                    break
        if nav is None:
            return [], None
        text = nav.read_text("utf-8", errors="replace")
        nav_blocks = re.findall(r"<nav\b[^>]*>.*?</nav>", text, re.I | re.S)
        block = None
        for nb in nav_blocks:
            if re.search(r"epub:type\s*=\s*[\"']toc[\"']", nb, re.I):
                block = nb
                break
        if block is None and nav_blocks:
            block = nav_blocks[0]
        if block is None:
            return [], None
        entries = []
        for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', block, re.I | re.S):
            title = re.sub(r"<[^>]+>", "", m.group(2))
            title = unescape(title).strip()
            if title:
                entries.append((title, m.group(1)))
        return entries, nav
    except Exception:
        return [], None


def build_toc_maps(base_dir: Path):
    """构建目录 → 图片映射。

    返回 (ncx_map, nav_map, has_ncx, has_nav)：
    - ncx_map: norm_path -> (title, depth)，同来源一图多条目保留 depth 最大（最具体）
    - nav_map: norm_path -> title
    - has_ncx/has_nav: 该来源是否存在条目（决定双目录合并加前缀与否）"""
    ncx_map, nav_map = {}, {}
    entries, ncx = parse_ncx_entries(base_dir)
    if ncx:
        anchor = ncx.parent
        for title, href, depth in entries:
            img = _resolve_toc_href_to_image(anchor, href or "", base_dir)
            if img is None:
                continue
            key = norm_path(img)
            if key not in ncx_map or depth > ncx_map[key][1]:
                ncx_map[key] = (title, depth)
    entries, nav = parse_nav_entries(base_dir)
    if nav:
        anchor = nav.parent
        for title, href in entries:
            img = _resolve_toc_href_to_image(anchor, href or "", base_dir)
            if img is None:
                continue
            key = norm_path(img)
            if key not in nav_map:
                nav_map[key] = title
    return ncx_map, nav_map, bool(ncx_map), bool(nav_map)


def toc_label_for(norm: str, ncx_map: dict, nav_map: dict, multi_src: bool) -> str:
    """单图目录列：双目录并存时按来源合并去重；单一来源不加前缀。"""
    hits = []
    if norm in ncx_map:
        hits.append(("NCX", ncx_map[norm][0]))
    if norm in nav_map:
        hits.append(("nav", nav_map[norm]))
    if not hits:
        return ""
    if not multi_src:
        return hits[0][1]
    seen, titles = set(), []
    for src, ti in hits:
        if ti not in seen:
            seen.add(ti)
            titles.append((src, ti))
    if len(titles) == 1:
        return titles[0][1]
    return " | ".join(f"[{src}] {ti}" for src, ti in titles)


def _list_filter_pass(attrs: dict, expr) -> bool:
    """FILTER 行筛选：无表达式全部显示；有表达式命中任一 OR 组显示。"""
    if expr is None:
        return True
    return any(eval_filter_atoms(attrs, g) for g in expr)


def _fmt_size(n: int | None) -> str:
    """文件大小显示：512.3 KB / 1.5 MB / 890 B；None → '?'"""
    if n is None:
        return "?"
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    if n < 1024 * 1024 * 1024:
        return f"{n / (1024 * 1024):.1f} MB"
    return f"{n / (1024 * 1024 * 1024):.1f} GB"


def _mode_str(mode: str | None, depth: int | None) -> str:
    """模式/色深列显示（英文规范名 + bit 深，跨语言统一）：index/gray/rgb/graya/rgba。"""
    if not mode:
        return "?"
    return f"{mode} {depth if depth else '?'}bit"


def _dir_str(d: str | None) -> str:
    return {"landscape": t("dir.landscape"), "portrait": t("dir.portrait"),
            "square": t("dir.square")}.get(d or "", "?")


# ---- ANSI 颜色（仅 TTY 控制台生效；管道/日志/JSON 永不上色）----
_color_enabled = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
_ANSI_RESET = "\x1b[0m"


def _c(code: int | None, s: str) -> str:
    """ANSI 前景色包裹（31-36）；未启用颜色或 code 为 None 时原样返回。"""
    if not _color_enabled or code is None:
        return s
    return f"\x1b[{code}m{s}{_ANSI_RESET}"


def _strip_ansi(s: str) -> str:
    """剥离 ANSI 转义序列（日志文件写入前调用，避免色码污染日志）。"""
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def _mark_color(key: str) -> int | None:
    """标记颜色映射：黄=可疑（多余/异常/小图/缩略图/筛选/超大页/推断），红=舍弃，绿=追加，青=中性（封面/跨页/动图）。"""
    if key in ("extra", "anom", "small", "thumbnail", "filter", "overscale", "rotated_double", "inferred"):
        return 33
    if key == "drop":
        return 31
    if key == "append":
        return 32
    if key in ("cover", "double", "animated"):
        return 36
    return None


def _mark_strs(attrs: dict, is_cbz: bool, drop_expr, drop_small: float | None) -> list[str]:
    """标记列文本列表（CBZ 模式排除处置标记）。

    性质与处置两维独立拼接，全部为独立标记：
      汇总：[异常] 首位恒显（overscale/rotated_double/small/thumbnail/animated/extra 任一）
      性质：[多余] 不在 spine 的图（含封面补位）/ [封面] / [小图] / [跨页] / [动图] /
            [缩略图] / [超大页] / [旋转跨页] / [筛选]（命中过滤表达式）
      推断：[推断] 独立标记（旋转跨页 / 缩略图 / 封面补位等推断性识别，替代原"疑似"前缀）
      处置（仅非 CBZ）：[追加] 保留进 CBZ / [舍弃] 将被丢弃
    有目录的图在目录列展示，此处不重复标 [目录]。TTY 下按标记类型上色。
    """
    keys: list[str] = []
    mark = attrs["mark"]
    # [异常] 汇总标记恒显于首位
    if attrs.get("anom"):
        keys.append("anom")
    # 性质标记
    if attrs.get("extra") or attrs.get("cover_extra"):
        keys.append("extra")          # 封面补位也是不在 spine 的图 → 标多余
    if attrs.get("cover") or attrs.get("cover_extra"):
        keys.append("cover")
    if "double" in mark:
        keys.append("double")
    if "thumbnail" in mark:
        keys.append("thumbnail")
    if "animated" in mark:
        keys.append("animated")
    if "small" in mark:
        keys.append("small")
    if "overscale" in mark:
        keys.append("overscale")
    if "rotated_double" in mark:
        keys.append("rotated_double")
    d = _dropped_desc(drop_expr, attrs) if drop_expr is not None else None
    if d and "extra" not in d:
        keys.append("filter")
    # [推断] 独立标记：旋转跨页 / 缩略图 / 封面补位等推断性识别
    if attrs.get("inferred"):
        keys.append("inferred")
    # 处置标记（仅非 CBZ；CBZ 为已转换产物无转换态）
    if not is_cbz:
        disp = attrs.get("disposition")
        if disp == "drop":
            keys.append("drop")
        elif disp == "append":
            keys.append("append")
    marks = [t(f"mark.{k}") for k in keys]
    if _color_enabled:
        return [_c(_mark_color(k), m) for k, m in zip(keys, marks)]
    return marks


def _render_stats(attrs_list: list[dict], has_toc: bool, extra_dropped: bool, drop_small: float | None = None) -> None:
    """统计块：恒全量（不受 FILTER 筛选影响）。

    drop_small 开启时追加小图阈值提示；--quiet 下输出 summary 级一行汇总，
    避免用户误以为没有扫描。
    """
    total = len(attrs_list)
    emit(t("list.total", n=total))
    # 格式分布
    fmt_c = Counter(a["ext"] for a in attrs_list)
    fmt_c = {k: v for k, v in fmt_c.items() if k}
    if fmt_c:
        parts = [f"{k.upper()} {v} ({v / total * 100:.1f}%)"
                 for k, v in sorted(fmt_c.items(), key=lambda x: -x[1])]
        emit(t("list.fmt", parts=" | ".join(parts)))
    # 模式/色深分布
    mode_c = Counter(_mode_str(a["mode"], a["depth"]) for a in attrs_list if a.get("mode"))
    if mode_c:
        parts = [f"{k} {v} ({v / total * 100:.0f}%)"
                 for k, v in sorted(mode_c.items(), key=lambda x: -x[1])]
        emit(t("list.mode", parts=" | ".join(parts)))
    # 尺寸分布
    res_c = Counter((a["w"], a["h"]) for a in attrs_list if a.get("w") and a.get("h"))
    if res_c:
        emit(t("list.res_title"))
        for (w, h), v in res_c.most_common(3):
            emit("  " + t("list.res_item", w=w, h=h, count=v, pct=f"{v / total * 100:.0f}"))
        rest = total - sum(v for (_, _), v in list(res_c.most_common(3)))
        if rest > 0:
            emit("  " + t("list.res_other", count=rest, pct=f"{rest / total * 100:.0f}") + t("list.res_other_note"))
    # 双页 / 动图 / 小图
    double_n = sum(1 for a in attrs_list if "double" in a["mark"])
    anim_n = sum(1 for a in attrs_list if "animated" in a["mark"])
    small_n = sum(1 for a in attrs_list if "small" in a["mark"])
    emit(t("list.double", n=double_n))
    emit(t("list.animated", n=anim_n))
    emit(t("list.small", n=small_n))
    if drop_small is not None:
        emit(t("list.drop_small_note", ratio=drop_small))
    # 异常图片明细（超大页 / 疑似旋转跨页 / 疑似缩略图 / 异常小图 / 动图 / 目录外）
    anoms = []
    for a in attrs_list:
        descs = []
        if "overscale" in a["mark"]:
            descs.append(t("anom.overscale"))
        if "rotated_double" in a["mark"]:
            descs.append(t("anom.rotated_double"))
        if "thumbnail" in a["mark"]:
            descs.append(t("anom.thumbnail"))
        if "small" in a["mark"]:
            descs.append(t("anom.small"))
        if "animated" in a["mark"]:
            descs.append(t("anom.animated", frames=a.get("frames", "?")))
        if a.get("extra"):
            descs.append(t("anom.extra_drop") if extra_dropped else t("anom.extra_append"))
        if descs:
            name = (Path(a["zname"]).name if a["zname"] else a["path"].name)
            dim = f"{a['w']}x{a['h']}" if a.get("w") and a.get("h") else "?"
            anoms.append((name, dim, ", ".join(descs)))
    if anoms:
        emit(t("list.anomaly", n=len(anoms)))
        for name, dim, desc in anoms:
            emit("  - " + t("list.anomaly_item", name=name, dim=dim, desc=desc))
    if _quiet_mode:
        emit(t("list.quiet_summary", n=total, anomalies=len(anoms)), level="summary")


def _render_table(rows: list[dict], has_toc: bool) -> None:
    """清单表格：按 CJK 显示宽度列对齐；目录列宽度上限 30，超长截断 '...'。"""
    headers = [t("list.col.no"), t("list.col.file"), t("list.col.res"), t("list.col.size"),
               t("list.col.mode"), t("list.col.dir")]
    if has_toc:
        headers.append(t("list.col.toc"))
    headers.append(t("list.col.mark"))
    cells = [[str(r["no"]), r["name"], r["res"], r["size"], r["mode"], r["dir"]] for r in rows]
    if has_toc:
        for i, r in enumerate(rows):
            cells[i].append(trunc_wide(r["toc"], 30))
    for i, r in enumerate(rows):
        cells[i].append(r["mark"])
    widths = [disp_width(h) for h in headers]
    for row in cells:
        for i, c in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], disp_width(_strip_ansi(c)))
    emit("  " + "  ".join(pad_wide(h, widths[i]) for i, h in enumerate(headers)))
    for row in cells:
        emit("  " + "  ".join(pad_wide(c, widths[i]) for i, c in enumerate(row)))


def _list_ebook(p: Path, args, double_ratio, list_expr) -> None:
    """EPUB/MOBI 单文件清单：复用转换链路（spine→封面→目录对齐→去重）+ 目录标注。"""
    emit(t("list.file_line", name=p.name))
    drop_expr = args.drop  # 统一丢弃表达式（条件组或 None）
    # 小图比例：清单表达式内 small 条件优先，其次 --drop 表达式
    small_ratio = extract_small_ratio(list_expr) or extract_small_ratio(drop_expr)
    tempdir = None  # 解包异常时保持 None，避免 finally 里 rmtree 引用未定义变量抛 NameError
    try:
        if p.suffix.lower() == ".epub":
            tempdir = extract_epub_to_temp(p)
        else:
            tempdir_raw, _ = mobi.extract(str(p))
            tempdir = Path(tempdir_raw)
    except Exception as e:
        emit(t("inspect.status_fail", err=e), level="error")
        return
    try:
        base_dir = select_mobi_dir(tempdir, args.prefer)
        opf_path = find_opf(base_dir)
        if opf_path:
            images = extract_images_by_spine(opf_path)
            if not images:
                images = collect_images_fallback(base_dir)
        else:
            images = collect_images_fallback(base_dir)
        if not images:
            emit(t("list.no_images"), level="error")
            return
        spine_set = {norm_path(i) for i in images}
        # 封面补齐：OPF guide 封面优先，未命中回退文件名关键词（与 inspect 链路口径一致）
        cover_extra = False
        cover_guide_path = None
        if images and opf_path:
            href = get_opf_guide_cover_href(opf_path)
            if href:
                clean = href.split("#", 1)[0]
                cand = (opf_path.parent / clean).resolve()
                if not (cand.is_file() and cand.suffix.lower() in IMAGE_EXTENSIONS):
                    cand = (base_dir / clean).resolve()
                if cand.is_file() and cand.suffix.lower() in IMAGE_EXTENSIONS:
                    cover_guide_path = cand
        if images:
            cover = cover_guide_path
            if cover is None:
                cover_cands = [cp for cp in base_dir.rglob("*")
                               if cp.is_file() and cp.suffix.lower() in IMAGE_EXTENSIONS
                               and any(k in cp.name.lower() for k in COVER_KEYWORDS)]
                if cover_cands:
                    cover_cands.sort(key=natural_key)
                    cover = cover_cands[0]
            if cover is not None and norm_path(cover) not in spine_set:
                images.insert(0, cover)
                cover_extra = True
        # 目录对齐：多余图（extra 条件决定追加或舍弃）
        collected = {norm_path(i) for i in images}
        extras = [ep for ep in base_dir.rglob("*")
                  if ep.is_file() and ep.suffix.lower() in IMAGE_EXTENSIONS
                  and norm_path(ep) not in collected]
        extras.sort(key=natural_key)
        drop_all_extra = bool(drop_expr) and any(("extra",) in g for g in drop_expr)
        extra_dropped = bool(drop_all_extra)
        extra_marks = {}
        if drop_all_extra:
            for ep in extras:
                extra_marks[norm_path(ep)] = "dropped"
        else:
            images = images + extras
            for ep in extras:
                extra_marks[norm_path(ep)] = "appended"
        # 物理去重
        deduped, seen = [], set()
        for img in images:
            nk = norm_path(img)
            if nk in seen:
                continue
            seen.add(nk)
            deduped.append(img)
        images = deduped
        # 目录映射
        ncx_map, nav_map, has_ncx, has_nav = build_toc_maps(base_dir)
        multi_src = has_ncx and has_nav
        # 属性构建 + 处置标记
        attrs_list = []
        for img in images:
            a = build_image_attrs(img, double_ratio)
            nk = norm_path(img)
            a["extra"] = nk in extra_marks
            if cover_extra and nk == norm_path(images[0]):
                a["cover_extra"] = True
                a["inferred"] = True
            elif ((cover_guide_path is not None and nk == norm_path(cover_guide_path))
                  or (nk in spine_set and any(k in img.name.lower() for k in COVER_KEYWORDS))):
                a["cover"] = True
            a["extra_dropped"] = extra_marks.get(nk) == "dropped"
            # drop-small 命中标记
            a["drop_small_hit"] = False
            a["toc"] = toc_label_for(nk, ncx_map, nav_map, multi_src)
            attrs_list.append(a)
        _fill_small_mark(attrs_list, small_ratio)
        _fill_overscale_mark(attrs_list)
        # drop-small 命中判定（面积口径，与 [小图] 标记 / 转换丢弃 / inspect 预览统一）
        if small_ratio is not None:
            dims = [(a["w"], a["h"]) for a in attrs_list if a.get("w") and a.get("h")]
            if len(dims) >= 2:
                med_area = _median_area(dims)
                for a in attrs_list:
                    if a.get("w") and a.get("h") and a["w"] * a["h"] < med_area * small_ratio:
                        a["drop_small_hit"] = True
        # 处置状态固化（append/drop，供 filter/drop/append 筛选原子与标记复用）
        for a in attrs_list:
            d = _dropped_desc(drop_expr, a) if drop_expr is not None else None
            filter_hit = bool(d) and "extra" not in d
            if a.get("extra_dropped") or a.get("drop_small_hit") or filter_hit:
                a["disposition"] = "drop"
            elif a.get("extra") or a.get("cover_extra"):
                a["disposition"] = "append"
            else:
                a["disposition"] = None
        # 清单行（FILTER 筛选）+ 目录预览
        has_toc = has_ncx or has_nav
        if has_toc:
            if has_ncx:
                ncx_count, ncx_preview = parse_ncx_toc(base_dir)
                ncx_str = " | ".join(ncx_preview)
                if ncx_count > len(ncx_preview):
                    ncx_str += " | ..."
                emit(t("inspect.ncx_count", count=ncx_count, preview=ncx_str))
            if has_nav:
                nav_count, nav_preview = parse_nav_toc(base_dir)
                nav_str = " | ".join(nav_preview)
                if nav_count > len(nav_preview):
                    nav_str += " | ..."
                emit(t("inspect.nav_count", count=nav_count, preview=nav_str))
        rows = []
        for i, a in enumerate(attrs_list, 1):
            if not _list_filter_pass(a, list_expr):
                continue
            marks = _mark_strs(a, False, drop_expr, small_ratio)
            rows.append({
                "no": i, "name": a["path"].name, "res": f"{a['w']}x{a['h']}" if a.get("w") and a.get("h") else "?",
                "size": _fmt_size(a["size"]), "mode": _mode_str(a["mode"], a["depth"]),
                "dir": _dir_str(a["dir"]), "toc": a["toc"], "mark": " ".join(marks),
            })
        if rows:
            _render_table(rows, has_toc)
        else:
            emit(t("list.no_match"), level="info")
        _render_stats(attrs_list, has_toc, extra_dropped, small_ratio)
        # 构建 JSON 文件级记录（--list-images --json / --json-out 输出使用）
        return _build_list_record(str(p), attrs_list, has_toc)
    finally:
        if tempdir is not None:  # 解包异常路径 tempdir 为 None，跳过清理（内部已自清理）
            try:
                shutil.rmtree(tempdir, ignore_errors=True)
            except Exception:
                pass


def _cbz_opf_cover_zname(zf) -> str | None:
    """从 CBZ zip 内 OPF 解析封面条目名（zip 内路径），无 OPF / 未命中返回 None。

    定位 OPF：META-INF/container.xml 指定 rootfile 优先，回退 *.opf 条目；
    解析逻辑与 _opf_cover_href_scan 一致（guide > cover-image > meta cover）。"""
    try:
        names = zf.namelist()
    except Exception:
        return None
    opf_entry = None
    try:
        if "META-INF/container.xml" in names:
            ctext = zf.read("META-INF/container.xml").decode("utf-8", "replace")
            m = re.search(r'full-path=["\']([^"\']+\.opf)["\']', ctext, re.I)
            if m and m.group(1) in names:
                opf_entry = m.group(1)
    except Exception:
        opf_entry = None
    if opf_entry is None:
        for n in names:
            if n.lower().endswith(".opf") and not n.endswith("/"):
                opf_entry = n
                break
    if opf_entry is None:
        return None
    try:
        otext = zf.read(opf_entry).decode("utf-8", "replace")
    except Exception:
        return None
    href = _opf_cover_href_scan(otext)
    if not href:
        return None
    href = href.split("#", 1)[0]
    # href 相对 OPF 所在 zip 目录解析（支持 ../ 归一）
    parts = []
    if "/" in opf_entry:
        parts = [seg for seg in opf_entry.rsplit("/", 1)[0].split("/") if seg not in ("", ".")]
    for seg in href.replace("\\", "/").split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)
    return "/".join(parts)


def _list_cbz(p: Path, args, double_ratio, list_expr) -> None:
    """CBZ 单文件清单：zipfile 直读不落盘；无目录列、无转换态标记。"""
    emit(t("list.file_line", name=p.name))
    drop_expr = args.drop  # 统一丢弃表达式（条件组或 None）
    # 小图比例：清单表达式内 small 条件优先，其次 --drop 表达式
    small_ratio = extract_small_ratio(list_expr) or extract_small_ratio(drop_expr)
    try:
        with zipfile.ZipFile(str(p)) as zf:
            names = [n for n in zf.namelist()
                     if Path(n).suffix.lower() in IMAGE_EXTENSIONS and not n.endswith("/")]
            names.sort(key=lambda n: natural_key(Path(n)))
            if not names:
                emit(t("list.no_images"), level="error")
                return
            attrs_list = []
            cover_zname = _cbz_opf_cover_zname(zf)
            for n in names:
                a = build_cbz_image_attrs(zf, n, double_ratio)
                if cover_zname and cover_zname == n.replace("\\", "/"):
                    a["cover"] = True
                elif any(k in Path(n).name.lower() for k in COVER_KEYWORDS):
                    a["cover"] = True
                attrs_list.append(a)
            _fill_small_mark(attrs_list, small_ratio)
            _fill_overscale_mark(attrs_list)
            if small_ratio is not None:
                dims = [(a["w"], a["h"]) for a in attrs_list if a.get("w") and a.get("h")]
                if len(dims) >= 2:
                    med_area = _median_area(dims)
                    for a in attrs_list:
                        if a.get("w") and a.get("h") and a["w"] * a["h"] < med_area * small_ratio:
                            a["drop_small_hit"] = True
            rows = []
            for i, a in enumerate(attrs_list, 1):
                if not _list_filter_pass(a, list_expr):
                    continue
                marks = _mark_strs(a, True, drop_expr, small_ratio)
                rows.append({
                    "no": i, "name": Path(a["zname"]).name,
                    "res": f"{a['w']}x{a['h']}" if a.get("w") and a.get("h") else "?",
                    "size": _fmt_size(a["size"]), "mode": _mode_str(a["mode"], a["depth"]),
                    "dir": _dir_str(a["dir"]), "toc": "", "mark": " ".join(marks),
                })
            if rows:
                _render_table(rows, False)
            else:
                emit(t("list.no_match"), level="info")
            _render_stats(attrs_list, False, False, small_ratio)
            # 构建 JSON 文件级记录（--list-images --json / --json-out 输出使用）
            return _build_list_record(str(p), attrs_list, False)
    except zipfile.BadZipFile as e:
        emit(t("list.badzip", err=e), level="error")
        return None
    except Exception as e:
        emit(t("list.fail", err=e), level="error")
        return None


def list_images_mode(ebook_files: list[Path], args) -> None:
    """--list-images 主入口：遍历文件输出清单 + 统计。

    表达式统一在此解析一次（None=全列），避免无值 const='all' 被
    当作过滤表达式逐字符遍历导致清单为空。
    """
    if getattr(args, "list_images", None) in (None, "all"):
        list_expr = None
    else:
        try:
            list_expr = parse_drop_expr(args.list_images)
        except argparse.ArgumentTypeError as e:
            emit(str(e), level="error")
            return
    double_ratio = args.double_page
    if not isinstance(double_ratio, (int, float)):
        double_ratio = _parse_double_page_arg(double_ratio) if double_ratio else None
    records = []
    total_start = time.perf_counter()
    for p in ebook_files:
        if p.suffix.lower() == ".cbz":
            rec = _list_cbz(p, args, double_ratio, list_expr)
        else:
            rec = _list_ebook(p, args, double_ratio, list_expr)
        if rec is not None:
            records.append(rec)
    # --list-images 的 JSON 输出（--json stdout 精简 / --json-out 落盘全量）
    if _json_stdout or _json_out_path:
        _emit_list_json(records, time.perf_counter() - total_start)


def build_parser() -> argparse.ArgumentParser:
    """构建参数解析器：help 文案全部经 t() 生成，随 --language 切换"""
    parser = argparse.ArgumentParser(description=t("help.description"))
    parser.add_argument(
        "--version", action="version", version=f"{SCRIPT_NAME} {__version__}"
    )
    # 输入：语言选择 auto/zh-CN/zh-TW/ja/en；输出：全部文案与 --help 随所选语言翻译
    # 容错：zh/cn/zhtw/jp 等常见写法经 _normalize_lang 规范化，未知写法回退 en
    parser.add_argument(
        "--language",
        default="auto",
        help=t("help.language"),
    )
    # 输入：目标目录或文件路径（位置参数）；输出：作为扫描/转换的起点
    parser.add_argument("target", help=t("help.target"))
    # 输入：仅处理 target 目录顶层文件；输出：不递归子目录收集电子书
    parser.add_argument(
        "--top-only", action="store_true", help=t("help.top_only")
    )
    # 输入：是否删除源文件；输出：转换成功后删除原始电子书
    parser.add_argument(
        "--delete", action="store_true", help=t("help.delete")
    )
    # 输入：双目录 mobi 保留哪份 mobi7/mobi8；输出：解包后选择目录的依据
    parser.add_argument(
        "--prefer",
        choices=["mobi7", "mobi8", "auto"],
        default="auto",
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
    # 输入：统一丢弃过滤器（--drop，nargs='?' 可选值）；输出：转换时按条件丢弃图片
    # 取值：无值 → 丢弃全部多余图片；带值 → extra/small[=比例]/格式/条件词过滤
    #       （逗号=OR、'+'=AND）；off/no/0/false → 关闭。三链路（转换/inspect/清单）同源。
    parser.add_argument(
        "--drop",
        nargs="?",
        const="extra",
        default=None,
        metavar="EXPR",
        type=parse_drop_expr,
        help=t("help.drop"),
    )
    # 隐藏兼容别名：旧 --drop-extra 并入 --drop（无值/extra 语义不变，带值即过滤表达式）
    parser.add_argument(
        "--drop-extra",
        nargs="?",
        const="extra",
        default=None,
        metavar="FILTER",
        type=parse_drop_expr,
        help=argparse.SUPPRESS,
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
        default=DEFAULT_TIMEOUT,
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
    # 输入：进度条显示策略 auto|on|off；输出：控制文件级进度条是否显示
    # 取值：不传 → off（默认关闭）；--progress 无值 → auto（TTY 且文件数≥2 且未用 --json/--json-out 时显示）；on → 强制显示；off → 强制关闭
    parser.add_argument(
        "--progress",
        nargs="?",
        const="auto",
        default="off",
        metavar="VALUE",
        choices=["auto", "on", "off"],
        help=t("help.progress"),
    )
    # 隐藏兼容别名：旧 --no-progress（强制关闭进度条）保留，避免旧命令失效
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    # 输入：是否静默；输出：抑制非 summary/error 级输出（仅写日志）
    parser.add_argument(
        "--quiet",
        action="store_true",
        help=t("help.quiet"),
    )
    # 输入：是否禁用颜色；输出：即使 TTY 且无 NO_COLOR 也不上色（日志/JSON/管道本就不含颜色）
    parser.add_argument(
        "--no-color",
        action="store_true",
        help=t("help.no_color"),
    )
    # 输入：是否输出调试信息；输出：--debug 时 debug 级行到 stderr（日志文件始终记录）
    parser.add_argument(
        "--debug",
        action="store_true",
        help=t("help.debug"),
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
    # 输入：检查模式 [MODE][,FILTER]；输出：sample 随机抽查 1 个文件，all 全量检查（均不生成 cbz）
    # 取值：不传 → sample（抽查 1 个）；MODE=sample|all；后缀 ,FILTER → 命中条件的图片输出数量+清单
    parser.add_argument(
        "--inspect",
        nargs="?",
        const="sample",
        default=None,
        metavar="[MODE][,FILTER]",
        type=parse_inspect_arg,
        help=t("help.inspect"),
    )
    # 隐藏兼容别名：旧 --inspect-all（全量检查）保留，等价 --inspect all
    parser.add_argument(
        "--inspect-all",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    # 输入：是否关闭 ComicInfo.xml 生成；输出：关闭时 CBZ 不含漫画元数据
    parser.add_argument(
        "--no-comicinfo",
        action="store_true",
        help=t("help.no_comicinfo"),
    )
    # 输入：双页检测（nargs='?'，可选值）；输出：ComicInfo 仅写逐页 DoublePage 标记；Manga 改用 --setinfo 单独声明
    # 取值：不传/auto → 开启（阈值 2.0）；数值 → 开启并调阈值；off/no/0/false → 关闭
    parser.add_argument(
        "--double-page",
        nargs="?",
        const="auto",
        default="auto",
        metavar="VALUE",
        type=_parse_double_page_arg,
        help=t("help.double_page"),
    )
    # 隐藏兼容别名：旧 --drop-small 并入 --drop（映射为 --drop small[=比例]；无值/auto → 0.5）
    parser.add_argument(
        "--drop-small",
        nargs="?",
        const="auto",
        default=None,
        metavar="VALUE",
        type=_parse_drop_small_arg,
        help=argparse.SUPPRESS,
    )
    # 输入：列出图片清单（nargs='?' 可选值）；输出：清单+全量统计，不生成 CBZ
    # 取值：无值 → 全量列出；带值 → FILTER 表达式（逗号=OR、'+'=AND，支持格式/分辨率/大小/
    #       方向/模式/位深/标记，'-'前缀排除类目词）
    parser.add_argument(
        "--list-images",
        nargs="?",
        const="all",
        default=None,
        metavar="FILTER",
        help=t("help.list_images"),
    )
    # 输入：设置 ComicInfo 字段（可多次）；输出：覆盖/新增对应字段
    parser.add_argument(
        "--setinfo",
        action="append",
        default=[],
        metavar="FIELD=VALUE",
        help=t("help.setinfo"),
    )
    # 输入：是否重命名输出文件名（nargs='?' 可选模板，默认关闭）；输出：CBZ 文件名按模板+自动标记前缀生成
    # 取值：不传 → 关闭（保持原名）；--rename 无值 → 默认模板（系列名+自动标记前缀）；--rename=TEMPLATE → 自定义模板
    #       标记前缀按类型自动选：整卷[Vol.x]/单话[Ch.x]/卷+章[Vol.x][Ch.x]/无类型[x]；连话（話005-006）标 [Ch.5-6]
    #       占位符：%series/%number/%volume/%title/%writer/%publisher/%date/%language/%description/%filename/%leftN/%rightN/%subN_M、%0<N>number 补零
    #       来源优先级：文件名推断 > 文件自带元数据(OPF/ComicInfo.xml) 兜底；setinfo 解耦不参与
    parser.add_argument(
        "--rename",
        nargs="?",
        const="default",
        default=None,
        metavar="TEMPLATE",
        help=t("help.rename"),
    )
    # 输入：日志文件路径；输出：控制台输出同步写入该文件（UTF-8）
    parser.add_argument(
        "--log",
        nargs="?",
        const="auto",
        metavar="FILE",
        help=t("help.log"),
    )
    # 输入：是否输出 JSON；输出：stdout 单行紧凑 JSON（给 AI/管道读取），开启时屏蔽人类可读文本（error 走 stderr）
    parser.add_argument(
        "--json",
        action="store_true",
        help=t("help.json"),
    )
    # 输入：JSON 输出文件路径；输出：转换结果写入 JSON 文件（省略时自动时间戳命名，对齐 --log auto）
    parser.add_argument(
        "--json-out",
        nargs="?",
        const="auto",
        metavar="FILE",
        help=t("help.json_out"),
    )
    # 输入：是否解包查看；输出：只解压不转换，输出到源文件所在目录的「源名_扩展名」子目录
    parser.add_argument(
        "--unpack",
        action="store_true",
        help=t("help.unpack"),
    )
    # 输入：重新打包；输出：将已解包的 CBZ 目录（目录名以 .cbz 结尾）打包回 CBZ
    parser.add_argument(
        "--repack",
        action="store_true",
        help=t("help.repack"),
    )
    return parser


def _main() -> None:
    # 先解析 --language（不触发帮助），确定语言后再建正式 parser，使 --help 随语言翻译
    # 容错：zh/cn/zhtw/jp 等常见写法经 set_language→_normalize_lang 规范化，未知写法回退 en
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        "--language",
        default="auto",
    )
    known, _ = pre_parser.parse_known_args()
    set_language(known.language)

    parser = build_parser()
    args = parser.parse_args()

    # 修复7（nargs 吞路径）_main 兜底纠正：nargs='?' 选项值恰为已存在路径且 target 缺失时，
    # 判定该值是被误吞的目标路径 → 回填 target 并将选项复位为默认值（未传入语义）。
    # 在 --inspect-all 归一化之前执行，避免与 inspect 复位冲突。
    # 注：target 为必填位置参数，argparse 已在 parse_args 阶段对"选项+空格+路径且无 target"
    #     报 target required 退出；此兜底为防御性覆盖 target 被解析为 None/空串的边缘场景，
    #     主要防护仍靠四语 help 提示（带值请用 --选项=值 或路径前置）。
    _nargs_opt_defaults = {
        "drop": None, "drop_extra": None, "min_size": 0, "progress": "off",
        "inspect": None, "double_page": "auto", "drop_small": None,
        "list_images": None, "rename": None, "log": None, "json_out": None,
    }
    for _attr, _default in _nargs_opt_defaults.items():
        _val = getattr(args, _attr, None)
        if isinstance(_val, str) and _val and not args.target and os.path.exists(_val):
            args.target = _val
            setattr(args, _attr, _default)

    # 旧 --inspect-all 隐藏别名归一化：等价 --inspect all
    if args.inspect_all:
        args.inspect = parse_inspect_arg("all")

    # --drop / --drop-extra / --drop-small 合并为统一丢弃表达式（组间 OR）
    drop_groups = args.drop or []
    if args.drop_extra is not None:
        drop_groups = drop_groups + args.drop_extra
    if args.drop_small is not None:
        # --drop-small 映射为 small 条件（无值/auto → 默认比例）
        drop_groups = drop_groups + [[("small", args.drop_small)]]
    args.drop = drop_groups or None

    global _debug_mode, _quiet_mode, _log_path, _short_summary, _compress_level, _json_stdout, _json_out_path, _color_enabled
    _debug_mode = args.debug
    _quiet_mode = args.quiet
    # 颜色开关：TTY 且无 NO_COLOR 环境变量 且 未显式 --no-color（模块级默认已检测前两者，此处仅收 --no-color）
    _color_enabled = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None and not args.no_color
    if args.log == "auto":
        _log_path = f"manga-mobi2cbz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        emit(t("log.auto_named", path=_log_path))
    else:
        _log_path = args.log
    _short_summary = args.short_summary
    _compress_level = args.compress
    _json_stdout = args.json
    if args.json_out == "auto":
        _json_out_path = f"manga-mobi2cbz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:
        _json_out_path = args.json_out

    # 输入：--language auto（或未显式指定走默认 auto）；输出：提示实际识别的语种（quiet 时抑制）
    if known.language == "auto":
        emit(t("run.auto_language", lang=CURRENT_LANGUAGE))

    target = Path(args.target)
    # 通配符模式（含 * 或 ?）不做字面存在性检查，交给 collect_ebook_files 做 glob 展开
    if not target.exists() and not any(c in args.target for c in "*?"):
        emit(t("run.path_not_found", path=args.target), level="error")
        sys.exit(2)

    output_dir = Path(args.output_dir) if args.output_dir else None

    # 启动校验：--flatten 必须与 --output-dir 联用，否则报错退出
    if args.flatten and output_dir is None:
        emit(t("error.flatten_without_output_dir"), level="error")
        emit(t("output.flatten_requires_dir"), level="error")
        sys.exit(2)

    # --inspect-all 隐藏别名已在解析后归一化为 --inspect all

    # input_root：target 为目录时作为相对子目录结构的基准；
    # target 为文件时不计算相对路径，直接输出 DIR/stem.cbz
    input_root = target if target.is_dir() else None

    # --repack 模式：target 是 .cbz 解包目录或含 *.cbz 解包目录的父目录，
    # 不走电子书收集流程，直接打包回 CBZ 后返回
    if args.repack:
        repack_mode(target, args)
        return

    ebook_files = collect_ebook_files(target, include_cbz=args.inspect is not None or args.unpack or args.list_images or bool(args.setinfo) or bool(args.rename), top_only=args.top_only)
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

    if precheck_skipped and not args.dry_run and args.inspect is None and not args.unpack:
        emit(t("run.precheck_header", count=len(precheck_skipped)), level="summary")
        if not _short_summary:
            for mf, reason in precheck_skipped:
                emit("  " + t("skip_entry", path=str(mf), reason=reason), level="summary")

    # 只读/解包模式串联执行（互不排斥）：unpack → inspect → list-images 依次跑完；
    # 任一模式被指定即在此处理后 return，不再进入下方 CBZ 修改/转换流程
    mode_used = False
    if args.unpack:
        unpack_mode(ebook_files, args)
        mode_used = True

    if args.inspect is not None:
        inspect_mode(ebook_files, precheck_skipped, args)
        mode_used = True

    # --list-images 模式：列出书内图片清单+统计（EPUB/MOBI 走解包，CBZ 走 zipfile 直读）
    if args.list_images:
        list_images_mode(ebook_files, args)
        mode_used = True

    if mode_used:
        return

    # #36 CBZ 修改模式：--setinfo 且输入为已有 CBZ 时，直接修改其 ComicInfo.xml；
    # --rename 独立模式：输入为已有 CBZ 时仅重命名文件名（二者可叠加，P0-2 修复：先改元数据再改名）
    cbz_modify_files = [f for f in ebook_files if f.suffix.lower() == ".cbz"]
    ebook_files = [f for f in ebook_files if f.suffix.lower() != ".cbz"]
    if cbz_modify_files:
        # P0-2 修复（方案A，推荐）：先 setinfo 再 rename。
        #   原顺序先 rename 后 modify，二者共用 cbz_modify_files 旧路径列表，
        #   rename 原地改名后 modify 打开旧路径 → FileNotFoundError。
        if args.setinfo:
            modify_cbz_mode(cbz_modify_files, args)
        if args.rename:
            rename_cbz_mode(cbz_modify_files, args)

    if not ebook_files:
        # 纯 CBZ 修改模式已处理完成，无待转换 mobi
        return

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
        _dryrun_start = time.perf_counter()
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
        json_files: list = []
        pbar = create_progress_if_needed(args, ebook_files, t("progress.desc.dry_run"))
        try:
            for mf in ebook_files:
                if pbar is not None:
                    pbar.set_postfix_str(truncate_name(mf.name))
                out = target_cbz_path(mf, output_dir, flatten=args.flatten, input_root=input_root)
                rinfo = None
                if args.rename:
                    new_stem, rinfo = _build_rename_basename(mf, args.rename)
                    out = _apply_rename_to_target(out, new_stem)
                will_skip = (out.exists() or str(out) in used_names) and not args.overwrite
                state_tag = t("tag.will_skip") if will_skip else t("tag.pending")
                if not will_skip:
                    used_names.add(str(out))
                # rename 预览着色（颜色③）：主干青色、自动标记前缀绿色（仅 TTY 且未 --no-color 时生效）
                if rinfo and rinfo["new_stem"] != rinfo["old_stem"]:
                    mark = rinfo.get("mark") or ""
                    new_stem = rinfo["new_stem"]
                    head = new_stem[:-len(mark)] if mark and new_stem.endswith(mark) else new_stem
                    out_disp = _c(36, head) + (_c(32, mark) if mark else "") + ".cbz"
                    emit(f"  {state_tag} {mf} -> {out_disp}", level="summary")
                else:
                    emit(f"  {state_tag} {mf} -> {out}", level="summary")
                json_files.append({
                    "source": str(mf),
                    "status": "will_skip" if will_skip else "pending",
                    "target": str(out),
                    "reason": None,
                    "elapsed_sec": None,
                    "renamed": {"old": rinfo["old_stem"] + ".cbz", "new": rinfo["new_stem"] + ".cbz"} if rinfo and rinfo["new_stem"] != rinfo["old_stem"] else None,
                    "series_source": (rinfo or {}).get("series_source"),
                    "number_source": (rinfo or {}).get("number_source"),
                    "volume_source": (rinfo or {}).get("volume_source"),
                    "dry_run": True,
                })
                if pbar is not None:
                    pbar.update(1)
        finally:
            if pbar is not None:
                pbar.close()
        emit(t("run.dryrun_end"), level="summary")
        emit_json(json_files, success=0, skipped=sum(1 for x in json_files if x["status"] == "will_skip"),
                  failed=0, interrupted=False, total_elapsed=time.perf_counter() - _dryrun_start)
        return

    # 启动告警：扫描上次中断/强杀/断电残留的 *.cbz.tmp 半成品（仅告警不删除，保护用户数据）
    try:
        stale = []
        if output_dir is not None and output_dir.is_dir():
            stale.extend(output_dir.rglob("*.cbz.tmp"))
        else:
            seen_roots = set()
            for mf in ebook_files:
                d = mf.parent.resolve()
                if d in seen_roots:
                    continue
                seen_roots.add(d)
                stale.extend(d.rglob("*.cbz.tmp"))
        stale = sorted(set(stale))
        if stale:
            emit(t("run.stale_tmp", count=len(stale)), level="warning")
            if not _short_summary:
                for s in stale[:10]:
                    emit(f"  {s}", level="warning")
    except Exception:
        pass

    emit(t("run.start", count=len(ebook_files)))

    total_start = time.perf_counter()
    json_files: list = []
    success = 0
    success_cbzs = []
    skipped_files = []
    failed_files = []
    failed_reasons = Counter()
    interrupted = False
    drop_total = 0
    pbar = create_progress_if_needed(args, ebook_files, t("progress.desc.convert"))
    try:
        for mf in ebook_files:
            if pbar is not None:
                pbar.set_postfix_str(truncate_name(mf.name))
            file_start = time.perf_counter()
            disk_warn = check_disk_space(output_dir or mf.parent, Path(tempfile.gettempdir()), estimate_expanded_size(mf))
            if disk_warn:
                emit(disk_warn, level="warning")
            timed_out, converted = run_with_timeout(
                ebook_to_cbz, args.timeout,
                mf, delete_original=args.delete, prefer=args.prefer,
                drop_expr=args.drop, overwrite=args.overwrite,
                output_dir=output_dir, compress=_compress_level,
                flatten=args.flatten, input_root=input_root,
                comicinfo=not args.no_comicinfo, setinfo_args=args.setinfo,
                double_page=args.double_page,
                rename_template=args.rename,
            )
            file_elapsed = time.perf_counter() - file_start
            json_status = "ok"
            json_target = None
            json_reason = None
            conv_sources = None
            if timed_out:
                emit(t("run.timeout", name=mf.name, seconds=args.timeout), level="error")
                emit(t("run.timeout_residue"), level="warning")
                failed_files.append(mf)
                failed_reasons["timeout"] += 1
                json_status = "timeout"
                json_reason = "timeout"
            else:
                result, status, reason, conv_sources = converted
                if status == ConvStatus.OK:
                    success += 1
                    success_cbzs.append(result)
                    json_target = str(result)
                elif status == ConvStatus.SKIP:
                    skipped_files.append(mf)
                    json_status = "skip"
                elif status == ConvStatus.FAIL:
                    failed_files.append(mf)
                    failed_reasons[reason] += 1
                    json_status = "fail"
                    json_reason = reason
            emit(t("run.elapsed", name=mf.name, seconds=f"{file_elapsed:.2f}"))
            conv_sources = conv_sources or {}
            drop_total += conv_sources.get("dropped_small") or 0
            _renamed = conv_sources.get("renamed")
            json_files.append({
                "source": str(mf),
                "status": json_status,
                "target": json_target,
                "reason": json_reason,
                "elapsed_sec": round(file_elapsed, 3),
                "renamed": {"old": _renamed["old_stem"] + ".cbz", "new": _renamed["new_stem"] + ".cbz"} if _renamed else None,
                "series_source": conv_sources.get("series_source"),
                "number_source": conv_sources.get("number_source"),
                "volume_source": conv_sources.get("volume_source"),
                "cover_source": conv_sources.get("cover_source"),
                "dropped_small": conv_sources.get("dropped_small"),
                "dropped_filter": conv_sources.get("dropped_filter"),
            })
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
    if drop_total:
        emit(t("run.drop_small_total", count=drop_total), level="summary")
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
    if failed_reasons:
        parts = ", ".join(f"{k}={v}" for k, v in failed_reasons.items())
        emit(t("run.failed_reasons", summary=parts), level="summary")
    emit(t("run.total_elapsed", seconds=f"{total_elapsed:.2f}"), level="summary")
    emit_json(json_files, success=success, skipped=len(skipped_files),
              failed=len(failed_files), interrupted=interrupted,
              total_elapsed=total_elapsed)

    # 退出码语义：0=全部成功（含全部跳过，无失败）；1=存在转换失败文件（失败/DRM/校验失败）；
    # 130=转换过程中收到 Ctrl+C 中断（即使已转换部分也以中断码退出，与包装层一致）
    sys.exit(130 if interrupted else (1 if failed_files else 0))


if __name__ == "__main__":
    main()
