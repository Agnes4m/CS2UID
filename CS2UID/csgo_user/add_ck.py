from gsuid_core.models import Event

from ..utils.database.models import CS2User


async def add_token(ev: Event, tk: str):
    await CS2User.insert_data(ev.user_id, ev.bot_id, cookie=tk)
    return '添加成功！'


async def add_uid(ev: Event, uid: str):
    await CS2User.insert_data(ev.user_id, ev.bot_id, uid=uid)
    return '添加成功！'
