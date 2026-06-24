"""
CS2UID 查询缓存模块

提供 API 返回数据的缓存功能，减少重复 API 调用
"""

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any

from gsuid_core.logger import logger


@dataclass
class CacheEntry:
    """缓存条目"""

    value: Any
    created_at: float
    ttl: float  # 过期时间戳

    def is_expired(self) -> bool:
        return time.time() > self.ttl


class CS2Cache:
    """
    CS2 查询缓存管理器

    使用内存缓存，支持 TTL 过期机制
    """

    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._default_ttl = 300  # 默认 5 分钟

    def _make_key(self, platform: str, uid: str, method: str, **kwargs) -> str:
        """
        生成缓存 key

        格式: {platform}:{uid}:{method}:{params_hash}
        """
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{platform}:{uid}:{method}:{params_hash}"

    def get(
        self, platform: str, uid: str, method: str, **kwargs
    ) -> Any | None:
        """获取缓存值"""
        key = self._make_key(platform, uid, method, **kwargs)
        entry = self._cache.get(key)

        if entry is None:
            logger.debug(f"[CS2][Cache] 未命中: {key}")
            return None

        if entry.is_expired():
            logger.debug(f"[CS2][Cache] 已过期: {key}")
            del self._cache[key]
            return None

        logger.debug(f"[CS2][Cache] 命中: {key}")
        return entry.value

    def set(
        self,
        platform: str,
        uid: str,
        method: str,
        value: Any,
        ttl: int | None = None,
        **kwargs,
    ):
        """设置缓存值"""
        key = self._make_key(platform, uid, method, **kwargs)
        ttl = ttl or self._default_ttl

        self._cache[key] = CacheEntry(
            value=value, created_at=time.time(), ttl=time.time() + ttl
        )
        logger.debug(f"[CS2][Cache] 设置: {key} (TTL: {ttl}s)")

    def invalidate(
        self, platform: str, uid: str, method: str | None = None, **kwargs
    ):
        """使缓存失效"""
        if method:
            key = self._make_key(platform, uid, method, **kwargs)
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"[CS2][Cache] 失效: {key}")
        else:
            # 删除该用户的所有缓存
            prefix = f"{platform}:{uid}:"
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._cache[k]
            logger.debug(f"[CS2][Cache] 失效 {len(keys_to_delete)} 条")

    def clear_expired(self):
        """清除所有过期缓存"""
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for k in expired_keys:
            del self._cache[k]
        if expired_keys:
            logger.debug(f"[CS2][Cache] 清理 {len(expired_keys)} 条过期缓存")

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        total = len(self._cache)
        expired = sum(1 for v in self._cache.values() if v.is_expired())
        return {"total": total, "expired": expired, "valid": total - expired}


# 全局缓存实例
cs2_cache = CS2Cache()


def cached_query(platform: str, ttl: int = 300):
    """
    API 查询缓存装饰器

    用于包装 API 方法，自动处理缓存逻辑

    Args:
        platform: 平台标识 ('pf' 或 '5e')
        ttl: 缓存过期时间（秒），默认 5 分钟

    Example:
        @cached_query('pf', ttl=300)
        async def get_userdetail(self, uid: str, season: str = ""):
            ...
    """

    def decorator(func: Callable):
        is_coroutine = (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

        if is_coroutine:

            @wraps(func)
            async def async_wrapper(self, uid: str, *args, **kwargs):
                # 先检查缓存
                cached = cs2_cache.get(
                    platform, uid, func.__name__, args=args, kwargs=kwargs
                )
                if cached is not None:
                    return cached

                # 调用原函数
                result = await func(self, uid, *args, **kwargs)

                # 缓存结果
                if result is not None and not isinstance(result, int):
                    cs2_cache.set(
                        platform,
                        uid,
                        func.__name__,
                        result,
                        ttl,
                        args=args,
                        kwargs=kwargs,
                    )

                return result

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(self, uid: str, *args, **kwargs):
                # 先检查缓存
                cached = cs2_cache.get(
                    platform, uid, func.__name__, args=args, kwargs=kwargs
                )
                if cached is not None:
                    return cached

                # 调用原函数
                result = func(self, uid, *args, **kwargs)

                # 缓存结果
                if result is not None and not isinstance(result, int):
                    cs2_cache.set(
                        platform,
                        uid,
                        func.__name__,
                        result,
                        ttl,
                        args=args,
                        kwargs=kwargs,
                    )

                return result

            return sync_wrapper

    return decorator


def invalidate_user_cache(platform: str, uid: str):
    """
    使指定用户的缓存失效

    当用户数据更新时调用
    """
    cs2_cache.invalidate(platform, uid)


def load_json_cached(
    file_path: Path,
    platform: str,
    uid: str,
    method: str,
    ttl: int = 300,
) -> Any | None:
    """优先从内存缓存读 JSON,缓存未命中时尝试从文件读。"""
    cached = cs2_cache.get(platform, uid, method)
    if cached is not None:
        return cached
    if not file_path.is_file():
        return None
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"[CS2][Cache] 读 JSON 失败: {e}")
        return None
    cs2_cache.set(platform, uid, method, data, ttl=ttl)
    return data


def save_json_cached(
    data: Any,
    file_path: Path,
    platform: str,
    uid: str,
    method: str,
    ttl: int = 300,
) -> None:
    """同时写入文件和内存缓存。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except OSError as e:
        logger.warning(f"[CS2][Cache] 写 JSON 失败: {e}")
    cs2_cache.set(platform, uid, method, data, ttl=ttl)
