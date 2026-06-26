"""连接池实现 - 复用HTTP连接，减少TCP握手开销"""

from typing import Any, Literal, Optional

import httpx
from httpx import AsyncClient, Limits, Timeout

from gsuid_core.logger import logger


class ConnectionPool:
    """
    单例连接池，复用httpx AsyncClient
    避免每次请求新建TCP连接，减少约100ms+延迟
    """

    _instance: Optional["ConnectionPool"] = None
    _client: AsyncClient | None = None

    # 连接池配置
    MAX_KEEPALIVE_CONNECTIONS = 20  # 保持多少个长连接
    MAX_CONNECTIONS = 100  # 最大并发连接数
    KEEPALIVE_EXPIRY = 30.0  # 连接保持时间(秒)
    DEFAULT_TIMEOUT = 300.0  # 默认超时时间(秒)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is not None:
            return

        self._limits = Limits(
            max_keepalive_connections=self.MAX_KEEPALIVE_CONNECTIONS,
            max_connections=self.MAX_CONNECTIONS,
            keepalive_expiry=self.KEEPALIVE_EXPIRY,
        )

        self._timeout = Timeout(self.DEFAULT_TIMEOUT)

        logger.info(
            f"[CS2][ConnectionPool] 初始化连接池 "
            f"(max_keepalive={self.MAX_KEEPALIVE_CONNECTIONS}, "
            f"max_connections={self.MAX_CONNECTIONS})"
        )

    async def get_client(self) -> AsyncClient:
        """获取或创建AsyncClient单例"""
        if self._client is None or self._client.is_closed:
            self._client = AsyncClient(
                limits=self._limits,
                timeout=self._timeout,
                verify=False,  # 保持原有设置
                http2=True,  # 启用HTTP/2提升性能
            )
            logger.info("[CS2][ConnectionPool] AsyncClient已创建")
        return self._client

    async def request(
        self,
        method: Literal["GET", "POST"],
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """
        使用连接池发起请求

        Args:
            method: 请求方法 GET/POST
            url: 请求URL
            headers: 请求头
            params: URL参数
            json: JSON body
            data: Form data
            timeout: 超时时间(秒)，None则使用默认

        Returns:
            httpx.Response对象
        """
        client = await self.get_client()

        request_kwargs = {
            "method": method,
            "url": url,
            "headers": headers,
        }

        if params:
            request_kwargs["params"] = params
        if json:
            request_kwargs["json"] = json
        if data:
            request_kwargs["data"] = data
        if timeout:
            request_kwargs["timeout"] = Timeout(timeout)

        logger.debug(f"[CS2][ConnectionPool] {method} {url}")

        return await client.request(**request_kwargs)

    async def close(self):
        """关闭连接池"""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("[CS2][ConnectionPool] 连接池已关闭")

    @property
    def is_closed(self) -> bool:
        """检查连接池是否已关闭"""
        return self._client is None or self._client.is_closed


# 全局单例
_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    """获取连接池单例"""
    global _pool
    if _pool is None:
        _pool = ConnectionPool()
    return _pool


async def close_pool():
    """关闭连接池"""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
