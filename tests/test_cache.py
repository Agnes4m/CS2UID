"""cache.py 单元测试。"""

import time
from pathlib import Path

import pytest

from CS2UID.utils.cache import (
    CacheEntry,
    CS2Cache,
    cs2_cache,
    load_json_cached,
    save_json_cached,
)


@pytest.fixture(autouse=True)
def clear_global_cache():
    cs2_cache._cache.clear()
    yield
    cs2_cache._cache.clear()


def test_make_key_includes_kwargs():
    c = CS2Cache()
    k1 = c._make_key("pf", "uid1", "get_userdetail", season="")
    k2 = c._make_key("pf", "uid1", "get_userdetail", season="S5")
    assert k1 != k2


def test_set_get_roundtrip():
    cs2_cache.set("pf", "uid1", "get_x", {"a": 1}, ttl=60)
    assert cs2_cache.get("pf", "uid1", "get_x") == {"a": 1}


def test_get_returns_none_when_missing():
    assert cs2_cache.get("pf", "uid1", "not_set") is None


def test_invalidate_specific_method():
    cs2_cache.set("pf", "uid1", "get_a", 1, ttl=60)
    cs2_cache.set("pf", "uid1", "get_b", 2, ttl=60)
    cs2_cache.invalidate("pf", "uid1", "get_a")
    assert cs2_cache.get("pf", "uid1", "get_a") is None
    assert cs2_cache.get("pf", "uid1", "get_b") == 2


def test_invalidate_all_user_methods():
    cs2_cache.set("pf", "uid1", "get_a", 1, ttl=60)
    cs2_cache.set("pf", "uid1", "get_b", 2, ttl=60)
    cs2_cache.invalidate("pf", "uid1")
    assert cs2_cache.get("pf", "uid1", "get_a") is None
    assert cs2_cache.get("pf", "uid1", "get_b") is None


def test_cache_entry_expiry():
    entry = CacheEntry(
        value="x", created_at=time.time() - 10, ttl=time.time() - 1
    )
    assert entry.is_expired() is True


def test_cache_entry_not_expired():
    entry = CacheEntry(value="x", created_at=time.time(), ttl=time.time() + 60)
    assert entry.is_expired() is False


def test_clear_expired():
    expired = CacheEntry(
        value="old", created_at=time.time() - 10, ttl=time.time() - 1
    )
    fresh = CacheEntry(
        value="new", created_at=time.time(), ttl=time.time() + 60
    )
    cs2_cache._cache["k1"] = expired
    cs2_cache._cache["k2"] = fresh
    cs2_cache.clear_expired()
    assert "k1" not in cs2_cache._cache
    assert "k2" in cs2_cache._cache


def test_get_stats():
    cs2_cache.set("pf", "uid1", "m1", 1, ttl=60)
    stats = cs2_cache.get_stats()
    assert stats["total"] == 1
    assert stats["valid"] == 1


def test_load_json_cached_returns_none_when_file_missing(tmp_path: Path):
    fp = tmp_path / "nope.json"
    assert load_json_cached(fp, "pf", "u1", "m1") is None


def test_save_then_load_roundtrip(tmp_path: Path):
    fp = tmp_path / "match.json"
    save_json_cached({"data": 1}, fp, "pf", "u1", "m1", ttl=60)
    assert fp.is_file()
    assert load_json_cached(fp, "pf", "u1", "m1") == {"data": 1}


def test_load_json_cached_corrupted_file(tmp_path: Path):
    fp = tmp_path / "bad.json"
    fp.write_text("{not json", encoding="utf-8")
    assert load_json_cached(fp, "pf", "u1", "m1") is None


def test_load_json_cached_uses_memory_first(tmp_path: Path):
    fp = tmp_path / "match.json"
    cs2_cache.set("pf", "u1", "m1", {"from": "memory"}, ttl=60)
    fp.write_text('{"from": "disk"}', encoding="utf-8")
    assert load_json_cached(fp, "pf", "u1", "m1") == {"from": "memory"}
