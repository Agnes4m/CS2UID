from gsuid_core.models import Event

from ..utils.database.models import CS2User


async def add_token(ev: Event, tk: str):
    await CS2User.insert_data(ev.user_id, ev.bot_id, cookie=tk)
    return "完美token添加成功！"


async def add_stoken(ev: Event, sk: str):
    if await CS2User.data_exist(user_id=ev.user_id, bot_id=ev.bot_id):
        await CS2User.update_data(ev.user_id, ev.bot_id, stoken=sk)
    else:
        await CS2User.insert_data(ev.user_id, ev.bot_id, stoken=sk, cookie="")
    return "5etoken添加成功！"


async def add_uid(ev: Event, uid: str):
    await CS2User.insert_data(ev.user_id, ev.bot_id, uid=uid)
    return "添加成功！"
