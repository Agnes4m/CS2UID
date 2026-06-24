"""platform.py 单元测试。"""

from CS2UID.utils.platform import detect_platform


def test_detect_platform_5e_variants():
    assert detect_platform("5E") == "5e"
    assert detect_platform("5e") == "5e"
    assert detect_platform("cs 5e 12345") == "5e"
    assert detect_platform("CS5E查询") == "5e"


def test_detect_platform_gf_variants():
    assert detect_platform("官匹") == "gf"
    assert detect_platform("gp") == "gf"
    assert detect_platform("gf") == "gf"
    assert detect_platform("国服") == "gf"
    assert detect_platform("CS 官匹查询") == "gf"


def test_detect_platform_pf_variants():
    assert detect_platform("pf") == "pf"
    assert detect_platform("完美") == "pf"
    assert detect_platform("wanmei") == "pf"
    assert detect_platform("CS完美查询") == "pf"


def test_detect_platform_default_fallback():
    """无关键字时返回 None(由调用方走 default 平台)。"""
    assert detect_platform("") is None
    assert detect_platform("hello") is None
    assert detect_platform("查询") is None


def test_detect_platform_priority():
    """5E 优先于完美关键字(避免 "完美5E" 误判)。"""
    assert detect_platform("完美5E") == "5e"
    assert detect_platform("5E完美") == "5e"
