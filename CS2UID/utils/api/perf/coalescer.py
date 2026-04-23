"""请求去重 - 防止并发重复请求"""

import asyncio
import hashlib
from typing import Any, Dict, Callable, Optional, Awaitable

from gsuid_core.logger import logger


class RequestCoalescer:
    """
    并发请求合并器

    当多个请求同时发起且目标相同时，只执行一次实际网络请求，
    其他请求等待该请求完成并共享结果

    场景：10个用户同时查询同一玩家的信息，只会发起1次网络请求
    """

    def __init__(self):
        self._pending: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._results: Dict[str, Any] = {}

    def _make_key(self, *args, **kwargs) -> str:
        """
        生成请求唯一标识
        用于判断是否是相同请求
        """
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get(
        self,
        key: str,
        coro: Callable[[], Awaitable[Any]],
    ) -> Any:
        """
        获取结果，如果已有相同请求在执行中则等待

        Args:
            key: 请求唯一标识
            coro: 实际执行请求的协程函数

        Returns:
            请求结果
        """
        async with self._lock:
            # 检查是否有相同请求正在执行
            if key in self._pending:
                logger.debug(f"[CS2][Coalescer] 请求合并，等待中: {key[:8]}...")
                # 返回正在执行的task的结果
                return await self._pending[key]

            # 创建新task
            task = asyncio.create_task(coro())
            self._pending[key] = task

            logger.debug(f"[CS2][Coalescer] 新建请求: {key[:8]}...")

            try:
                result = await task
                # 保存结果一段时间，以便后续相同请求可以直接获取
                self._results[key] = result
                return result
            finally:
                # 清理
                self._pending.pop(key, None)

    async def request(self, coro: Callable[[], Awaitable[Any]], *args, **kwargs) -> Any:
        """
        便捷方法，自动生成key并执行

        Args:
            coro: 实际执行请求的协程函数
            *args, **kwargs: 用于生成key的参数

        Returns:
            请求结果
        """
        key = self._make_key(*args, **kwargs)
        return await self.get(key, coro)

    def get_cached(self, key: str) -> Optional[Any]:
        """直接获取已缓存的结果（不等待）"""
        return self._results.get(key)

    def clear_cache(self, key: Optional[str] = None):
        """清除缓存结果"""
        if key:
            self._results.pop(key, None)
        else:
            self._results.clear()

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "pending_count": len(self._pending),
            "cached_count": len(self._results),
        }


# 全局实例
_coalescer: Optional[RequestCoalescer] = None


def get_coalescer() -> RequestCoalescer:
    """获取请求合并器单例"""
    global _coalescer
    if _coalescer is None:
        _coalescer = RequestCoalescer()
    return _coalescer
