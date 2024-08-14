from pathlib import Path
from typing import Union

from PIL import Image

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.api.models import MatchTotal
from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error
from .utils import add_detail, load_groudback, save_img

TEXTURE = Path(__file__).parent / "texture2d"
FONT_PATH = Path(__file__).parent / "font/萝莉体 第二版.ttf"
green_logo = Image.open(TEXTURE / "green.png")


async def get_csgo_match_detail_img(match_id: str) -> Union[str, bytes]:
    detail = await pf_api.get_match_detail(match_id)
    logger.debug(detail)
    if isinstance(detail, int):
        return get_error(detail)
    if isinstance(detail, str):
        return detail

    return await draw_csgo_match_img(
        detail,
    )


async def draw_csgo_match_img(detail: MatchTotal) -> bytes | str:
    """做图"""
    base = detail["base"]
    players = detail["players"]
    if not detail:
        return "token已过期"
    img_bg = await load_groudback(Path(TEXTURE / "bg" / "5.jpg"))

    # 总分数部分
    # 750*480
    map_img = await save_img(base["mapUrl"], "map")
    print(map_img.size)
    img_bg.paste(map_img, (0, 0), mask=map_img)

    return await convert_img(await add_detail(img_bg))
