import random
import datetime
from pathlib import Path
from typing import Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.utils import download_pic_to_image
from gsuid_core.utils.image.image_tools import draw_pic_with_ring

from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error
from ..utils.api.models import UserHomedetailData


async def get_csgohome_info_img(uid: str) -> Union[str, bytes]:

    detail = await pf_api.get_csgohomedetail(uid)

    if isinstance(detail, int):
        return get_error(detail)

    return await draw_csgohome_info_img(detail['data'])



async def draw_csgohome_info_img(detail: UserHomedetailData) -> bytes | str:
    if not detail:
        return "token已过期"
    name = detail["nickName"]
    uid = detail["steamId"]
    uid = uid[:4] + "********" + uid[12:]
    avatar = detail["avatar"]
    return 1