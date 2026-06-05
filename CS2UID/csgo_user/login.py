"""CS2 扫码登录"""

import io
import asyncio
from pathlib import Path

import qrcode
import aiohttp
import aiofiles
from qrcode.constants import ERROR_CORRECT_L
from qrcode.image.pil import PilImage

from gsuid_core.sv import SV, Bot, Event
from gsuid_core.logger import logger
from gsuid_core.segment import MessageSegment
from gsuid_core.data_store import get_res_path

from ..utils.database.models import CS2Bind, CS2User

cs2_qr_login = SV("CS2扫码登录")

QR_APPLY_URL = "https://passport.pwesports.cn/qrAuth/applyToken"
QR_CHECK_URL = "https://passport.pwesports.cn/qrAuth/check"
APP_ID = "5"
QR_TYPE = "1"
WEBSITE = "pvp"
POLL_INTERVAL = 2
MAX_POLL_COUNT = 30


async def get_qrcode_base64(url: str, path: Path, bot_id: str) -> bytes | str:
    qr = qrcode.QRCode(
        version=1, error_correction=ERROR_CORRECT_L, box_size=10, border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(255, 134, 36), back_color="white")
    assert isinstance(img, PilImage)

    if bot_id == "onebot":
        img = img.resize((700, 700))
        img.save(
            path, format="PNG", save_all=True, append_images=[img], duration=100, loop=0
        )
        async with aiofiles.open(path, "rb") as fp:
            img = await fp.read()
    else:
        img_byte = io.BytesIO()
        img.save(img_byte, format="PNG")
        img = img_byte.getvalue()
    return img


async def save_qr_login(ev: Event, steam_id: str, token: str) -> str:
    await CS2User.insert_data(ev.user_id, ev.bot_id, cookie=token, uid=steam_id)
    await CS2Bind.insert_uid(
        ev.user_id, ev.bot_id, steam_id, ev.group_id, is_digit=False
    )
    logger.info(f"[CS2][QR] 绑定成功 steam_id={steam_id}")
    return f"扫码登录成功！\nSteamID: {steam_id}\n已自动绑定"


async def apply_qr_code() -> tuple[str, str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            QR_APPLY_URL,
            json={
                "appId": APP_ID,
                "qrType": QR_TYPE,
                "redirect": False,
                "website": WEBSITE,
            },
        ) as resp:
            data = await resp.json()
    qr_url = data["result"]["accessUrl"]
    access_token = qr_url.split("accessToken=")[1].split("&")[0]
    return qr_url, access_token


async def check_qr_status(access_token: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            QR_CHECK_URL, json={"appId": APP_ID, "accessToken": access_token}
        ) as resp:
            data = await resp.json()
    return data.get("result", {})


@cs2_qr_login.on_command(("扫码登录", "登录"), block=True)
async def handle_qr_login(bot: Bot, ev: Event):
    path = get_res_path(["CS2UID", "qr"]) / f"cs2_qr_{ev.user_id}.png"
    try:
        logger.info("正在申请二维码...")
        qr_url, access_token = await apply_qr_code()

        img_data = await get_qrcode_base64(qr_url, path, ev.bot_id)
        await bot.send(
            [
                MessageSegment.text("请使用完美世界电竞APP扫描下方二维码登录："),
                MessageSegment.image(img_data),
                MessageSegment.text("扫描后请在APP中确认登录... (等待时间约60秒)"),
            ]
        )

        logger.info("请在APP中确认登录... (等待时间约60秒)")

        for i in range(MAX_POLL_COUNT):
            result = await check_qr_status(access_token)
            status = result.get("status")

            if status == 2:
                account_item = result.get("accountItem", {})
                steam_id = account_item.get("steamId", "")
                token = result.get("token", "")
                msg = await save_qr_login(ev, steam_id, token)
                await bot.send(f"✅ {msg}")
                return
            elif status == 3:
                await bot.send("❌ 二维码已过期，请重新扫码")
                return
            elif status == 1 and i % 5 == 0:
                await bot.send(f"等待扫码中... [{i + 1}/{MAX_POLL_COUNT}]")

            await asyncio.sleep(POLL_INTERVAL)

        await bot.send("❌ 扫码超时，请重新操作")

    except Exception as e:
        logger.error(f"[CS2][QR] 登录异常: {e}")
        await bot.send(f"❌ 登录异常: {e}")
    finally:
        if path.exists():
            path.unlink()
