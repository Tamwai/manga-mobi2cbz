# -*- coding: utf-8 -*-
"""manga-mobi2cbz 回归测试。

覆盖：多语言别名 / [] 粘贴 / 与或表达式 / 标签与文件名原子 / 处置筛选
      / overscale 标记回填 / 转换链路与 list 侧标记一致性（源码护栏）。
不依赖 PIL，纯单元断言 + inspect 源码护栏。运行：
    python tests/test_mobi2cbz.py
"""
import importlib.util
import inspect
import subprocess
import sys
import tempfile
import types
import unittest
import zipfile
from argparse import ArgumentTypeError
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "manga-mobi2cbz.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("_mobi2cbz_under_test", MAIN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
parse_atom = mod._parse_atom
parse_drop_expr = mod.parse_drop_expr
parse_inspect_arg = mod.parse_inspect_arg
extract_small_ratio = mod.extract_small_ratio
eval_atom = mod.eval_filter_atom
fill_small = mod._fill_small_mark
fill_overscale = mod._fill_overscale_mark
DEFAULT_DROP_SMALL_RATIO = mod.DEFAULT_DROP_SMALL_RATIO


def mkattrs(**kw):
    """手搓图片属性 dict，避免依赖真实文件。"""
    d = {"path": "x.jpg", "zname": None, "ext": "jpg", "w": 100, "h": 150,
         "mode": "rgb", "depth": 24, "size": 1000, "dir": "portrait",
         "mark": set(), "extra": False, "cover": False, "cover_extra": False,
         "filter_hit": False, "disposition": None, "anom": False}
    d.update(kw)
    return d


def _make_mini_epub(d: Path, broken: bool = False) -> Path:
    """构造自包含最小 epub（1 张 1x1 PNG，无外部依赖）；broken=True 截断为损坏样本。

    broken 样本保留 PK 魔数头部、截断正文：可通过 precheck（只查魔数），
    但解包必然失败，从而计入转换失败（failed_files），用于退出码 1 场景。
    """
    png = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000d4944415478da63fcffff3f030005fe02fea73d5d900000000049454e44ae426082")
    opf = (
        '<?xml version="1.0"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">\n'
        ' <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        '  <dc:title>Mini Test</dc:title>\n'
        '  <dc:language>zh</dc:language>\n'
        ' </metadata>\n'
        ' <manifest>\n'
        '  <item id="p1" href="p1.xhtml" media-type="application/xhtml+xml"/>\n'
        '  <item id="img" href="img.png" media-type="image/png"/>\n'
        ' </manifest>\n'
        ' <spine><itemref idref="p1"/></spine>\n'
        '</package>')
    xh = ('<?xml version="1.0" encoding="utf-8"?>\n'
          '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>t</title></head>'
          '<body><p>hi</p><img src="img.png"/></body></html>')
    ep = d / ("broken.epub" if broken else "mini.epub")
    with zipfile.ZipFile(ep, "w") as z:
        z.writestr("mimetype", "application/epub+zip")
        z.writestr("content.opf", opf)
        z.writestr("p1.xhtml", xh)
        z.writestr("img.png", png)
    if broken:
        head = ep.read_bytes()[:256]
        ep.write_bytes(head)
    return ep


def _run_cli(*args) -> subprocess.CompletedProcess:
    """子进程运行主脚本，返回 CompletedProcess（UTF-8 解码防中文崩溃）。"""
    return subprocess.run(
        [sys.executable, str(MAIN), *args],
        capture_output=True, encoding="utf-8", errors="replace",
    )


class TestMultiLangAlias(unittest.TestCase):
    """四语别名 + [] 粘贴 + 大小写不敏感。"""

    def _check(self, alias, expect):
        got = parse_atom(alias)
        self.assertIsNotNone(got, f"alias 未解析: {alias!r}")
        self.assertEqual(got, expect, f"alias={alias!r}")

    def test_cover(self):
        for a in ("cover", "COVER", "Cover", "封面", "表紙", "[封面]", "[cover]"):
            self._check(a, ("mark", "cover"))

    def test_double(self):
        for a in ("double", "双页", "雙頁", "見開き", "[双页]", "[雙頁]"):
            self._check(a, ("mark", "double"))

    def test_overscale(self):
        for a in ("overscale", "超大页", "超大頁", "特大ページ", "[超大页]"):
            self._check(a, ("mark", "overscale"))

    def test_rotated_double(self):
        for a in ("rotated_double", "疑似旋转跨页", "疑似旋轉跨頁",
                  "縦向き見開き", "回転見開き", "[疑似旋转跨页]"):
            self._check(a, ("mark", "rotated_double"))

    def test_anom(self):
        for a in ("anom", "异常", "異常", "[异常]"):
            self._check(a, ("mark", "anom"))

    def test_disposition(self):
        for a in ("append", "追加", "[追加]"):
            self._check(a, ("mark", "append"))
        for a in ("drop", "舍弃", "捨棄", "破棄", "[舍弃]"):
            self._check(a, ("mark", "drop"))
        for a in ("filter", "filtered", "筛选", "篩選", "フィルタ", "[筛选]"):
            self._check(a, ("mark", "filter"))

    def test_existing_atoms_unchanged(self):
        for a in ("jpg", "gif", "extra", "landscape", "portrait", "square",
                  "gray", "rgb", "index", "8bit", "24bit", "thumbnail", "small",
                  "animated"):
            self.assertIsNotNone(parse_atom(a), f"原有词不应被破坏: {a!r}")

    def test_name_atom(self):
        self.assertEqual(parse_atom("name=cover"), ("name", "cover"))
        self.assertEqual(parse_atom("name=image00"), ("name", "image00"))
        self.assertEqual(parse_atom("name=IMAGE00"), ("name", "image00"))
        self.assertEqual(parse_atom("name=表紙"), ("name", "表紙"))

    def test_res_size_atom(self):
        self.assertEqual(parse_atom("res<200"), ("res", "<", 200))
        self.assertEqual(parse_atom("size>1mb"), ("size", ">", 1048576))


class TestParseDropExpr(unittest.TestCase):
    """逗号=OR、+=AND、[] 粘贴、关闭词、非法 token。"""

    def test_or(self):
        self.assertEqual(parse_drop_expr("封面,超大页"),
                         [[("mark", "cover")], [("mark", "overscale")]])

    def test_and(self):
        self.assertEqual(parse_drop_expr("封面+超大页"),
                         [[("mark", "cover"), ("mark", "overscale")]])

    def test_bracket(self):
        self.assertEqual(parse_drop_expr("[封面],[疑似旋转跨页]"),
                         [[("mark", "cover")], [("mark", "rotated_double")]])

    def test_mixed(self):
        self.assertEqual(parse_drop_expr("封面+超大页,异常"),
                         [[("mark", "cover"), ("mark", "overscale")],
                          [("mark", "anom")]])

    def test_name_mix(self):
        self.assertEqual(parse_drop_expr("name=cover,res<200"),
                         [[("name", "cover")], [("res", "<", 200)]])

    def test_close_words(self):
        for v in ("off", "0", "no", "false", "none", ""):
            self.assertIsNone(parse_drop_expr(v), f"{v!r} 应为关闭")
        self.assertIsNone(parse_drop_expr(None))

    def test_invalid_token(self):
        for v in ("不存在的词", "[封面] [追加]"):
            with self.assertRaises(ArgumentTypeError, msg=f"{v!r} 应报错"):
                parse_drop_expr(v)


class TestEvalAtom(unittest.TestCase):
    """原子判定，重点：cover_extra 修复、name、处置、anom。"""

    def test_cover_hits_cover_extra(self):
        a = mkattrs(cover_extra=True)
        self.assertTrue(eval_atom(a, ("mark", "cover")))
        self.assertTrue(eval_atom(a, ("extra",)))  # 封面补位同时计入 [多余]

    def test_cover_hits_in_spine(self):
        self.assertTrue(eval_atom(mkattrs(cover=True), ("mark", "cover")))
        self.assertFalse(eval_atom(mkattrs(), ("mark", "cover")))

    def test_extra(self):
        self.assertTrue(eval_atom(mkattrs(extra=True), ("extra",)))
        self.assertFalse(eval_atom(mkattrs(), ("extra",)))

    def test_name_ci_substring(self):
        a = mkattrs(path="Cover00196.jpeg")
        self.assertTrue(eval_atom(a, ("name", "cover")))
        self.assertTrue(eval_atom(a, ("name", "00196")))
        self.assertFalse(eval_atom(a, ("name", "zzz")))

    def test_mark_tags(self):
        a = mkattrs(mark={"overscale"})
        self.assertTrue(eval_atom(a, ("mark", "overscale")))
        self.assertFalse(eval_atom(a, ("mark", "rotated_double")))
        a2 = mkattrs(mark={"overscale", "rotated_double"})
        self.assertTrue(eval_atom(a2, ("mark", "rotated_double")))
        # 原有 double/animated/thumbnail/small 标记判定不破坏
        for tag in ("double", "animated", "thumbnail", "small"):
            self.assertTrue(eval_atom(mkattrs(mark={tag}), ("mark", tag)))

    def test_anom(self):
        self.assertTrue(eval_atom(mkattrs(anom=True), ("mark", "anom")))
        self.assertFalse(eval_atom(mkattrs(), ("mark", "anom")))

    def test_disposition(self):
        self.assertTrue(eval_atom(mkattrs(disposition="drop"), ("mark", "drop")))
        self.assertTrue(eval_atom(mkattrs(disposition="append"), ("mark", "append")))
        self.assertFalse(eval_atom(mkattrs(), ("mark", "drop")))
        self.assertFalse(eval_atom(mkattrs(), ("mark", "append")))
        self.assertTrue(eval_atom(mkattrs(filter_hit=True), ("mark", "filter")))
        self.assertFalse(eval_atom(mkattrs(), ("mark", "filter")))

    def test_res_size(self):
        self.assertTrue(eval_atom(mkattrs(w=1200, h=2000), ("res", ">", 1000)))
        self.assertTrue(eval_atom(mkattrs(w=120, h=200), ("res", "<", 200)))
        self.assertFalse(eval_atom(mkattrs(w=1200, h=2000), ("res", "<", 1000)))
        self.assertTrue(eval_atom(mkattrs(size=5000), ("size", ">", 1024)))
        self.assertTrue(eval_atom(mkattrs(size=500), ("size", "<", 1024)))
        self.assertFalse(eval_atom(mkattrs(size=None), ("size", ">", 1)))


class TestMarkFilling(unittest.TestCase):
    """_fill_small_mark / _fill_overscale_mark 标记回填与 anom 汇总。"""

    def _mkimg(self, w, h, **kw):
        return mkattrs(w=w, h=h, dir=None, **kw)

    def test_small(self):
        # 面积口径：宽×高 < 中位面积×ratio 判小图（ratio=None 不标）
        lst = [self._mkimg(960, 1500), self._mkimg(1000, 1500), self._mkimg(100, 150)]
        fill_small(lst, 0.5)
        self.assertIn("small", lst[2]["mark"])
        self.assertNotIn("small", lst[0]["mark"])
        # 边长不小但面积小（600x800 宽>中位宽×0.5）→ 面积口径命中
        lst2 = [self._mkimg(960, 1500), self._mkimg(1000, 1500), self._mkimg(600, 800)]
        fill_small(lst2, 0.5)
        self.assertIn("small", lst2[2]["mark"])
        # ratio=None 不标
        lst3 = [self._mkimg(960, 1500), self._mkimg(1000, 1500), self._mkimg(100, 150)]
        fill_small(lst3, None)
        self.assertNotIn("small", lst3[2]["mark"])

    def test_overscale_and_rotated(self):
        # 正常页中位 (960,1500) ratio≈0.64；2000x3000 超大；1486x1920 ratio≈0.77 旋转跨页
        lst = [self._mkimg(960, 1500), self._mkimg(950, 1500), self._mkimg(1000, 1500),
               self._mkimg(2000, 3000), self._mkimg(1486, 1920)]
        fill_overscale(lst)
        self.assertIn("overscale", lst[3]["mark"])
        self.assertIn("overscale", lst[4]["mark"])
        self.assertIn("rotated_double", lst[4]["mark"])
        self.assertNotIn("overscale", lst[0]["mark"])
        self.assertTrue(lst[4]["anom"])
        self.assertTrue(lst[3]["anom"])
        self.assertFalse(lst[0]["anom"])

    def test_overscale_cover_not_exempt(self):
        # 封面尺寸异常照标 [异常]（封面不豁免）
        lst = [self._mkimg(960, 1500), self._mkimg(950, 1500), self._mkimg(1000, 1500),
               self._mkimg(3000, 1500, cover=True)]
        fill_overscale(lst)
        self.assertIn("overscale", lst[3]["mark"])
        self.assertTrue(lst[3]["anom"])


class TestInspectArg(unittest.TestCase):
    """v3.3.0：--inspect [MODE][,FILTER] 解析 → (mode, filter)。"""

    def test_defaults(self):
        self.assertEqual(parse_inspect_arg(None), ("sample", None))
        self.assertEqual(parse_inspect_arg(""), ("sample", None))
        self.assertEqual(parse_inspect_arg("sample"), ("sample", None))
        self.assertEqual(parse_inspect_arg("all"), ("all", None))

    def test_with_filter(self):
        self.assertEqual(parse_inspect_arg("all,small=0.6"),
                         ("all", [[("small", 0.6)]]))
        self.assertEqual(parse_inspect_arg("small=0.6"),
                         ("sample", [[("small", 0.6)]]))
        self.assertEqual(parse_inspect_arg("sample,封面,超大页"),
                         ("sample", [[("mark", "cover")], [("mark", "overscale")]]))

    def test_off(self):
        self.assertEqual(parse_inspect_arg("off"), ("sample", None))

    def test_invalid_token(self):
        with self.assertRaises(ArgumentTypeError):
            parse_inspect_arg("all,不存在的词")


class TestExtractSmallRatio(unittest.TestCase):
    """v3.3.0：从丢弃/过滤表达式提取 small 比例（三链路统一口径）。"""

    def test_none(self):
        self.assertIsNone(extract_small_ratio(None))
        self.assertIsNone(extract_small_ratio([[("mark", "cover")]]))

    def test_implicit_ratio_uses_default(self):
        self.assertEqual(extract_small_ratio([[("small", None)]]),
                         DEFAULT_DROP_SMALL_RATIO)

    def test_explicit_ratio(self):
        self.assertEqual(extract_small_ratio([[("small", 0.6)]]), 0.6)
        # 混合组：多组时取首个 small 比例
        self.assertEqual(extract_small_ratio(
            [[("small", 0.3)], [("mark", "cover")]]), 0.3)


class TestSmallParamAlias(unittest.TestCase):
    """v3.3.0：small 独立带参条件词，多语言别名可带比例。"""

    def _check(self, alias, expect):
        got = parse_atom(alias)
        self.assertIsNotNone(got, f"alias 未解析: {alias!r}")
        self.assertEqual(got, expect, f"alias={alias!r}")

    def test_small_implicit(self):
        for a in ("small", "异常小图", "異常小圖", "異常小画像", "極小画像", "[small]"):
            self._check(a, ("small", None))

    def test_small_with_ratio(self):
        self._check("small=0.6", ("small", 0.6))
        self._check("異常小圖=0.5", ("small", 0.5))
        self._check("異常小画像=0.7", ("small", 0.7))
        self._check("極小画像=0.8", ("small", 0.8))
        self._check("small=auto", ("small", None))

    def test_small_invalid(self):
        for v in ("small=2", "small=0", "small=abc", "small=-0.1"):
            with self.assertRaises(ArgumentTypeError, msg=f"{v!r} 应报错"):
                parse_atom(v)


class TestSourceGuard(unittest.TestCase):
    """源码护栏：转换链路必须与 list 侧一样回填 small/overscale 标记，防回归。"""

    def test_conversion_chain_calls_fill_marks(self):
        src = inspect.getsource(mod.ebook_to_cbz)
        self.assertIn("_fill_small_mark(attrs_list, drop_small)", src)
        self.assertIn("_fill_overscale_mark(attrs_list)", src)

    def test_list_chains_call_fill_marks(self):
        for fn in (mod._list_ebook, mod._list_cbz):
            src = inspect.getsource(fn)
            self.assertIn("_fill_small_mark(attrs_list, small_ratio)", src)
            self.assertIn("_fill_overscale_mark(attrs_list)", src)

    def test_eval_atom_has_cover_extra_fix(self):
        # 防止 cover_extra 修复被回退
        src = inspect.getsource(mod.eval_filter_atom)
        self.assertIn("attrs.get(\"cover\") or attrs.get(\"cover_extra\")", src)
        self.assertIn("attrs.get(\"extra\") or attrs.get(\"cover_extra\")", src)

    def test_list_chains_use_unified_drop(self):
        # v3.3.0：list/inspect/转换三链路统一 --drop 表达式（list 侧 drop_expr=args.drop + small_ratio）
        for fn in (mod._list_ebook, mod._list_cbz):
            src = inspect.getsource(fn)
            self.assertIn("drop_expr = args.drop", src)
            self.assertIn("extract_small_ratio(list_expr) or extract_small_ratio(drop_expr)", src)

    def test_inspect_ebook_has_filter_hits(self):
        # v3.3.0：--inspect [MODE][,FILTER] 命中清单字段与 emit 护栏
        src = inspect.getsource(mod.inspect_ebook)
        self.assertIn("\"filter_hits\"", src)
        self.assertIn("filter_expr", src)
        self.assertIn("t(\"inspect.filter_hits\"", src)



class TestZipSafety(unittest.TestCase):
    """_safe_zip_extract 驱动器相对路径（C:foo）与 .. 跳转逃逸防护（v3.1.0 P0 修复护栏）。"""

    def test_drive_relative_and_dotdot_blocked(self):
        import io
        from zipfile import ZipFile, ZipInfo
        buf = io.BytesIO()
        with ZipFile(buf, "w") as zf:
            zf.writestr(ZipInfo("C:evil.txt"), b"x")  # 驱动器相对路径
            zf.writestr("../evil.txt", b"x")          # .. 跳转
            zf.writestr("ok.txt", b"y")               # 合法条目
        buf.seek(0)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            with ZipFile(buf) as zf:
                mod._safe_zip_extract(zf, out)
            self.assertTrue((out / "ok.txt").exists(), "合法条目应解出")
            self.assertFalse((out / "evil.txt").exists(), "C:foo 条目不得写出")
            self.assertFalse((out.parent / "evil.txt").exists(), ".. 跳转不得逃逸")


class TestRepack(unittest.TestCase):
    """--repack 输出名还原 + 已有 ComicInfo 原样带回 + 已存在跳过。"""

    @staticmethod
    def _args(**kw):
        base = dict(no_comicinfo=False, setinfo=None, output_dir=None, overwrite=False)
        base.update(kw)
        return types.SimpleNamespace(**base)

    def test_repack_restores_name_with_comicinfo(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "vol_cbz"
            src.mkdir()
            (src / "p1.jpg").write_bytes(b"fake-jpg")
            (src / "ComicInfo.xml").write_text(
                "<ComicInfo><Title>Vol 1</Title></ComicInfo>", encoding="utf-8")
            self.assertTrue(mod.repack_one(src, self._args()))
            out = base / "vol.cbz"
            self.assertTrue(out.exists(), "应还原为 vol.cbz")
            with zipfile.ZipFile(out) as zf:
                names = zf.namelist()
                self.assertIn("p1.jpg", names)
                self.assertIn("ComicInfo.xml", names)
                self.assertIn("Vol 1", zf.read("ComicInfo.xml").decode("utf-8"),
                              "已有 ComicInfo 应原样带回")

    def test_repack_skips_existing_without_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = base / "vol_cbz"
            src.mkdir()
            (src / "p1.jpg").write_bytes(b"fake-jpg")
            existing = base / "vol.cbz"
            existing.write_bytes(b"OLD")
            self.assertTrue(mod.repack_one(src, self._args()))
            self.assertEqual(existing.read_bytes(), b"OLD", "已存在且无 overwrite 应跳过")


class TestWindowsPathName(unittest.TestCase):
    """name 原子对 WindowsPath 文件名不崩溃（v3.1.0 修复护栏）。"""

    def test_name_atom_with_windows_path(self):
        from pathlib import PureWindowsPath
        a = mkattrs(path=PureWindowsPath(r"D:\manga\Cover001.jpeg"))
        self.assertTrue(eval_atom(a, ("name", "cover")), "WindowsPath 应正常匹配纯文件名")
        self.assertFalse(eval_atom(a, ("name", "zzz")))
        self.assertFalse(eval_atom(a, ("name", "manga")), "目录路径不应计入 name= 匹配")


class TestExitCodeSemantics(unittest.TestCase):
    """v3.4.0 退出码语义：0=全部成功、1=有失败文件、2=参数用法错误。"""

    def test_bad_flag_exit_2(self):
        self.assertEqual(_run_cli("--no-such-flag").returncode, 2, "参数用法错误应退出 2")

    def test_missing_path_exit_1(self):
        self.assertEqual(_run_cli(str(MAIN.parent / "no_such_dir_xyz")).returncode, 1)

    def test_broken_convert_exit_1(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ep = _make_mini_epub(d, broken=True)
            r = _run_cli("--output-dir", str(d / "out"), str(ep))
            self.assertEqual(r.returncode, 1, "转换失败应退出 1")

    def test_success_convert_exit_0(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ep = _make_mini_epub(d, broken=False)
            r = _run_cli("--output-dir", str(d / "out"), str(ep))
            self.assertEqual(r.returncode, 0, "全部成功应退出 0")


class TestInspectJsonFormats(unittest.TestCase):
    """v3.4.0 --inspect --json formats 汇总字段（源码护栏 + 子进程实测）。"""

    def test_summary_helper_keeps_only_formats(self):
        helper = mod._inspect_img_summary
        self.assertEqual(list(inspect.signature(helper).parameters), ["fmt_counter"])
        self.assertEqual(set(helper({"jpeg": 42}).keys()), {"formats"})
        self.assertEqual(helper({"jpeg": 42})["formats"], {"jpeg": 42})
        self.assertIsNone(helper({})["formats"], "空计数时 formats 应为 null")

    def test_base_fields_include_formats(self):
        src = inspect.getsource(mod._emit_inspect_json)
        self.assertIn('"filter_hits", "formats")', src, "精简行 base_fields 应含 formats")

    def test_summary_wired_to_both_branches(self):
        src = inspect.getsource(mod)
        self.assertGreaterEqual(
            src.count("_inspect_img_summary("), 3,
            "helper 定义 + CBZ 分支 + EPUB 分支均应出现 _inspect_img_summary 调用")

    def test_inspect_json_stdout_has_formats(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ep = _make_mini_epub(d, broken=False)
            r = _run_cli("--inspect", "all", "--json", str(ep))
            self.assertEqual(r.returncode, 0)
            self.assertIn('"formats"', r.stdout, "inspect --json 精简行应带 formats")


class TestVersionGuard(unittest.TestCase):
    """v3.4.0 版本号同步护栏：__version__ / docstring 更新日志。"""

    def test_version_is_3_4_0(self):
        self.assertEqual(mod.__version__, "3.4.0")

    def test_docstring_changelog_has_3_4_0(self):
        self.assertIn("v3.4.0", mod.__doc__)
        self.assertIn("退出码", mod.__doc__)


if __name__ == "__main__":
    unittest.main(verbosity=2)
