"""Token缓存管理 - 避免每次请求都查数据库"""

import time
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from gsuid_core.logger import logger

from ...database.models import CS2User


@dataclass
class CachedToken:
    """缓存的Token对象"""

    uid: str
    token: str
    platform: str  # 'pf' or '5e'
    expires_at: float  # 过期时间戳
    is_valid: bool = True

    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() > self.expires_at


class TokenManager:
    """
    Token管理器 - 内存缓存 + 数据库双层访问
    避免每次API请求都查数据库
    """

    # Token缓存
    _cache: Dict[str, CachedToken] = {}

    # 缓存配置
    CACHE_TTL = 3600  # 缓存有效期1小时
    TOKEN_EXPIRY_BUFFER = 300  # 提前5分钟过期

    # 平台标识
    PLATFORM_PF = "pf"
    PLATFORM_5E = "5e"

    @classmethod
    def _make_cache_key(cls, uid: str, platform: str) -> str:
        """生成缓存key"""
        return f"{platform}:{uid}"

    @classmethod
    async def get_token(cls, uid: str, platform: str = PLATFORM_PF) -> Optional[str]:
        """
        获取有效token

        1. 先查内存缓存
        2. 缓存有效则直接返回
        3. 缓存失效或不存在则查数据库
        4. 查库后更新缓存
        """
        cache_key = cls._make_cache_key(uid, platform)

        # 1. 检查缓存
        cached = cls._cache.get(cache_key)
        if cached is not None and not cached.is_expired():
            logger.debug(f"[CS2][TokenCache] 命中缓存 uid={uid[:4]}***")
            return cached.token

        # 2. 缓存未命中，查数据库
        logger.debug(f"[CS2][TokenCache] 缓存未命中，查数据库 uid={uid[:4]}***")

        if platform == cls.PLATFORM_PF:
            token = await CS2User.get_user_cookie_by_uid(uid)
        elif platform == cls.PLATFORM_5E:
            token = await CS2User.get_user_stoken_by_uid(uid)
        else:
            token = None

        # 3. 更新缓存
        if token:
            cls._cache[cache_key] = CachedToken(
                uid=uid,
                token=token,
                platform=platform,
                expires_at=time.time() + cls.CACHE_TTL,
            )
            logger.debug(f"[CS2][TokenCache] 已缓存 uid={uid[:4]}***")

        return token

    @classmethod
    async def get_random_token(cls, platform: str = PLATFORM_PF) -> Optional[List[str]]:
        """
        获取随机有效token（用于不需要特定用户的场景）
        保持原有random.choice的行为
        """
        user_list = await CS2User.get_all_user()
        if not user_list:
            logger.warning("[CS2][TokenCache] 数据库中无用户")
            return None

        user = random.choice(user_list)
        if user.uid is None:
            logger.warning("[CS2][TokenCache] 随机选中的用户无uid")
            return None

        token = await cls.get_token(user.uid, platform)
        if token is None:
            logger.warning(f"[CS2][TokenCache] 用户 {user.uid[:4]}*** 无有效token")
            return None

        return [user.uid, token]

    @classmethod
    def invalidate(cls, uid: str, platform: str = PLATFORM_PF) -> None:
        """使指定token缓存失效"""
        cache_key = cls._make_cache_key(uid, platform)
        if cache_key in cls._cache:
            del cls._cache[cache_key]
            logger.debug(f"[CS2][TokenCache] 已失效 uid={uid[:4]}*** platform={platform}")

    @classmethod
    def invalidate_all(cls) -> None:
        """清空所有缓存"""
        count = len(cls._cache)
        cls._cache.clear()
        logger.info(f"[CS2][TokenCache] 已清空 {count} 条缓存")

    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total = len(cls._cache)
        expired = sum(1 for t in cls._cache.values() if t.is_expired())
        return {
            "total": total,
            "expired": expired,
            "valid": total - expired,
        }


# 全局实例
token_manager = TokenManager()
