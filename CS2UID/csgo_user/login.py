"""CS2 扫码登录 (handler 层)。"""

import asyncio

from gsuid_core.bot import Bot
from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV

from ..utils.api.login import (
    MAX_POLL_COUNT as PF_MAX_POLL_COUNT,
)
from ..utils.api.login import (
    POLL_INTERVAL as PF_POLL_INTERVAL,
)
from ..utils.api.login import (
    CS2Login,
    build_qrcode_payload,
)
from ..utils.api.login_5e import CS25ELogin, _decode_jwt_uid
from ..utils.csgo_config import majs_config
from ..utils.database.models import CS2Bind, CS2User

cs2_qr_login = SV("CS2扫码登录")

_PLATFORM_MAP = {"完美": "pf", "5e": "5e"}


async def _save_qr_login(ev: Event, steam_id: str, token: str) -> str:
    await CS2User.insert_data(
        ev.user_id, ev.bot_id, cookie=token, uid=steam_id
    )
    await CS2Bind.insert_uid(
        ev.user_id, ev.bot_id, steam_id, ev.group_id, is_digit=False
    )
    logger.info(f"[CS2][QR] 绑定成功 steam_id={steam_id}")
    return f"扫码登录成功！\nSteamID: {steam_id}\n已自动绑定"


def _resolve_platform(ev: Event) -> str:
    text = ev.text.strip()
    if not text:
        return _PLATFORM_MAP.get(
            str(majs_config.get_config("DefaultLoginPlatform").data), "pf"
        )
    return _PLATFORM_MAP.get(text, text)


@cs2_qr_login.on_command(("扫码登录", "登录"), block=True)
async def handle_qr_login(bot: Bot, ev: Event):
    platform = _resolve_platform(ev)
    if platform == "5e":
        await _handle_5e_login(bot, ev)
    else:
        await _handle_pf_login(bot, ev)


async def _handle_5e_login(bot: Bot, ev: Event):
    path = get_res_path(["CS2UID", "qr"]) / f"cs2_5e_qr_{ev.user_id}.png"
    login = CS25ELogin()
    try:
        logger.info("正在申请5E二维码...")
        qr = await login.apply_qr()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(qr.qr_code_bytes)

        await bot.send(
            [
                MessageSegment.text("请使用5E对战平台APP扫描下方二维码登录："),
                MessageSegment.image(qr.qr_code_bytes),
                MessageSegment.text(
                    "扫描后请在APP中确认登录... (等待时间约60秒)"
                ),
            ]
        )

        scan_result = await login.wait_for_scan()
        if not scan_result.success:
            await bot.send(f"❌ {scan_result.message}")
            return

        result = await login.confirm_login()
        if result.success and result.token:
            uid = _decode_jwt_uid(result.token)
            await CS2User.insert_data(
                ev.user_id, ev.bot_id, cookie=result.token, uid=uid
            )
            await CS2Bind.insert_uid(
                ev.user_id, ev.bot_id, uid, ev.group_id, is_digit=False
            )
            await bot.send(f"✅ 5E登录成功！\n5E UID: {uid}\n已自动绑定")
            logger.info(f"[CS2][5E] 登录成功 uid={uid}")
        else:
            await bot.send(f"❌ {result.message}")

    except Exception as e:
        logger.error(f"[CS2][5E] 登录异常: {e}")
        await bot.send(f"❌ 登录异常: {e}")
    finally:
        if path.exists():
            path.unlink()


async def _handle_pf_login(bot: Bot, ev: Event):
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

        for i in range(PF_MAX_POLL_COUNT):
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
                await bot.send(f"等待扫码中... [{i + 1}/{PF_MAX_POLL_COUNT}]")

            await asyncio.sleep(PF_POLL_INTERVAL)

        await bot.send("❌ 扫码超时，请重新操作")

    except Exception as e:
        logger.error(f"[CS2][QR] 登录异常: {e}")
        await bot.send(f"❌ 登录异常: {e}")
    finally:
        if path.exists():
            path.unlink()
