from pathlib import Path

from PIL import Image

from gsuid_core.subscribe import gs_subscribe
from gsuid_core.status.plugin_status import register_status

from ..utils.database.models import CS2Bind, CS2User

ICON = Path(__file__).parent.parent.parent / "img/logo.jpg"


def get_ICON():
    return Image.open(ICON)


async def get_user_num():
    datas = await CS2User.get_all_cookie()
    return len(datas)


async def get_add_num():
    datas = await CS2Bind.get_all_data()
    all_uid = []
    for data in datas:
        if data.uid:
            all_uid.extend(data.user_id.split("_"))
    return len(set(all_uid))



register_status(
    get_ICON(),
    "CS2UID",
    {
        "账户数量": get_add_num,
        "用户数量": get_user_num,
    },
)
