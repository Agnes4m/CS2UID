"""CS2 二维码登录 - 异步实现"""

import asyncio
from typing import Optional
from dataclasses import dataclass

import httpx

from gsuid_core.logger import logger

# API 端点
QR_APPLY_URL = "https://passport.pwesports.cn/qrAuth/applyToken"
QR_CHECK_URL = "https://passport.pwesports.cn/qrAuth/check"

# 请求配置
APP_ID = "5"
QR_TYPE = "1"
WEBSITE = "pvp"

# 轮询配置
POLL_INTERVAL = 2  # 秒
MAX_POLL_COUNT = 30  # 最多轮询30次 = 60秒


@dataclass
class QRLoginResult:
    """二维码登录结果"""

    steam_id: str
    """Steam64位ID"""
    token: str
    """完美平台Token"""
    success: bool
    """是否成功"""
    message: str
    """结果消息"""


class CS2Login:
    """CS2 二维码登录类"""

    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.access_token: Optional[str] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.client = httpx.AsyncClient(verify=False, timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.client:
            await self.client.aclose()
        return False

    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()

    async def apply_qr(self) -> tuple[str, str]:
        """
        申请二维码

        Returns:
            tuple[str, str]: (access_url, access_token)
        """
        if not self.client:
            raise RuntimeError(
                "Client not initialized. Use 'async with CS2Login()' context manager."
            )

        resp = await self.client.post(
            QR_APPLY_URL,
            json={
                "appId": APP_ID,
                "qrType": QR_TYPE,
                "redirect": False,
                "website": WEBSITE,
            },
        )
        data = resp.json()

        qr_url = data["result"]["accessUrl"]
        # 从URL中提取access_token
        access_token = qr_url.split("accessToken=")[1].split("&")[0]
        self.access_token = access_token

        logger.info(f"[CS2][QR] 申请二维码成功, access_token: {access_token[:10]}***")
        return qr_url, access_token

    async def check_qr_status(self) -> dict:
        """
        检查二维码状态

        Returns:
            dict: 包含 status, accountItem, token 等字段的响应
        """
        if not self.client:
            raise RuntimeError(
                "Client not initialized. Use 'async with CS2Login()' context manager."
            )

        if not self.access_token:
            logger.warning("[CS2][QR] access_token 不存在，请先调用 apply_qr")
            return {"result": {"status": -1}}

        resp = await self.client.post(
            QR_CHECK_URL,
            json={
                "appId": APP_ID,
                "accessToken": self.access_token,
            },
        )
        data = resp.json()

        return data.get("result", {})

    async def wait_for_scan(self) -> QRLoginResult:
        """
        轮询等待扫码完成

        Returns:
            QRLoginResult: 登录结果
        """
        if not self.access_token:
            return QRLoginResult(
                steam_id="",
                token="",
                success=False,
                message="access_token 不存在，请先调用 apply_qr",
            )

        for i in range(MAX_POLL_COUNT):
            result = await self.check_qr_status()
            status = result.get("status")

            if status == 2:
                # 扫码成功
                account_item = result.get("accountItem", {})
                steam_id = account_item.get("steamId", "")
                token = result.get("token", "")

                logger.info(
                    f"[CS2][QR] 登录成功! steam_id: {steam_id}, token: {token[:10]}***"
                )
                return QRLoginResult(
                    steam_id=steam_id,
                    token=token,
                    success=True,
                    message="登录成功",
                )

            elif status == 3:
                # 二维码过期
                logger.info("[CS2][QR] 二维码已过期")
                return QRLoginResult(
                    steam_id="",
                    token="",
                    success=False,
                    message="二维码已过期，请重新扫码",
                )

            elif status == 1:
                # 等待扫码
                logger.debug(f"[CS2][QR] 等待扫码... [{i + 1}/{MAX_POLL_COUNT}]")

            else:
                logger.warning(f"[CS2][QR] 未知状态: {status}")

            await asyncio.sleep(POLL_INTERVAL)

        # 超时
        logger.info("[CS2][QR] 扫码超时")
        return QRLoginResult(
            steam_id="",
            token="",
            success=False,
            message="扫码超时，请重新操作",
        )

    async def login_by_qr(self) -> QRLoginResult:
        """
        完整二维码登录流程

        Returns:
            QRLoginResult: 登录结果
        """
        # 1. 申请二维码
        await self.apply_qr()

        # 2. 轮询等待扫码
        result = await self.wait_for_scan()

        return result
