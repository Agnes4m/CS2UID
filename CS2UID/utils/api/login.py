"""CS2 二维码登录 — 异步实现 (统一登录入口)。"""

import asyncio
import io
from dataclasses import dataclass
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_L
from qrcode.image.pil import PilImage

from gsuid_core.logger import logger

from .perf.pool import get_pool

API_BASE = "https://passport.pwesports.cn"
QR_APPLY_URL = f"{API_BASE}/qrAuth/applyToken"
QR_CHECK_URL = f"{API_BASE}/qrAuth/check"

APP_ID = "5"
QR_TYPE = "1"
WEBSITE = "pvp"
POLL_INTERVAL = 2
MAX_POLL_COUNT = 30


@dataclass
class QRLoginResult:
    """二维码登录结果。"""

    steam_id: str
    token: str
    success: bool
    message: str


def generate_qrcode_image(url: str, bot_id: str = "") -> bytes:
    """生成登录二维码图片 (bytes)。"""
    qr = qrcode.QRCode(
        version=1, error_correction=ERROR_CORRECT_L, box_size=10, border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(255, 134, 36), back_color="white")
    assert isinstance(img, PilImage)

    if bot_id == "onebot":
        img = img.resize((700, 700))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class CS2Login:
    """CS2 二维码登录(走项目统一连接池)。"""

    def __init__(self) -> None:
        self.access_token: str | None = None

    async def apply_qr(self) -> str:
        """申请二维码,返回 access_url。"""
        pool = get_pool()
        resp = await pool.request(
            "POST",
            url=QR_APPLY_URL,
            json={
                "appId": APP_ID,
                "qrType": QR_TYPE,
                "redirect": False,
                "website": WEBSITE,
            },
        )
        data = resp.json()
        qr_url: str = data["result"]["accessUrl"]
        self.access_token = qr_url.split("accessToken=")[1].split("&")[0]
        logger.info(
            f"[CS2][QR] 申请二维码成功, access_token: {self.access_token[:10]}***"
        )
        return qr_url

    async def check_qr_status(self) -> dict:
        """检查二维码状态。"""
        if not self.access_token:
            logger.warning("[CS2][QR] access_token 不存在，请先调用 apply_qr")
            return {"status": -1}

        pool = get_pool()
        resp = await pool.request(
            "POST",
            url=QR_CHECK_URL,
            json={"appId": APP_ID, "accessToken": self.access_token},
        )
        return resp.json().get("result", {})

    async def wait_for_scan(self) -> QRLoginResult:
        """轮询等待扫码完成。"""
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

            if status == 3:
                logger.info("[CS2][QR] 二维码已过期")
                return QRLoginResult(
                    steam_id="",
                    token="",
                    success=False,
                    message="二维码已过期，请重新扫码",
                )

            if status == 1:
                logger.debug(
                    f"[CS2][QR] 等待扫码... [{i + 1}/{MAX_POLL_COUNT}]"
                )
            else:
                logger.warning(f"[CS2][QR] 未知状态: {status}")

            await asyncio.sleep(POLL_INTERVAL)

        logger.info("[CS2][QR] 扫码超时")
        return QRLoginResult(
            steam_id="",
            token="",
            success=False,
            message="扫码超时，请重新操作",
        )

    async def login_by_qr(self) -> QRLoginResult:
        """完整二维码登录流程。"""
        await self.apply_qr()
        return await self.wait_for_scan()


def build_qrcode_payload(url: str, save_path: Path, bot_id: str) -> bytes:
    """生成二维码图片,onebot 平台保存到磁盘,其他平台返回 bytes。"""
    if bot_id == "onebot":
        payload = generate_qrcode_image(url, bot_id)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(payload)
        return payload
    return generate_qrcode_image(url, bot_id)
