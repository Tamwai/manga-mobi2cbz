# -*- coding: utf-8 -*-
"""manga-mobi2cbz 回归测试。

覆盖：多语言别名 / [] 粘贴 / 与或表达式 / 标签与文件名原子 / 处置筛选
      / overscale 标记回填 / 转换链路与 list 侧标记一致性（源码护栏）。
不依赖 PIL，纯单元断言 + inspect 源码护栏。运行：
    python tests/test_mobi2cbz.py
"""
import importlib.util
import inspect
import sys
import unittest
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
eval_atom = mod.eval_filter_atom
fill_small = mod._fill_small_mark
fill_overscale = mod._fill_overscale_mark


def mkattrs(**kw):
    """手搓图片属性 dict，避免依赖真实文件。"""
    d = {"path": "x.jpg", "zname": None, "ext": "jpg", "w": 100, "h": 150,
         "mode": "rgb", "depth": 24, "size": 1000, "dir": "portrait",
         "mark": set(), "extra": False, "cover": False, "cover_extra": False,
         "filter_hit": False, "disposition": None, "anom": False}
    d.update(kw)
    return d


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
        lst = [self._mkimg(960, 1500), self._mkimg(1000, 1500), self._mkimg(100, 150)]
        fill_small(lst)
        self.assertIn("small", lst[2]["mark"])
        self.assertNotIn("small", lst[0]["mark"])

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


class TestSourceGuard(unittest.TestCase):
    """源码护栏：转换链路必须与 list 侧一样回填 small/overscale 标记，防回归。"""

    def test_conversion_chain_calls_fill_marks(self):
        src = inspect.getsource(mod.ebook_to_cbz)
        self.assertIn("_fill_small_mark(attrs_list)", src)
        self.assertIn("_fill_overscale_mark(attrs_list)", src)

    def test_list_chains_call_fill_marks(self):
        for fn in (mod._list_ebook, mod._list_cbz):
            src = inspect.getsource(fn)
            self.assertIn("_fill_small_mark(attrs_list)", src)
            self.assertIn("_fill_overscale_mark(attrs_list)", src)

    def test_eval_atom_has_cover_extra_fix(self):
        # 防止 cover_extra 修复被回退
        src = inspect.getsource(mod.eval_filter_atom)
        self.assertIn("attrs.get(\"cover\") or attrs.get(\"cover_extra\")", src)
        self.assertIn("attrs.get(\"extra\") or attrs.get(\"cover_extra\")", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
