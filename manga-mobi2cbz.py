#!/usr/bin/env python3
"""
manga-mobi2cbz — 将 mobi/azw/azw3/epub 电子书漫画文件批量转换为 cbz 格式（OPF spine 排序 + 封面兜底增强版）

用法:
    python manga-mobi2cbz.py <目录或文件路径> [--language auto|zh-CN|zh-TW|ja|en] [--delete] [--prefer mobi7|mobi8|auto] [--ext-priority EXTS] [--drop-extra] [--overwrite] [--timeout SECONDS] [--output-dir DIR] [--flatten] [--dry-run] [--progress|--no-progress] [--quiet] [--short-summary] [--compress LEVEL] [--inspect] [--inspect-all] [--no-comicinfo] [--setinfo FIELD=VALUE] [--unpack] [--log FILE]

示例:
    # 转换整个文件夹（递归搜索所有 .mobi/.azw/.azw3/.epub）
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

    # 平铺输出：所有 CBZ 直接放到输出目录根下（同名未指定 --overwrite 时跳过）
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

    # 覆盖/新增 ComicInfo 字段（可多次；VALUE 支持 %series/%number/%title/%filename/%leftN/%rightN）
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi" --setinfo "Series=One Piece" --setinfo "Number=%number" --setinfo "Summary=hello, world"

    # 解包查看：只解压不转换，输出到源文件所在目录的同名子目录
    python manga-mobi2cbz.py "D:\\Manga\\Vol1.mobi" --unpack

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
    --drop-extra     目录中有未被收集的多余图片时放弃追加，默认追加到末尾
    --overwrite      目标 cbz 已存在时强制重新生成（默认跳过）
    --timeout SECONDS 单文件转换超时秒数，超时自动跳过并计入失败（默认 600，0 表示不限制）
    --min-size BYTES  过滤小于指定字节的电子书（不带数字默认 1000，0 关闭，不传则关闭）
    --output-dir DIR CBZ 输出到指定目录（自动创建），默认保留相对输入的
                     子目录结构（如 One Piece/001.mobi → DIR/One Piece/001.cbz），
                     需要平铺时加 --flatten
    --flatten       仅与 --output-dir 联用：所有 CBZ 平铺到输出目录根下，
                     同名文件未指定 --overwrite 时跳过（SKIP），
                     指定时覆盖首选名；单独使用（无 --output-dir）将报错退出
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
    --double-page   双页检测：图片宽/高 ≥ 阈值（默认 2.0）判为跨页横幅，
                     在 ComicInfo 写入逐页 <Page Type="DoublePage"/> 标记；
                     传数值调阈值，off/no/0 关闭（默认 auto 开启）
    --drop-small    丢弃小图：开启时"宽和高均小于中位数×比例"的图被丢弃
                     （默认比例 0.5，传数值调比例，off/no/0 关闭，默认关闭）；
                     封面小缩略图等自动命中，丢弃后 PageCount 按实际图数重算
    --setinfo FIELD=VALUE 设置 ComicInfo 字段（可多次，后出现覆盖先出现；
                     优先级最高，覆盖自动推断/元数据来源）。VALUE 支持
                     固定值或占位符：%series/%number/%title/%filename/
                     %leftN/%rightN（%leftN=文件名前 N 字符，%rightN=后 N
                     字符；占位符对应值缺失时该字段不写入）。智能拆分：
                     仅当逗号后紧跟"字段名="时才拆分，否则逗号视为值的
                     一部分（如 Summary=hello, world 不拆分）。Manga 默认
                     不写入，需显式 --setinfo Manga=Unknown|No|Yes|YesAndRightToLeft
    --unpack        解包查看：只解压不转换，输出到各源文件所在目录的
                     同名子目录（已存在自动加序号避让）；mobi 走 extract
                     保留完整结构，cbz 走 extractall
    --log FILE       将全部输出追加写入指定日志文件
    --version        显示版本号

依赖: pip install mobi
要求: Python 3.10+

更新日志:
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
          "One Piece Vol.01" 等点号卷号可正确推断
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
         ）；"One Piece Vol.01" 等正常推断不受影响

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

__version__ = "2.5.1"

SCRIPT_NAME = "manga-mobi2cbz"

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
        "help.target": "电子书文件路径或包含电子书（.mobi/.azw/.azw3/.epub）的目录",
        "help.delete": "转换成功后删除原始电子书文件",
        "help.prefer": "双目录 mobi（mobi7/mobi8）时保留哪份：auto 默认优先 mobi8、空壳自动回退 mobi7；指定 mobi7/mobi8 时，指定目录为空也自动回退另一份",
        "help.ext_priority": "同目录同名（仅扩展名不同）时保留哪种格式：逗号分隔、顺序即优先级从高到低，仅接受 mobi/azw/azw3/epub，默认 azw3；优先级未覆盖时回退兜底顺序 azw3→epub→mobi→azw；与 --prefer（双目录选择）无关",
        "help.drop_extra": "目录中有未被收集的多余图片时放弃追加（默认追加到 cbz 末尾）",
        "help.overwrite": "目标 cbz 已存在时强制重新生成（默认跳过）",
        "help.timeout": "单文件转换超时秒数，超时自动跳过并计入失败（默认 600，0 表示不限制；超时后底层解包线程可能后台残留）",
        "help.min_size": "过滤小于指定字节的电子书；不带数字默认1000字节，0关闭大小过滤，不传则关闭",
        "help.output_dir": "CBZ 输出到指定目录（自动创建），默认保留相对输入的子目录结构（如 One Piece/001.mobi → DIR/One Piece/001.cbz），加 --flatten 可平铺到目录根下",
    "help.flatten": "仅与 --output-dir 联用：所有 CBZ 平铺到输出目录根下，同名文件未指定 --overwrite 时跳过（SKIP），指定时覆盖首选名；单独使用将报错退出",
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
        "help.double_page": "双页检测：不传/auto 开启（阈值 2.0）；数值调阈值；off/no/0 关闭（开启时写入逐页 DoublePage 标记，不写 Manga 声明；如需 Manga 请用 --setinfo Manga=）",
        "error.double_page_invalid": "无效的 --double-page 值 '{value}'：支持 auto/数值/off/no/0",
        "help.drop_small": "丢弃小图：转换时剔除尺寸明显偏小的图片（宽和高均 < 中位数×比例 判为小图；不传/auto=0.5，可传 0~1 数值调比例，off/no/0 关闭）；丢弃后 PageCount 按实际剩余图数重算",
        "error.drop_small_invalid": "无效的 --drop-small 值 '{value}'：支持 auto/数值(0~1)/off/no/0",
        "convert.drop_small": "  [清理] 丢弃小图 {count} 张: {names}",
        "run.drop_small_total": "丢弃小图合计: {count} 张",
        "inspect.drop_small_preview": "  [提示] 图片中 {count} 张为小图（开启 --drop-small 时将被丢弃）",
        "help.setinfo": "设置 ComicInfo 字段（可多次，格式 FIELD=VALUE；VALUE 支持 %%series/%%number/%%title/%%filename/%%leftN/%%rightN；逗号后紧跟字段名=才拆分，值内含 Key= 结构请用多次 --setinfo 传入；Manga 取值限 Unknown/No/Yes/YesAndRightToLeft，默认不写；--setinfo 开启时输入中的已有 .cbz 会就地修改其 ComicInfo.xml）",
        "comicinfo.generating": "生成 ComicInfo.xml",
        "comicinfo.created": "已写入 ComicInfo.xml",
        "comicinfo.disabled": "ComicInfo.xml 已禁用（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml 无效或生成失败: {err}",
        "comicinfo.inferred": "推断",
        "help.log": "将全部输出追加写入日志文件（省略文件名时自动生成时间戳日志）",
        "help.json": "在 stdout 输出单行紧凑 JSON 结果（给 AI/管道读取），开启时屏蔽人类可读文本；仅在转换或 CBZ 修改执行后输出（dry-run/inspect/unpack 不输出）；进度条写 stderr 不与 JSON 混流，但 2>&1 合并重定向会混入",
        "help.json_out": "将转换结果写入 JSON 文件（省略文件名时自动生成时间戳文件，或指定路径；同 --json 仅转换/修改模式写入）",
        "log.auto_named": "日志文件: {path}（自动命名）",
        "json.written": "JSON 结果已写入: {path}",
        "help.unpack": "解包模式：只解压不转换，输出到源文件所在目录的同名子目录（已存在自动加序号避让）",
        "unpack.done": "已解包 {name} -> {dir}",
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
        "align.drop": "  [提示] 目录中 {count} 张图片未被收集，已按 --drop-extra 放弃",
        "align.append": "  [提示] 目录中 {count} 张图片未被收集，已追加到末尾",
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
    "modify.done": "  [修改] {name}：ComicInfo.xml 已更新",
    "modify.nochange": "  [修改] {name}：无字段变化，未改动",
    "modify.fail": "  [失败] {name}: {err}",
    "modify.stats": "  修改完成：成功 {success}，无变化 {nochange}，失败 {fail}",
    "modify.failed_reasons": "修改失败原因: {summary}",
    "modify.dryrun_end": "  试运行结束：未实际修改任何 CBZ",
    "progress.desc.modify": "修改中",
    "setinfo.whitelist_skip": "  [警告] {field} 不在 ComicInfo 白名单，已忽略",
    "setinfo.unknown_placeholder": "  [警告] 未知占位符 {raw}，按原样写入",
    "setinfo.invalid_manga": "  [警告] 无效的 Manga 取值 '{value}'（限 Unknown/No/Yes/YesAndRightToLeft），已忽略",
    "convert.source_newer_reconvert": "  [提示] 目标 {name} 已存在但源文件更新，自动重新转换",
    "inspect.pagecount_mismatch": "  [提示] ComicInfo PageCount={declared} 与实际图片数 {actual} 不一致",
    "inspect.pagecount_non_numeric": "  [警告] ComicInfo PageCount 非数字: {raw}",
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
        "help.target": "電子書檔案路徑或包含電子書（.mobi/.azw/.azw3/.epub）的目錄",
        "help.delete": "轉換成功後刪除原始電子書檔案",
        "help.prefer": "雙目錄 mobi（mobi7/mobi8）時保留哪份：auto 預設優先 mobi8、空殼自動回退 mobi7；指定 mobi7/mobi8 時，指定目錄為空也自動回退另一份",
        "help.ext_priority": "同目錄同名（僅副檔名不同）時保留哪種格式：逗號分隔、順序即優先級從高到低，僅接受 mobi/azw/azw3/epub，預設 azw3；優先級未覆蓋時回退兜底順序 azw3→epub→mobi→azw；與 --prefer（雙目錄選擇）無關",
        "help.drop_extra": "目錄中有未被收集的多餘圖片時放棄追加（預設追加到 cbz 末尾）",
        "help.overwrite": "目標 cbz 已存在時強制重新生成（預設跳過）",
        "help.timeout": "單檔轉換逾時秒數，逾時自動跳過並計入失敗（預設 600，0 表示不限制；逾時後底層解包執行緒可能於背景殘留）",
        "help.min_size": "過濾小於指定位元組的電子書；不帶數字預設1000位元組，0關閉大小過濾，不傳則關閉",
        "help.output_dir": "CBZ 輸出到指定目錄（自動建立），預設保留相對輸入的子目錄結構（如 One Piece/001.mobi → DIR/One Piece/001.cbz），加 --flatten 可平鋪到目錄根下",
    "help.flatten": "僅與 --output-dir 聯用：所有 CBZ 平鋪到輸出目錄根下，同名檔案未指定 --overwrite 時跳過（SKIP），指定時覆蓋首選名；單獨使用將報錯退出",
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
        "help.double_page": "雙頁偵測：不傳/auto 開啟（閾值 2.0）；數值調閾值；off/no/0 關閉（開啟時寫入逐頁 DoublePage 標記，不寫 Manga 宣告；如需 Manga 請用 --setinfo Manga=）",
        "error.double_page_invalid": "無效的 --double-page 值 '{value}'：支援 auto/數值/off/no/0",
        "help.drop_small": "丟棄小圖：轉換時剔除尺寸明顯偏小的圖片（寬和高均 < 中位數×比例 判為小圖；不傳/auto=0.5，可傳 0~1 數值調比例，off/no/0 關閉）；丟棄後 PageCount 按實際剩餘圖數重算",
        "error.drop_small_invalid": "無效的 --drop-small 值 '{value}'：支援 auto/數值(0~1)/off/no/0",
        "convert.drop_small": "  [清理] 丟棄小圖 {count} 張: {names}",
        "run.drop_small_total": "丟棄小圖合計: {count} 張",
        "inspect.drop_small_preview": "  [提示] 圖片中 {count} 張為小圖（開啟 --drop-small 時將被丟棄）",
        "help.setinfo": "設定 ComicInfo 欄位（可多次，格式 FIELD=VALUE；VALUE 支援 %%series/%%number/%%title/%%filename/%%leftN/%%rightN；逗號後緊跟欄位名=才拆分，值內含 Key= 結構請用多次 --setinfo 傳入；Manga 取值限 Unknown/No/Yes/YesAndRightToLeft，預設不寫；--setinfo 開啟時輸入中的既有 .cbz 會就地修改其 ComicInfo.xml）",
        "comicinfo.generating": "生成 ComicInfo.xml",
        "comicinfo.created": "已寫入 ComicInfo.xml",
        "comicinfo.disabled": "ComicInfo.xml 已停用（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml 無效或生成失敗: {err}",
        "comicinfo.inferred": "推斷",
        "help.log": "將全部輸出追加寫入日誌檔案（省略檔名時自動產生時間戳日誌）",
        "help.json": "在 stdout 輸出單行緊湊 JSON 結果（供 AI/管道讀取），開啟時屏蔽人類可讀文本；僅在轉換或 CBZ 修改執行後輸出（dry-run/inspect/unpack 不輸出）；進度條寫 stderr 不與 JSON 混流，但 2>&1 合併重新導向會混入",
        "help.json_out": "將轉換結果寫入 JSON 檔案（省略檔名時自動產生時間戳檔案，或指定路徑；同 --json 僅轉換/修改模式寫入）",
        "log.auto_named": "日誌檔案: {path}（自動命名）",
        "json.written": "JSON 結果已寫入: {path}",
        "help.unpack": "解包模式：只解壓不轉換，輸出到來源檔案所在目錄的同名子目錄（已存在自動加序號避讓）",
        "unpack.done": "已解包 {name} -> {dir}",
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
        "align.drop": "  [提示] 目錄中 {count} 張圖片未被收集，已按 --drop-extra 放棄",
        "align.append": "  [提示] 目錄中 {count} 張圖片未被收集，已追加到末尾",
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
    "modify.done": "  [修改] {name}：ComicInfo.xml 已更新",
    "modify.nochange": "  [修改] {name}：無欄位變化，未改動",
    "modify.fail": "  [失敗] {name}: {err}",
    "modify.stats": "  修改完成：成功 {success}，無變化 {nochange}，失敗 {fail}",
    "modify.failed_reasons": "修改失敗原因: {summary}",
    "modify.dryrun_end": "  試運行結束：未實際修改任何 CBZ",
    "progress.desc.modify": "修改中",
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
        "help.target": "Path to an ebook file or a directory containing ebooks (.mobi/.azw/.azw3/.epub)",
        "help.delete": "Delete the original ebook file after successful conversion",
        "help.prefer": "Which directory to keep when both mobi7/mobi8 exist: auto (default) prefers mobi8 and falls back to mobi7 if empty; when mobi7/mobi8 is specified, falls back to the other if the chosen one is empty",
        "help.ext_priority": "When same-name files differ only by extension in the same directory, which format to keep: comma-separated, order is priority high->low, only mobi/azw/azw3/epub accepted, default azw3; falls back to azw3->epub->mobi->azw when not covered; unrelated to --prefer (mobi7/mobi8 selection)",
        "help.drop_extra": "Drop extra images not collected from the directory (default: append them to the end of the cbz)",
        "help.overwrite": "Force regenerate when the target cbz already exists (default: skip)",
        "help.timeout": "Per-file conversion timeout in seconds; on timeout the file is skipped and counted as failed (default 600, 0 = no limit; on timeout the underlying unpack thread may linger in the background)",
        "help.min_size": "Filter out ebooks smaller than the given bytes; without a number defaults to 1000 bytes, 0 disables size filtering, omitted disables it",
        "help.output_dir": "Output CBZ to the given directory (auto-created); by default keeps the relative subdirectory structure of the input (e.g. One Piece/001.mobi -> DIR/One Piece/001.cbz), add --flatten to flatten into the root",
    "help.flatten": "Only with --output-dir: flatten all CBZ into the root of the output directory; same-name files are skipped (SKIP) unless --overwrite is given, which overwrites the preferred name; using it alone exits with an error",
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
        "help.double_page": "Double-page detection: no value/auto enable (ratio 2.0); a number sets ratio; off/no/0 disable (when enabled, writes per-page DoublePage marks but no Manga element; use --setinfo Manga= for Manga)",
        "error.double_page_invalid": "Invalid --double-page value '{value}': use auto, a number, or off/no/0",
        "help.drop_small": "Drop small images: exclude images clearly smaller than others during conversion (an image is small if both its width and height are below median x ratio; no value/auto = 0.5, a 0~1 number sets ratio, off/no/0 disables). PageCount is recalculated after dropping",
        "error.drop_small_invalid": "Invalid --drop-small value '{value}': use auto, a number (0~1), or off/no/0",
        "convert.drop_small": "  [Clean] Dropped {count} small image(s): {names}",
        "run.drop_small_total": "Total small images dropped: {count}",
        "inspect.drop_small_preview": "  [Note] {count} small image(s) found (will be dropped when --drop-small is enabled)",
        "help.setinfo": "Set ComicInfo field (repeatable, FIELD=VALUE; VALUE supports %%series/%%number/%%title/%%filename/%%leftN/%%rightN; split on comma only when followed by FIELD=; use multiple --setinfo for a value containing Key=; Manga accepts Unknown/No/Yes/YesAndRightToLeft, not written by default; when enabled, existing .cbz inputs have their ComicInfo.xml modified in place)",
        "comicinfo.generating": "Generating ComicInfo.xml",
        "comicinfo.created": "ComicInfo.xml written",
        "comicinfo.disabled": "ComicInfo.xml disabled (--no-comicinfo)",
        "comicinfo.invalid": "ComicInfo.xml invalid or generation failed: {err}",
        "comicinfo.inferred": "inferred",
        "help.log": "Append all output to the given log file (omit filename to auto-generate a timestamped log)",
        "help.json": "Print a single-line compact JSON result to stdout (for AI/pipe consumption); suppresses human-readable text when enabled; only emitted after conversion or CBZ modification (not in dry-run/inspect/unpack); the progress bar writes to stderr and stays separate, but 2>&1 combined redirection mixes it in",
        "help.json_out": "Write conversion results to a JSON file (omit filename to auto-generate a timestamped file, or specify a path; like --json, only written in conversion/modify mode)",
        "log.auto_named": "Log file: {path} (auto-named)",
        "json.written": "JSON result written to: {path}",
        "help.unpack": "Unpack mode: extract only without converting, output to a same-named subdirectory next to the source (auto-append number if exists)",
        "unpack.done": "Unpacked {name} -> {dir}",
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
        "align.drop": "  [Info] {count} images in the directory were not collected, dropped per --drop-extra",
        "align.append": "  [Info] {count} images in the directory were not collected, appended to the end",
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
    "modify.done": "  [Modified] {name}: ComicInfo.xml updated",
    "modify.nochange": "  [Modified] {name}: no field changes, untouched",
    "modify.fail": "  [Failed] {name}: {err}",
    "modify.stats": "  Modify done: success {success}, unchanged {nochange}, failed {fail}",
    "modify.failed_reasons": "Modify failure reasons: {summary}",
    "modify.dryrun_end": "  Dry-run finished: no CBZ was actually modified",
    "progress.desc.modify": "Modifying",
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
        "help.target": '電子書籍ファイルのパス、または電子書籍（.mobi/.azw/.azw3/.epub）を含むディレクトリ',
        "help.delete": '変換成功後に元の電子書籍ファイルを削除',
        "help.prefer": '二重ディレクトリ mobi（mobi7/mobi8）がある場合にどちらを残すか：auto（デフォルト）は mobi8 優先、空なら mobi7 に自動フォールバック。mobi7/mobi8 指定時も、指定先が空ならもう一方に自動フォールバック',
        "help.ext_priority": '同じディレクトリで同名（拡張子のみ異なる）の場合にどの形式を残すか：カンマ区切り、順序が優先度（高→低）、mobi/azw/azw3/epub のみ指定可能、デフォルト azw3；優先度がカバーしない場合は azw3→epub→mobi→azw にフォールバック；--prefer（二重ディレクトリ選択）とは無関係',
        "help.drop_extra": 'ディレクトリ内で収集されなかった余分な画像を追加しない（デフォルトは cbz 末尾に追加）',
        "help.overwrite": '対象 cbz が既に存在する場合に強制的に再生成（デフォルトはスキップ）',
        "help.timeout": 'ファイルごとの変換タイムアウト秒数。タイムアウトで自動スキップし失敗に計上（デフォルト 600、0 は制限なし。タイムアウト後、基盤の解凍スレッドがバックグラウンドに残る可能性あり）',
        "help.min_size": '指定バイト数未満の電子書籍を除外；数字なしでデフォルト 1000 バイト、0 でサイズフィルタ無効、未指定で無効',
        "help.output_dir": "CBZ を指定ディレクトリに出力（自動作成）、デフォルトでは入力の相対サブディレクトリ構造を保持（例: One Piece/001.mobi → DIR/One Piece/001.cbz）、--flatten でルートにフラット化",
    "help.flatten": "--output-dir との併用時のみ：全 CBZ を出力ディレクトリのルートにフラット化、同名ファイルは --overwrite 指定時のみ上書き、未指定時はスキップ（SKIP）；単独使用はエラー終了",
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
        "help.double_page": "見開き検出：値なし/auto で有効（閾値 2.0）；数値で閾値調整；off/no/0 で無効（有効時はページ毎の DoublePage を書き込むが Manga 要素は書かない；Manga が必要なら --setinfo Manga= を使用）",
        "error.double_page_invalid": "無効な --double-page 値 '{value}'：auto/数値/off/no/0 のいずれか",
        "help.drop_small": "小画像を破棄：明らかに小さい画像を変換時に除外（幅・高さとも 中央値×比率 未満で小画像と判定；値なし/auto=0.5、0〜1 の数値で比率調整、off/no/0 で無効）。破棄後は PageCount を実画像数で再計算",
        "error.drop_small_invalid": "無効な --drop-small 値 '{value}'：auto/数値(0〜1)/off/no/0 のいずれか",
        "convert.drop_small": "  [クリーン] 小画像を {count} 枚破棄: {names}",
        "run.drop_small_total": "破棄した小画像の合計: {count} 枚",
        "inspect.drop_small_preview": "  [注意] 小画像が {count} 枚（--drop-small 有効時は破棄されます）",
        "help.setinfo": "ComicInfo フィールドを設定（複数可、形式 FIELD=VALUE；VALUE は %%series/%%number/%%title/%%filename/%%leftN/%%rightN をサポート；カンマ直後にフィールド名= がある場合のみ分割、値に Key= 構造が含まれる場合は --setinfo を複数回指定；Manga は Unknown/No/Yes/YesAndRightToLeft のみ有効、デフォルトでは書かない；--setinfo 有効時、入力中の既存 .cbz は ComicInfo.xml を直接変更）",
        "comicinfo.generating": "ComicInfo.xml を生成中",
        "comicinfo.created": "ComicInfo.xml を書き込みました",
        "comicinfo.disabled": "ComicInfo.xml は無効です（--no-comicinfo）",
        "comicinfo.invalid": "ComicInfo.xml が無効、または生成に失敗しました: {err}",
        "comicinfo.inferred": "推定",
        "help.log": 'すべての出力を指定ログファイルに追記（ファイル名を省略するとタイムスタンプ付きログを自動生成）',
        "help.json": '単一行のコンパクトな JSON 結果を stdout に出力（AI/パイプ読み取り用）。有効時は人間向けテキスト出力を抑制。変換または CBZ 変更の実行後にのみ出力（dry-run/inspect/unpack では出力しない）。プログレスバーは stderr に書き込まれ JSON と混ざらないが、2>&1 で結合リダイレクトすると混入する',
        "help.json_out": '変換結果を JSON ファイルに書き出し（ファイル名省略でタイムスタンプ付きファイルを自動生成、またはパス指定。--json と同様、変換/変更モードのみ書き込み）',
        "log.auto_named": 'ログファイル: {path}（自動命名）',
        "json.written": 'JSON 結果を書き込みました: {path}',
        "help.unpack": '解凍モード：解凍のみで変換は行わず、元ファイルと同じディレクトリの同名サブディレクトリに出力（既存の場合は自動で番号を付与）',
        "unpack.done": '解凍しました {name} -> {dir}',
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
        "dedupe.auto_fallback": '  [重複除去] 二重ディレクトリ、mobi8 が空のため mobi7 に自動フォールバック',
        "dedupe.prefer_empty_fallback": '  [重複除去] {prefer} を指定したが画像なし、{fallback} に自動フォールバック',
        # ---- 目录对齐 ----
        "align.drop": '  [情報] ディレクトリ内の未収集画像 {count} 枚を --drop-extra により破棄',
        "align.append": '  [情報] ディレクトリ内の未収集画像 {count} 枚を末尾に追加',
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
    "modify.done": '  [変更] {name}: ComicInfo.xml を更新しました',
    "modify.nochange": '  [変更] {name}: フィールド変更なし、変更なし',
    "modify.fail": '  [失敗] {name}: {err}',
    "modify.stats": '  変更完了：成功 {success}、変更なし {nochange}、失敗 {fail}',
    "modify.failed_reasons": '変更失敗理由: {summary}',
    "modify.dryrun_end": '  試行終了：実際にはどの CBZ も変更されていません',
    "progress.desc.modify": '変更中',
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
SUPPORTED_INPUT_EXTENSIONS = {".mobi", ".azw", ".azw3", ".epub"}
KEEP_EXT_ORDER = (".azw3", ".epub", ".mobi", ".azw")  # --ext-priority 未覆盖时的兜底顺序


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
    if _log_path:
        try:
            with open(_log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            if not _log_write_failed:
                _log_write_failed = True
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + t("error.log_write_failed", err=e, path=_log_path))
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
def collect_ebook_files(target: Path, include_cbz: bool = False) -> list[Path]:
    """收集所有待转换的电子书文件（.mobi/.azw/.azw3/.epub），按路径排序保证处理顺序可预测。

    include_cbz=True 时（--inspect / --unpack / --setinfo 模式）额外收集 .cbz，供检查或修改。"""
    exts = SUPPORTED_INPUT_EXTENSIONS | ({".cbz"} if include_cbz else set())
    if target.is_file():
        if target.suffix.lower() in exts:
            return [target]
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
      KEEP_EXT_ORDER（azw3→mobi→azw）。
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


    # 输入：源电子书路径、输出目录、是否平铺、相对基准与已占用名集合；输出：目标 cbz 绝对路径
def sanitize_filename_component(name: str) -> str:
    """替换 Windows 文件名非法字符（<>:"/\|?*）与 ASCII 控制字符（\x00-\x1f\x7f）为下划线，
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


def target_cbz_path(ebook_path: Path, output_dir: Path | None, flatten: bool = False, input_root: Path | None = None, used_names: set | None = None) -> Path:
    """计算目标 cbz 路径。

    - output_dir 为 None：与源电子书同目录（历史行为）
    - output_dir + flatten=False：保留相对 input_root 的子目录结构；
      相对路径计算失败（跨盘符等）时回退 output_dir/stem.cbz 并输出 warning
    - output_dir + flatten=True：平铺到 output_dir 根下，返回首选目标名
      output_dir/base.cbz（不唯一化）；同名文件由上层按 SKIP/--overwrite 处理，
      used_names 由调用方在确认占用后登记（本函数不修改）
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
            # 与 HtmlImgParser 兜底路径一致：统一 unquote 处理 %XX 百分号编码
            srcs = [unquote(s) for s in srcs]
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
def ebook_to_cbz(ebook_path: Path, delete_original: bool = False, prefer: str = "mobi8", drop_extra: bool = False, overwrite: bool = False, output_dir: Path | None = None, compress: int = 0, flatten: bool = False, input_root: Path | None = None, comicinfo: bool = True, setinfo_args: list | None = None, double_page: float | None = None, drop_small: float | None = None) -> tuple[Path | None, ConvStatus, str | None, dict | None]:
    """将单个电子书文件转换为 cbz

    prefer: "auto"（默认）双目录时优先 mobi8，mobi8 为空壳（无图片）自动回退 mobi7
    drop_extra: 目录中有未被收集的多余图片时放弃追加，默认追加到末尾
    overwrite: 目标 cbz 已存在时强制重新生成（默认跳过）
    output_dir: 指定 CBZ 输出目录（自动创建），默认与源 mobi 同目录
    flatten: 与 output_dir 联用时平铺到输出目录根下（默认保留相对子目录结构）
    input_root: target 为目录时作为相对子目录结构计算的基准
    comicinfo: 是否生成 ComicInfo.xml（默认生成，--no-comicinfo 关闭）
    double_page: 双页检测阈值（宽/高 >= 该值判为跨页），None 表示关闭（--double-page off）
    drop_small: 丢弃小图比例（宽和高均 < 中位数×该值 判为小图），None 表示关闭（--drop-small off）

    返回 (结果, 状态, 原因, 来源)：状态为 ConvStatus 枚举，
    - OK: 转换成功，结果为 cbz 路径，原因为 None，来源为 {series_source/number_source/cover_source/dropped_small} 字典
    - SKIP: 目标已存在且未指定 --overwrite，结果为 None，原因为 None，来源为 None
    - FAIL: 转换失败，结果为 None，原因为失败分类（no_images/drm/comicinfo/verify/other），来源为 None
    """
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
        total_in_dir = count_images_in_dir(base_dir)
        images, align_msg = align_images_with_dir(images, base_dir, drop_extra)
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

        # 丢弃小图（--drop-small）：宽和高均 < 中位数×比例 判为小图（封面缩略图等）
        dropped_small = 0
        if drop_small is not None:
            images, dropped_names = drop_small_images(images, drop_small)
            dropped_small = len(dropped_names)
            if dropped_names:
                emit(t("convert.drop_small", count=dropped_small, names=", ".join(dropped_names)))

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

        # Step 3.6: 生成 ComicInfo.xml（默认启用，--no-comicinfo 关闭）
        comicinfo_xml = None
        conv_sources = None
        if comicinfo:
            try:
                opf_meta = read_opf_metadata(opf_path) if opf_path else {}
                exth_meta = read_exth_metadata(ebook_path)
                meta = collect_comicinfo_meta(opf_meta, exth_meta, ebook_path)
                inferred = infer_series_number(ebook_path)
                setinfo = parse_setinfo_args(setinfo_args, meta, inferred, ebook_path)
                built = build_comicinfo(meta, images, inferred, setinfo, cover_source=cover_source, double_page=double_page)
                if built is not None:
                    comicinfo_xml, conv_sources = built
                else:
                    comicinfo_xml = None
            except Exception:
                comicinfo_xml = None
            if comicinfo_xml is None:
                emit(t("comicinfo.invalid", err="build"), level="error")
                # 不删除已有目标：元数据生成失败不应毁掉磁盘上原有的有效 CBZ
                return None, ConvStatus.FAIL, "comicinfo", None
            emit(t("comicinfo.generating"))

        # Step 4: 打包为 cbz（默认 ZIP 无压缩，图片本身已压缩；--compress 1-9 启用 deflate）
        # v2.2.1 原子替换：先写 cbz.tmp，全部成功后 os.replace，避免中途崩溃残留残缺 CBZ
        tmp_cbz = cbz_path.with_name(cbz_path.name + ".tmp")
        seen = {}
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
                if img.name in seen:
                    # 重名：用序号前缀 + 原文件名，保证顺序且不冲突
                    arcname = f"{idx:04d}_{img.name}"
                else:
                    arcname = img.name
                    seen[img.name] = arcname
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
            emit(t("comicinfo.invalid", err=comicinfo_failed), level="error")
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
                shutil.rmtree(p, ignore_errors=True)
        # KeyboardInterrupt（Ctrl+C）不被 except Exception 捕获，此处兜底清理半成品 tmp_cbz
        if tmp_cbz is not None and tmp_cbz.exists():
            tmp_cbz.unlink(missing_ok=True)


def _safe_zip_extract(zf: zipfile.ZipFile, out_dir: Path) -> None:
    """将 zip 内条目安全解压到 out_dir（含 zip-slip 路径穿越防护）。

    cbz / epub 共用；拒绝绝对路径与 .. 跳转条目，目录条目仅建目录。"""
    for member in zf.infolist():
        name = member.filename
        # 路径穿越防护：拒绝绝对路径与 .. 跳转，防止 zip-slip
        norm_name = name.replace("\\", "/")
        if norm_name.startswith("/") or ".." in norm_name.split("/"):
            emit(t("unpack.path_skip", name=Path(zf.filename).name, entry=name), level="warning")
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
    损坏 zip 由 zipfile.BadZipFile 抛出（走转换失败分类 corrupt）。"""
    tempdir = Path(tempfile.mkdtemp(prefix="manga_mobi2cbz_epub_"))
    with zipfile.ZipFile(str(epub_path)) as zf:
        _safe_zip_extract(zf, tempdir)
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


# 中文数字（一/二/…/十/百）转阿拉伯数字，无法解析返回 None
_CN_DIGITS = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def _cn_to_int(s: str) -> int | None:
    """把中文数字（如 "十二" / "二十" / "五"）转为阿拉伯数字，无法解析返回 None。"""
    s = s.strip()
    if not s or not all(c in "一二三四五六七八九十百零两" for c in s):
        return None
    total, section = 0, 0
    for c in s:
        if c in _CN_DIGITS:
            section = _CN_DIGITS[c]
        elif c == "十":
            total += (section if section else 1) * 10
            section = 0
        elif c == "百":
            total += (section if section else 1) * 100
            section = 0
        else:  # 零
            section = 0
    total += section
    return total or None


# 卷标记模式表：(正则, 类别)。系列名在 ?P<series>，数字在 ?P<num> 或 ?P<cn>。
# 覆盖 Vol/Volume/v1、第N卷、卷N（前缀式）、01巻/第1巻、第5册/册N、
# tome N、권N、시즌 N、เล่ม N、Том N、中文数字卷（第一卷/卷二）。
_VOLUME_PATTERNS = [
    (r"^(?P<series>.*?)[\s_\-\.]*[Vv]ol(?:ume)?[\s_\-\.]*(?P<num>\d{1,4}(?:\.\d+)?)\s*$", "vol"),
    (r"^(?P<series>.*?)[\s_\-\.]*[Vv][\s_\-\.]*(?P<num>\d{1,4})\s*$", "v"),
    (r"^(?P<series>.*?)[\s_\-\.]*第[\s_\-\.]*(?P<num>\d{1,4})[\s_\-\.]*卷\s*$", "cn"),
    (r"^(?P<series>.*?)[\s_\-\.]*卷[\s_\-\.]*(?P<num>\d{1,4})\s*$", "cn"),
    (r"^(?P<series>.*?)[\s_\-\.]*第?[\s_\-\.]*(?P<num>\d{1,4})[\s_\-\.]*巻\s*$", "jp"),
    (r"^(?P<series>.*?)[\s_\-\.]*巻[\s_\-\.]*(?P<num>\d{1,4})\s*$", "jp"),
    (r"^(?P<series>.*?)[\s_\-\.]*第?[\s_\-\.]*(?P<num>\d{1,4})[\s_\-\.]*[册冊]\s*$", "cn"),
    (r"^(?P<series>.*?)[\s_\-\.]*[Tt](?:ome)?[\s_\-\.]*(?P<num>\d{1,4})\s*$", "fr"),
    (r"^(?P<series>.*?)[\s_\-\.]*권[\s_\-\.]*(?P<num>\d{1,4})\s*$", "ko"),
    (r"^(?P<series>.*?)[\s_\-\.]*시즌[\s_\-\.]*(?P<num>\d{1,4})\s*$", "ko"),
    (r"^(?P<series>.*?)[\s_\-\.]*เล่มที่?[\s_\-\.]*(?P<num>\d{1,4})\s*$", "th"),
    (r"^(?P<series>.*?)[\s_\-\.]*Том(?:а)?[\s_\-\.]*(?P<num>\d{1,4})\s*$", "ru"),
    (r"^(?P<series>.*?)[\s_\-\.]*第?[\s_\-\.]*(?P<cn>[一二三四五六七八九十百零两]+)[\s_\-\.]*[卷巻]\s*$", "cn_cn"),
    (r"^(?P<series>.*?)[\s_\-\.]*[卷巻][\s_\-\.]*(?P<cn>[一二三四五六七八九十百零两]+)\s*$", "cn_cn"),
]


# 输入：电子书文件路径；输出：(series, number) 高置信度推断结果，无法判断返回 (None, None)
def infer_series_number(path: Path) -> tuple[str | None, str | None]:
    """从文件名高置信度推断漫画 Series/Number。

    支持形式：001 / 01 / 1 / Vol.01 / Vol 01 / Volume 01 / v1 / 第 01 卷 /
    卷12（前缀式）/ 01巻 / 第5册 / tome 2 / 권N / เล่มN / ТомN / 第一卷
    （中文数字卷）等；纯数字结尾（如 "One Piece 108"）也视为高置信度。
    文件名可带括号后缀（如 "天是紅河岸 - 第23卷 (筱原千繪)"），
    括号内容不影响推断。4 位年份（19xx/20xx）与纯数字文件名
    （如 "108"）会被排除，宁缺勿错；无系列名的纯卷标记
    （如 "Vol.01" / "第 01 卷" / "01巻"）只返回卷号 (None, number)。
    """
    name = path.name
    if not name:
        return None, None
    # 用 name 而非 stem：Path.stem 会把 "Vol.01" 的 ".01" 当扩展名吞掉，
    # 导致点号卷号（Vol.01）无法匹配；这里仅去掉已知电子书扩展名
    stem = name
    for ext in SUPPORTED_INPUT_EXTENSIONS:
        if name.lower().endswith(ext):
            stem = name[: -len(ext)]
            break
    s = stem.strip()
    # 括号后缀（如 "(作者)" / "(scan)"）不影响推断，统一剥离
    s = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    # 1) 各类卷标记（含前缀式、多语言与中文数字卷）
    for pattern, kind in _VOLUME_PATTERNS:
        m = re.match(pattern, s)
        if not m:
            continue
        series = m.group("series").strip()
        if "num" in m.groupdict() and m.group("num"):
            num_raw = m.group("num")
            num = num_raw if "." in num_raw else str(int(float(num_raw)))
        else:
            cn = _cn_to_int(m.group("cn"))
            if cn is None:
                continue
            num = str(cn)
        if not series or _is_volume_marker(series):
            return None, num
        return series, num
    # 2) 纯数字结尾（空格/连字符/下划线/点分隔）：如 "One Piece 108"
    m = re.match(r"^(?P<series>.+?)[\s_\-\.]+(\d{1,4})$", s)
    if m:
        num = m.group(2)
        if len(num) == 4 and 1900 <= int(num) <= 2100:
            return None, None  # 疑似年份，宁缺勿错
        series = m.group("series").strip()
        if not series:
            return None, None  # 纯数字文件名，无法判断
        if _is_volume_marker(series):
            return None, str(int(num))
        return series, str(int(num))
    return None, None


# 输入：聚合后的元数据字典 + 最终图片列表 + (series, number) 推断结果；输出：ComicInfo.xml 文本或 None
def _resolve_setinfo_value(raw: str, series, number, title, stem) -> str | None:
    """解析 --setinfo 值中的占位符：%series/%number/%title/%filename/%leftN/%rightN。

    占位符对应值缺失时返回 None（该字段不写入）；未知占位符按固定值原样返回。"""
    if not raw.startswith("%"):
        return raw
    token = raw[1:]
    if token == "series":
        return series
    if token == "number":
        return number
    if token == "title":
        return title
    if token == "filename":
        return stem
    m = re.match(r"^(left|right)(\d+)$", token)
    if m:
        side, n = m.group(1), int(m.group(2))
        if side == "left":
            return stem[:n]
        return stem[-n:] if n > 0 else ""
    emit(t("setinfo.unknown_placeholder", raw=raw), level="warning")
    return raw


# ComicInfo.xml v2.0/v2.1 标准简单字段白名单（42 个；Pages 为复杂结构不纳入）
COMICINFO_WHITELIST = {
    "Title", "Series", "Number", "Count", "Volume", "AlternateSeries",
    "AlternateNumber", "AlternateCount", "StoryArc", "StoryArcNumber",
    "SeriesGroup", "Genre", "Tags", "Writer", "Penciller", "Inker",
    "Colorist", "Letterer", "CoverArtist", "Editor", "Publisher",
    "Imprint", "Web", "PageCount", "LanguageISO", "Format", "AgeRating",
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
    series, number = inferred if isinstance(inferred, tuple) else (None, None)
    stem = ebook_path.stem
    title = meta.get("title") or stem
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
            value = _resolve_setinfo_value(raw, series, number, title, stem)
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


def build_comicinfo(meta: dict, images: list, inferred: tuple, setinfo: dict | None = None,
                    cover_source: str | None = None, double_page: float | None = None) -> tuple[str, dict] | None:
    """用 xml.etree.ElementTree 生成 ComicInfo.xml（禁止手工拼接字符串）。

    PageCount 必写（=最终写入 CBZ 的实际图片数）；其余字段有可靠来源
    才写入，无来源直接省略，不生成空标签。setinfo 为 --setinfo 解析结果，
    优先级最高（覆盖 meta 与 inferred）。
    double_page 非 None 时为双页检测阈值（图片宽/高 >= 该值判为跨页）：
    生成 <Pages> 逐页 DoublePage 标记；Manga 声明不再自动写入（改由 --setinfo
    Manga= 显式指定，官方 v2.0 枚举 Unknown/No/Yes/YesAndRightToLeft）；
    None 时不生成 <Pages>。
    CoverSource 不再写入 Notes（来源改由 --inspect / --json 展示，避免污染 ComicInfo）。

    返回 (xml 文本, sources)：sources 记录 series/number/cover 三者来源
    （series_source/number_source: setinfo/opf/inferred；cover_source: OPF guide/filename/spine/first），
    供 --json 输出；xml 生成失败返回 None。
    """
    try:
        root = ET.Element("ComicInfo")
        setinfo = setinfo or {}
        inferred_s, inferred_n = inferred if isinstance(inferred, tuple) else (None, None)
        # 优先级：setinfo（用户指定）> meta（OPF 元数据）> inferred（文件名推测）
        series = setinfo.get("Series") or meta.get("series") or inferred_s
        number = setinfo.get("Number") or meta.get("number") or inferred_n
        series_source = ("setinfo" if setinfo.get("Series")
                         else ("opf" if meta.get("series") else ("inferred" if inferred_s else None)))
        number_source = ("setinfo" if setinfo.get("Number")
                         else ("opf" if meta.get("number") else ("inferred" if inferred_n else None)))
        notes = setinfo.get("Notes")
        ordered = [
            ("Title", setinfo.get("Title", meta.get("title"))),
            ("Series", series),
            ("Number", number),
            ("Writer", setinfo.get("Writer", meta.get("writer"))),
            ("Publisher", setinfo.get("Publisher", meta.get("publisher"))),
            ("Year", setinfo.get("Year", meta.get("year"))),
            ("LanguageISO", setinfo.get("LanguageISO", meta.get("language"))),
            ("PageCount", str(len(images))),
            ("Summary", _strip_html(setinfo.get("Summary", meta.get("summary")))),
            ("Notes", notes),
            # 官方简单字段：仅 setinfo 显式指定时写入（Manga 默认不写，避免无跨页也声明）
            ("Manga", setinfo.get("Manga")),
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
                page.set("Image", img.name)
                dim = image_dimensions(img)
                if dim and dim[0] > 0 and dim[1] > 0 and dim[0] / dim[1] >= double_page:
                    page.set("Type", "DoublePage")
        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        sources = {
            "series_source": series_source,
            "number_source": number_source,
            "cover_source": cover_source,
        }
        return xml_bytes.decode("utf-8"), sources
    except Exception:
        return None


def get_drm_flag(p: Path) -> bool:
    """读取 PalmDB 头偏移 12 处的加密字段，非 0 表示 DRM 加密"""
    if p.suffix.lower() == ".epub":
        return False
    try:
        with open(p, "rb") as f:
            f.seek(12)
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
            head = f.read(65536)
    except Exception:
        return None
    return image_dimensions_bytes(head)


def get_opf_guide_cover_href(opf_path: Path) -> str | None:
    """解析 OPF 文件中的封面引用（返回 href 字符串），命中优先级：

    1. <guide><reference type="cover" href="...">
    2. <manifest><item properties="cover-image" href="...">（EPUB3 约定）
    3. <meta name="cover" content="{id}"> 对应的 manifest item href（EPUB2 约定）

    全程文本正则扫描（兼容属性顺序互换、无命名空间 OPF），均未命中返回 None。"""
    try:
        text = opf_path.read_text("utf-8", errors="replace")
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
            tree = ET.parse(opf_path)
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
def inspect_ebook(p: Path, min_bytes: int, prefer: str = "mobi8", setinfo_args: list | None = None, drop_small: float | None = None) -> str:
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
                    emit(t("inspect.drm_bad_hint"), level="summary")
                    return "noimg"
                emit(t("inspect.drm_none", count=total_in_dir))

                # 封面检测：文件名扫描
                cover = None
                for n in img_names:
                    if any(k in Path(n).name.lower() for k in COVER_KEYWORDS):
                        cover = n
                        break
                if cover:
                    try:
                        cdata = zf.read(cover)[:65536]
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
                        data = zf.read(n)[:65536]
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

                # 压缩建议
                jpeg_ratio = (fmt_counter.get("jpg", 0) + fmt_counter.get("jpeg", 0)) / total_fmt
                png_ratio = fmt_counter.get("png", 0) / total_fmt
                if png_ratio >= 0.5:
                    emit(t("inspect.adv_png"))
                elif jpeg_ratio >= 0.8:
                    emit(t("inspect.adv_jpeg"))
                else:
                    emit(t("inspect.adv_mixed"))

                # ComicInfo.xml 预览（若存在）
                if "ComicInfo.xml" in names:
                    try:
                        root = ET.fromstring(zf.read("ComicInfo.xml"))
                        emit("ComicInfo.xml:")
                        for tag in ("Title", "Series", "Number", "Writer", "Publisher", "Year", "LanguageISO", "PageCount", "Summary"):
                            node = root.find(tag)
                            if node is not None and node.text:
                                emit(f"  {tag}: {node.text}")
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
                return "ok"
        except Exception as e:
            emit(t("inspect.unpack_fail", err=e), level="summary")
            return "fail"

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

        ncx_count, ncx_preview = parse_ncx_toc(base_dir)
        if ncx_count:
            emit(t("inspect.ncx_count", count=ncx_count, preview=" | ".join(ncx_preview)))
        else:
            emit(t("inspect.ncx_missing"))
        nav_count, nav_preview = parse_nav_toc(base_dir)
        if nav_count:
            emit(t("inspect.nav_count", count=nav_count, preview=" | ".join(nav_preview)))
        else:
            emit(t("inspect.nav_missing"))

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

        # 丢弃小图预览：开启 --drop-small 时会丢弃多少张（仅提示，不改变转换）
        if drop_small is not None and len(res_list) > 1:
            med_w = statistics.median(d[0] for d in res_list)
            med_h = statistics.median(d[1] for d in res_list)
            small_n = sum(1 for w, h in res_list if w < med_w * drop_small and h < med_h * drop_small)
            if small_n:
                emit(t("inspect.drop_small_preview", count=small_n))

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
        # 来源标注与 build_comicinfo 优先级一致：setinfo > OPF 元数据 > 文件名推断
        cinf_s, cinf_n = infer_series_number(p)
        csetinfo = parse_setinfo_args(setinfo_args or [], cmeta, (cinf_s, cinf_n), p)
        series_src = "setinfo" if "Series" in csetinfo else ("opf" if cmeta.get("series") else ("inferred" if cinf_s else None))
        number_src = "setinfo" if "Number" in csetinfo else ("opf" if cmeta.get("number") else ("inferred" if cinf_n else None))
        cseries = csetinfo.get("Series") or cmeta.get("series") or cinf_s
        cnumber = csetinfo.get("Number") or cmeta.get("number") or cinf_n
        emit("ComicInfo.xml:")
        if csetinfo.get("Title") or cmeta.get("title"):
            emit(f"  Title: {csetinfo.get('Title') or cmeta.get('title')}")
        if cseries:
            emit(f"  Series: {cseries} [{series_src}]")
        if cnumber:
            emit(f"  Number: {cnumber} [{number_src}]")
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
        return "ok"
    except Exception as e:
        emit(t("inspect.unpack_fail", err=e), level="summary")
        return "fail"
    finally:
        for tp in extract_temp_paths:
            if tp.exists():
                shutil.rmtree(tp, ignore_errors=True)


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
        root = ET.fromstring(existing_data)
    else:
        root = ET.Element("ComicInfo")
        pc = ET.SubElement(root, "PageCount")
        pc.text = str(img_count)

    # 解析 setinfo：无 EXTH/OPF 元数据，meta 传空；占位符可从文件名推断（%number 等）
    setinfo = parse_setinfo_args(setinfo_args, {}, infer_series_number(cbz_path), cbz_path)
    changed = False
    for field, value in setinfo.items():
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


def modify_cbz_mode(cbz_files: list[Path], args) -> None:
    """--setinfo 修改已有 CBZ 的 ComicInfo.xml 模式入口。

    纳入 --dry-run / 进度条 / 汇总统计 / --log。
    """
    total_start = time.perf_counter()
    emit(t("modify.header", count=len(cbz_files)), level="summary")
    if args.dry_run:
        pbar = create_progress_if_needed(args, cbz_files, t("progress.desc.modify"))
        try:
            for mf in cbz_files:
                if pbar is not None:
                    pbar.set_postfix_str(truncate_name(mf.name))
                # dry-run 也做一次只读解析，触发白名单外字段 warning（不写盘）
                parse_setinfo_args(args.setinfo, {}, infer_series_number(mf), mf)
                emit(t("modify.plan", name=mf.name), level="summary")
                if pbar is not None:
                    pbar.update(1)
        finally:
            if pbar is not None:
                pbar.close()
        emit(t("modify.dryrun_end"), level="summary")
        return

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


def unpack_ebook(p: Path, out_root: Path) -> Path:
    """解包电子书到 out_root 下的同名子目录（已存在自动加序号避让）。

    mobi 走 mobi.extract 保留完整结构（mobi7/mobi8 等），cbz/epub 逐条目
    安全解压（含 zip-slip 路径穿越防护）。返回实际解包到的目录。
    """
    out_dir = out_root / p.stem
    n = 2
    while out_dir.exists():
        out_dir = out_root / f"{p.stem} ({n})"
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
            shutil.rmtree(str(tempdir), ignore_errors=True)
    return out_dir


def unpack_mode(ebook_files: list[Path], args) -> None:
    """--unpack 模式入口：只解包不转换，输出到各源文件所在目录的同名子目录。"""
    for mf in ebook_files:
        try:
            out_dir = unpack_ebook(mf, mf.parent)
            emit(t("unpack.done", name=mf.name, dir=out_dir))
        except Exception as e:
            emit(t("inspect.unpack_fail", err=e), level="error")


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
            timed_out, result = run_with_timeout(inspect_ebook, args.timeout, mf, args.min_size, args.prefer, args.setinfo, args.drop_small)
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


def drop_small_images(images: list[Path], ratio: float) -> tuple[list[Path], list[str]]:
    """丢弃尺寸明显偏小的图片：宽和高均 < 中位数×ratio 判为小图（--drop-small）。

    保持原顺序返回保留列表；无法解析尺寸的图片一律保留（不误删）。
    返回 (保留列表, 被丢弃文件名列表)。
    """
    if len(images) < 2:
        return images, []
    dims = [image_dimensions(img) for img in images]
    valid = [d for d in dims if d]
    if not valid:
        return images, []
    med_w = statistics.median(d[0] for d in valid)
    med_h = statistics.median(d[1] for d in valid)
    kept, dropped = [], []
    for img, d in zip(images, dims):
        if d and d[0] < med_w * ratio and d[1] < med_h * ratio:
            dropped.append(img)
        else:
            kept.append(img)
    return kept, [p.name for p in dropped]


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
    # 输入：双页检测（nargs='?'，可选值）；输出：ComicInfo 写入 <Manga>Yes</Manga> 与逐页 DoublePage 标记
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
    # 输入：丢弃小图（nargs='?'，可选值）；输出：转换时剔除尺寸明显偏小的图片（宽和高均 < 中位数×比例）
    # 取值：不传/auto → 开启（比例 0.5）；0~1 数值 → 开启并调比例；off/no/0/false → 关闭
    parser.add_argument(
        "--drop-small",
        nargs="?",
        const="auto",
        default=None,
        metavar="VALUE",
        type=_parse_drop_small_arg,
        help=t("help.drop_small"),
    )
    # 输入：设置 ComicInfo 字段（可多次）；输出：覆盖/新增对应字段
    parser.add_argument(
        "--setinfo",
        action="append",
        default=[],
        metavar="FIELD=VALUE",
        help=t("help.setinfo"),
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
    # 输入：是否解包查看；输出：只解压不转换，输出到源文件所在目录的同名子目录
    parser.add_argument(
        "--unpack",
        action="store_true",
        help=t("help.unpack"),
    )
    return parser


def _main():
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

    global _quiet_mode, _log_path, _short_summary, _compress_level, _json_stdout, _json_out_path
    _quiet_mode = args.quiet
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

    ebook_files = collect_ebook_files(target, include_cbz=args.inspect or args.unpack or bool(args.setinfo))
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

    if precheck_skipped and not args.dry_run and not args.inspect and not args.unpack:
        emit(t("run.precheck_header", count=len(precheck_skipped)), level="summary")
        if not _short_summary:
            for mf, reason in precheck_skipped:
                emit("  " + t("skip_entry", path=str(mf), reason=reason), level="summary")

    if args.unpack:
        unpack_mode(ebook_files, args)
        return

    if args.inspect:
        inspect_mode(ebook_files, precheck_skipped, args)
        return

    # #36 CBZ 修改模式：--setinfo 且输入为已有 CBZ 时，直接修改其 ComicInfo.xml
    cbz_modify_files = [f for f in ebook_files if f.suffix.lower() == ".cbz"]
    ebook_files = [f for f in ebook_files if f.suffix.lower() != ".cbz"]
    if cbz_modify_files:
        modify_cbz_mode(cbz_modify_files, args)

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
                will_skip = (out.exists() or str(out) in used_names) and not args.overwrite
                state_tag = t("tag.will_skip") if will_skip else t("tag.pending")
                if not will_skip:
                    used_names.add(str(out))
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
            timed_out, converted = run_with_timeout(
                ebook_to_cbz, args.timeout,
                mf, delete_original=args.delete, prefer=args.prefer,
                drop_extra=args.drop_extra, overwrite=args.overwrite,
                output_dir=output_dir, compress=_compress_level,
                flatten=args.flatten, input_root=input_root,
                comicinfo=not args.no_comicinfo, setinfo_args=args.setinfo,
                double_page=args.double_page, drop_small=args.drop_small,
            )
            file_elapsed = time.perf_counter() - file_start
            json_status = "ok"
            json_target = None
            json_reason = None
            conv_sources = None
            if timed_out:
                emit(t("run.timeout", name=mf.name, seconds=args.timeout), level="error")
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
            json_files.append({
                "source": str(mf),
                "status": json_status,
                "target": json_target,
                "reason": json_reason,
                "elapsed_sec": round(file_elapsed, 3),
                "series_source": conv_sources.get("series_source"),
                "number_source": conv_sources.get("number_source"),
                "cover_source": conv_sources.get("cover_source"),
                "dropped_small": conv_sources.get("dropped_small"),
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


if __name__ == "__main__":
    main()
