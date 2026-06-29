"""5E 扫码登录 — 异步实现。"""

import asyncio
import base64
import json
import uuid
from dataclasses import dataclass

from gsuid_core.logger import logger

from .perf.pool import get_pool

API_BASE = "https://www.5eplay.com"
QR_APPLY_URL = f"{API_BASE}/api/user/scan_code_login_qr_code"
QR_CHECK_URL = f"{API_BASE}/api/user/scan_code_login_result"
CONFIRM_LOGIN_URL = f"{API_BASE}/api/user/login"

POLL_INTERVAL = 2
MAX_POLL_COUNT = 30


_HEADERS = {
    "x-requested-with": "XMLHttpRequest",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ),
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.5eplay.com",
    "referer": "https://www.5eplay.com/user/login",
}


@dataclass
class QRCodeResult:
    key: str
    qr_code_bytes: bytes


@dataclass
class PollResult:
    status: int
    """0=未扫码 2=已扫码成功"""


@dataclass
class LoginResult:
    success: bool
    message: str
    token: str = ""
    """5E JWT token，确认登录后可用"""


def _decode_jwt_uid(token: str) -> str:
    """从JWT payload中提取 uid (不验签)。"""
    try:
        payload_b64 = token.split(".")[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload = json.loads(base64.b64decode(payload_b64))
        return str(payload.get("uid", ""))
    except Exception:
        return ""


class CS25ELogin:
    def __init__(self) -> None:
        self._key: str = ""
        self._unique_id: str = ""

    async def apply_qr(self) -> QRCodeResult:
        self._unique_id = str(uuid.uuid4())
        pool = get_pool()
        resp = await pool.request(
            "POST",
            url=QR_APPLY_URL,
            data={"unique_id": self._unique_id},
            headers=_HEADERS,
        )
        data = resp.json()
        result = data["data"]
        self._key = result["key"]
        b64 = result["qr_code"].split("base64,")[1]
        img_bytes = base64.b64decode(b64)
        logger.info(f"[CS2][5E] 申请二维码成功, key: {self._key[:8]}...")
        return QRCodeResult(key=self._key, qr_code_bytes=img_bytes)

    async def check_qr_status(self) -> int:
        if not self._key:
            return -1
        pool = get_pool()
        resp = await pool.request(
            "POST",
            url=QR_CHECK_URL,
            data={"key": self._key},
            headers=_HEADERS,
        )
        data = resp.json()
        status: int = data["data"]["status"]
        return status

    async def wait_for_scan(self) -> LoginResult:
        for i in range(MAX_POLL_COUNT):
            status = await self.check_qr_status()
            if status == 2:
                logger.info("[CS2][5E] 扫码成功")
                return LoginResult(success=True, message="扫码成功")
            if status == -1:
                return LoginResult(
                    success=False, message="key 不存在，请先申请二维码"
                )
            logger.debug(f"[CS2][5E] 等待扫码... [{i + 1}/{MAX_POLL_COUNT}]")
            await asyncio.sleep(POLL_INTERVAL)
        return LoginResult(success=False, message="扫码超时，请重新操作")

    async def confirm_login(self) -> LoginResult:
        """扫码后调 `/api/user/login` 换取正式 token。"""
        if not self._key:
            return LoginResult(success=False, message="key 不存在")
        pool = get_pool()
        try:
            resp = await pool.request(
                "POST",
                url=CONFIRM_LOGIN_URL,
                data={
                    "scan_code_login_yn": "true",
                    "scan_code_login_key": self._key,
                },
                headers=_HEADERS,
            )
            body = resp.json()
            if body.get("success"):
                token: str = body["data"]["token"]
                logger.info("[CS2][5E] 登录确认成功")
                return LoginResult(
                    success=True,
                    message="登录成功",
                    token=token,
                )
            return LoginResult(
                success=False,
                message=body.get("message", "登录确认失败"),
            )
        except Exception as e:
            return LoginResult(success=False, message=f"登录确认异常: {e}")

    async def login_by_qr(self) -> tuple[QRCodeResult, LoginResult]:
        qr = await self.apply_qr()
        result = await self.wait_for_scan()
        if not result.success:
            return qr, result
        result = await self.confirm_login()
        return qr, result
