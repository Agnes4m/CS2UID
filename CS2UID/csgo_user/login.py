"""CS2 扫码登录 (handler 层)。"""

import asyncio

from gsuid_core.bot import Bot
from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV

from ..utils.api.login import (
    MAX_POLL_COUNT,
    POLL_INTERVAL,
    CS2Login,
    build_qrcode_payload,
)
from ..utils.database.models import CS2Bind, CS2User

cs2_qr_login = SV("CS2扫码登录")


async def _save_qr_login(ev: Event, steam_id: str, token: str) -> str:
    await CS2User.insert_data(
        ev.user_id, ev.bot_id, cookie=token, uid=steam_id
    )
    await CS2Bind.insert_uid(
        ev.user_id, ev.bot_id, steam_id, ev.group_id, is_digit=False
    )
    logger.info(f"[CS2][QR] 绑定成功 steam_id={steam_id}")
    return f"扫码登录成功！\nSteamID: {steam_id}\n已自动绑定"


@cs2_qr_login.on_command(("扫码登录", "登录"), block=True)
async def handle_qr_login(bot: Bot, ev: Event):
    path = get_res_path(["CS2UID", "qr"]) / f"cs2_qr_{ev.user_id}.png"
    login = CS2Login()
    try:
        logger.info("正在申请二维码...")
        qr_url = await login.apply_qr()

        img_data = build_qrcode_payload(qr_url, path, ev.bot_id)
        await bot.send(
            [
                MessageSegment.text(
                    "请使用完美世界电竞APP扫描下方二维码登录："
                ),
                MessageSegment.image(img_data),
                MessageSegment.text(
                    "扫描后请在APP中确认登录... (等待时间约60秒)"
                ),
            ]
        )
        logger.info("请在APP中确认登录... (等待时间约60秒)")

        for i in range(MAX_POLL_COUNT):
            result = await login.check_qr_status()
            status = result.get("status")

            if status == 2:
                account_item = result.get("accountItem", {})
                steam_id = account_item.get("steamId", "")
                token = result.get("token", "")
                msg = await _save_qr_login(ev, steam_id, token)
                await bot.send(f"✅ {msg}")
                return

            if status == 3:
                await bot.send("❌ 二维码已过期，请重新扫码")
                return

            if status == 1 and i % 5 == 0:
                await bot.send(f"等待扫码中... [{i + 1}/{MAX_POLL_COUNT}]")

            await asyncio.sleep(POLL_INTERVAL)

        await bot.send("❌ 扫码超时，请重新操作")

    except Exception as e:
        logger.error(f"[CS2][QR] 登录异常: {e}")
        await bot.send(f"❌ 登录异常: {e}")
    finally:
        if path.exists():
            path.unlink()
