"""platform.py 中 _parse_s_value 的单元测试。"""

import importlib

from CS2UID.utils import platform


def test_parse_s_value_simple():
    p = platform._parse_s_value  # type: ignore[attr-defined]
    assert p("S5") == "5"
    assert p("s5") == "5"
    assert p("cs S10") == "10"


def test_parse_s_value_with_sign():
    p = platform._parse_s_value  # type: ignore[attr-defined]
    assert p("S+3") == "+3"
    assert p("S-2") == "-2"


def test_parse_s_value_no_digit():
    p = platform._parse_s_value  # type: ignore[attr-defined]
    assert p("Sabc") == ""
    assert p("") == ""


def test_parse_s_value_trailing_letters():
    p = platform._parse_s_value  # type: ignore[attr-defined]
    assert p("S5abc") == "5"


def test_parse_s_value_no_s_keyword():
    p = platform._parse_s_value  # type: ignore[attr-defined]
    assert p("123") == ""


def test_platform_module_reimports_cleanly():
    """防止移除私有函数后还有外部依赖。"""
    importlib.reload(platform)
    assert hasattr(platform, "detect_platform")
    assert hasattr(platform, "resolve_uid_and_platform")
