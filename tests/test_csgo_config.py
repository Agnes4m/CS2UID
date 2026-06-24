"""csgo_config 业务常量 + migrations.sql 加载单元测试。"""

from pathlib import Path

from CS2UID.utils.csgo_config import (
    DEFAULT_MATCH_TYPES,
    get_match_types,
)


def test_default_match_types_contains_all_categories():
    for kw in ("天梯", "pro", "巅峰", "周末", "自定义"):
        assert kw in DEFAULT_MATCH_TYPES
        assert isinstance(DEFAULT_MATCH_TYPES[kw], int)


def test_get_match_types_returns_copy():
    """外部修改返回值不应影响默认映射。"""
    a = get_match_types()
    a["新类型"] = 99
    b = get_match_types()
    assert "新类型" not in b


def test_match_types_known_values():
    assert DEFAULT_MATCH_TYPES["天梯"] == 12
    assert DEFAULT_MATCH_TYPES["pro"] == 41
    assert DEFAULT_MATCH_TYPES["巅峰"] == 20
    assert DEFAULT_MATCH_TYPES["周末"] == 27
    assert DEFAULT_MATCH_TYPES["自定义"] == 14


def test_migrations_sql_exists_and_contains_alter():
    fp = Path("CS2UID/utils/database/migrations.sql")
    assert fp.is_file()
    text = fp.read_text(encoding="utf-8")
    assert "ALTER TABLE CS2Bind" in text
    assert "platform" in text
    assert "domain" in text
