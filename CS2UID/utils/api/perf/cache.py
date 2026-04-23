"""响应缓存 - 基于TTL的LRU缓存"""

import time
from typing import Any, Dict, Tuple, Callable, Optional
from collections import OrderedDict

from gsuid_core.logger import logger


class ResponseCache:
    """
    基于TTL的LRU缓存

    特点:
    - TTL过期时间
    - LRU淘汰策略
    - 线程安全（asyncio场景下单线程无需锁）

    用途:
    - 缓存用户信息查询结果
    - 缓存排行榜等相对稳定的数据
    """

    def __init__(
        self,
        maxsize: int = 1000,
        ttl: int = 300,  # 默认5分钟TTL
    ):
        """
        Args:
            maxsize: 最大缓存条目数
            ttl: 缓存过期时间（秒）
        """
        self._maxsize = maxsize
        self._ttl = ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()

        logger.info(f"[CS2][ResponseCache] 初始化 (maxsize={maxsize}, ttl={ttl}s)")

    def _make_key(self, namespace: str, *args, **kwargs) -> str:
        """生成缓存key"""
        parts = [namespace]
        parts.extend(str(arg) for arg in args)
        parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "|".join(parts)

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存key

        Returns:
            缓存的值，如果不存在或已过期返回None
        """
        if key not in self._cache:
            logger.debug(f"[CS2][ResponseCache] 未命中: {key[:20]}...")
            return None

        value, expires_at = self._cache[key]

        # 检查是否过期
        if time.time() > expires_at:
            logger.debug(f"[CS2][ResponseCache] 已过期: {key[:20]}...")
            del self._cache[key]
            return None

        # 移动到末尾（最近使用）
        self._cache.move_to_end(key)
        logger.debug(f"[CS2][ResponseCache] 命中: {key[:20]}...")
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存

        Args:
            key: 缓存key
            value: 缓存的值
            ttl: 可选的过期时间（秒），默认使用初始化时的ttl
        """
        if ttl is None:
            ttl = self._ttl

        expires_at = time.time() + ttl

        # 如果key已存在，删除旧条目
        if key in self._cache:
            del self._cache[key]

        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self._maxsize:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug(f"[CS2][ResponseCache] LRU淘汰: {oldest_key[:20]}...")

        self._cache[key] = (value, expires_at)
        logger.debug(f"[CS2][ResponseCache] 已缓存: {key[:20]}...")

    def delete(self, key: str) -> bool:
        """
        删除指定缓存

        Returns:
            是否删除成功
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self):
        """清空所有缓存"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"[CS2][ResponseCache] 已清空 {count} 条缓存")

    def cached(self, namespace: str, ttl: Optional[int] = None):
        """
        装饰器方式使用缓存

        Args:
            namespace: 命名空间，用于区分不同类型的缓存
            ttl: 可选的过期时间

        Example:
            @cache.cached("user_info")
            async def get_user_info(uid):
                return await api.fetch_user(uid)
        """

        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                key = self._make_key(namespace, *args, **kwargs)

                # 尝试从缓存获取
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value

                # 执行实际函数
                result = await func(*args, **kwargs)

                # 缓存结果
                if result is not None:
                    self.set(key, result, ttl)

                return result

            # 保留原函数信息
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__

            # 提供手动清除缓存的方法
            wrapper.invalidate = lambda *a, **kw: self.delete(self._make_key(namespace, *a, **kw))
            wrapper.clear = self.clear

            return wrapper

        return decorator

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        now = time.time()
        expired = sum(1 for _, (_, exp) in self._cache.items() if now > exp)

        return {
            "total": len(self._cache),
            "expired": expired,
            "valid": len(self._cache) - expired,
            "maxsize": self._maxsize,
            "ttl": self._ttl,
        }


# 全局实例 - 默认配置
_response_cache: Optional[ResponseCache] = None


def get_response_cache(
    maxsize: int = 1000,
    ttl: int = 300,
) -> ResponseCache:
    """获取响应缓存单例"""
    global _response_cache
    if _response_cache is None:
        _response_cache = ResponseCache(maxsize=maxsize, ttl=ttl)
    return _response_cache
