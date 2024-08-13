from pathlib import Path
from typing import Union

from PIL import Image

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.api.models import MatchDetail
from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error
from .utils import add_detail, load_groudback

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


async def draw_csgo_match_img(detail: MatchDetail) -> bytes | str:
    """做图"""
    if not detail:
        return "token已过期"
    img_bg = await load_groudback(Path(TEXTURE / "bg" / "4.jpg"))

    text_img = await convert_img(await add_detail(img_bg))
    return "todo"
