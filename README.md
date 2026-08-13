# manga-mobi2cbz

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
