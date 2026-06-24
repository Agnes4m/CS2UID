"""utils.api.perf 包单元测试。"""

import asyncio
import time

import pytest

from CS2UID.utils.api.perf.cache import ResponseCache
from CS2UID.utils.api.perf.coalescer import RequestCoalescer


def test_response_cache_lru_eviction():
    c = ResponseCache(maxsize=3, ttl=60)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    c.set("d", 4)  # 触发 LRU 淘汰
    assert c.get("a") is None
    assert c.get("d") == 4


def test_response_cache_lru_ordering():
    c = ResponseCache(maxsize=3, ttl=60)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    c.get("a")  # 访问 a 提升为最近
    c.set("d", 4)  # 此时应淘汰 b
    assert c.get("a") == 1
    assert c.get("b") is None


def test_response_cache_ttl_expiry():
    c = ResponseCache(maxsize=10, ttl=1)
    c.set("a", 1, ttl=1)
    time.sleep(1.2)
    assert c.get("a") is None


def test_response_cache_overwrite_existing_key():
    c = ResponseCache(maxsize=10, ttl=60)
    c.set("a", 1)
    c.set("a", 2)
    assert c.get("a") == 2
    assert len(c._cache) == 1


def test_response_cache_delete():
    c = ResponseCache(maxsize=10, ttl=60)
    c.set("a", 1)
    assert c.delete("a") is True
    assert c.delete("a") is False


def test_response_cache_clear():
    c = ResponseCache(maxsize=10, ttl=60)
    c.set("a", 1)
    c.set("b", 2)
    c.clear()
    assert len(c._cache) == 0


def test_response_cache_stats():
    c = ResponseCache(maxsize=10, ttl=60)
    c.set("a", 1)
    c.set("b", 2)
    stats = c.get_stats()
    assert stats["total"] == 2
    assert stats["maxsize"] == 10


@pytest.mark.asyncio
async def test_coalescer_dedupes_concurrent_calls():
    co = RequestCoalescer()
    call_count = 0

    async def slow_call():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return "result"

    async def runner():
        return await co.get("k1", slow_call)

    results = await asyncio.gather(runner(), runner(), runner())
    assert call_count == 1
    assert all(r == "result" for r in results)


@pytest.mark.asyncio
async def test_coalescer_caches_after_completion():
    co = RequestCoalescer()
    call_count = 0

    async def slow_call():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.05)
        return "result"

    await co.get("k1", slow_call)
    cached = co.get_cached("k1")
    assert cached == "result"
    assert call_count == 1


@pytest.mark.asyncio
async def test_coalescer_different_keys_run_independently():
    co = RequestCoalescer()
    call_count = 0

    async def slow_call():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.05)
        return call_count

    a, b = await asyncio.gather(
        co.get("k1", slow_call),
        co.get("k2", slow_call),
    )
    assert call_count == 2
    assert a == 1
    assert b == 2


@pytest.mark.asyncio
async def test_coalescer_request_helper():
    co = RequestCoalescer()
    call_count = 0

    async def slow_call():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.05)
        return "x"

    a, b = await asyncio.gather(
        co.request(slow_call, "uid1", "m1"),
        co.request(slow_call, "uid1", "m1"),
    )
    assert call_count == 1


@pytest.mark.asyncio
async def test_coalescer_exception_propagates():
    co = RequestCoalescer()

    async def failing():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await co.get("k1", failing)
    assert "k1" not in co._pending


def test_coalescer_clear_cache():
    co = RequestCoalescer()
    co._results["k1"] = 1
    co._results["k2"] = 2
    co.clear_cache("k1")
    assert "k1" not in co._results
    assert "k2" in co._results
    co.clear_cache()
    assert len(co._results) == 0
