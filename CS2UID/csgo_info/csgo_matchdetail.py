from pathlib import Path
from typing import Union

from PIL import Image

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from .utils import font_head, save_img
from ..utils.api.models import MatchTotal
from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error
from .utils import add_detail, load_groudback, save_img, simple_paste_img

TEXTURE = Path(__file__).parent / "texture2d"
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
    map_img = await load_groudback(map_img, 0.8)
    if base["winTeam"] == 1:
        team1 = "green"
        team2 = "white"
    else:
        team1 = "white"
        team2 = "green"
    await simple_paste_img(map_img, str(base["score1"]), (200, 150), size=70, color=team1)
    await simple_paste_img(map_img, str(base["score2"]), (500, 150), size=70, color=team2)
    await simple_paste_img(map_img, str(base["halfScore1"]), (350, 150), size=40, color="gold")
    await simple_paste_img(map_img, str(base["halfScore2"]), (400, 150), size=40, color="blue")
    await simple_paste_img(map_img, str(base["score1"] - base["halfScore1"]), (350, 180), size=40, color="blue")
    await simple_paste_img(map_img, str(base["score2"] -base["halfScore2"]), (400, 180), size=40, color="gold")
    await simple_paste_img(map_img, "-", (375, 150), size=40)
    await simple_paste_img(map_img, "-", (375, 180), size=40)
    
    
    await simple_paste_img(map_img, "比赛地图", (50, 250), size=30)
    await simple_paste_img(map_img, base["map"], (50, 300), size=30)
    await simple_paste_img(map_img, "地图时长", (220, 250), size=30)
    await simple_paste_img(map_img, f"{base['duration']}分钟", (220, 300), size=30)
    await simple_paste_img(map_img, "结束时间", (390, 250), size=30)
    await simple_paste_img(map_img, str(base["endTime"][:10]).strip(), (390, 300), size=30)
    await simple_paste_img(map_img, str(base["endTime"][11:]).strip(), (390, 340), size=30)   
    await simple_paste_img(map_img, "匹配方式", (560, 250), size=30)
    if base["greenMatch"]:
        await simple_paste_img(map_img, "天梯绿色对局", (560, 300), size=30, color="green")
    else:
        await simple_paste_img(map_img, "天梯普通对局", (560, 300), size=30,color="blue")
    img_bg.paste(map_img, (75, -100), mask=map_img)
    print(players[0])
    
    for index, player in enumerate(players):
        play_bg = Image.open(TEXTURE / "icon" / "main.png").resize((800, 200))
        head = await save_img(player["avatar"], "avatar")
        play_bg.paste(head, (50, 100), mask=head)
        await simple_paste_img(play_bg, "昵称", (100, 20), size=30)
        await simple_paste_img(play_bg, player["nickName"], (100, 60), size=30)
        await simple_paste_img(play_bg, f"{player['kill']}/{player['entryKill']}", (100, 50), size=30)
        
        img_bg.paste(play_bg, (100, 500 + index * 300), mask=play_bg)

    return await convert_img(await add_detail(img_bg))
