from pathlib import Path
from typing import Union

from PIL import Image
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.csgo_api import pf_api
from ..utils.api.models import MatchTotal
from ..utils.error_reply import get_error
from .utils import (
    save_img,
    paste_img,
    add_detail,
    load_groudback,
    simple_paste_img,
)

TEXTURE = Path(__file__).parent / "texture2d"


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
    # map_img = await load_groudback(map_img, 0.9)
    if base["winTeam"] == 1:
        team1 = "green"
        team2 = "grey"
    else:
        team1 = "grey"
        team2 = "green"
    await paste_img(
        map_img, str(base["score1"]), size=70, site=(200, 150), color=team1
    )
    await paste_img(
        map_img, str(base["score2"]), size=70, site=(500, 150), color=team2
    )
    await paste_img(
        map_img,
        str(base["halfScore1"]),
        size=40,
        site=(350, 150),
        color="gold",
    )
    await paste_img(
        map_img,
        str(base["halfScore2"]),
        size=40,
        site=(400, 150),
        color="blue",
    )
    await paste_img(
        map_img,
        str(base["score1"] - base["halfScore1"]),
        size=40,
        site=(350, 180),
        color="blue",
    )
    await paste_img(
        map_img,
        str(base["score2"] - base["halfScore2"]),
        size=40,
        site=(400, 180),
        color="gold",
    )
    await simple_paste_img(map_img, "-", (375, 150), size=40)
    await simple_paste_img(map_img, "-", (375, 180), size=40)

    await simple_paste_img(map_img, "比赛地图", (50, 250), size=30)
    await simple_paste_img(map_img, base["map"], (50, 300), size=30)
    await simple_paste_img(map_img, "地图时长", (220, 250), size=30)
    await simple_paste_img(
        map_img, f"{base['duration']}分钟", (220, 300), size=30
    )
    await simple_paste_img(map_img, "结束时间", (390, 250), size=30)
    await simple_paste_img(
        map_img, str(base["endTime"][:10]).strip(), (390, 300), size=30
    )
    await simple_paste_img(
        map_img, str(base["endTime"][11:]).strip(), (390, 340), size=30
    )
    await simple_paste_img(map_img, "匹配方式", (560, 250), size=30)
    if base["greenMatch"]:
        await simple_paste_img(
            map_img, "天梯绿色对局", (560, 300), size=30, color="green"
        )
    else:
        await simple_paste_img(
            map_img, "天梯普通对局", (560, 300), size=30, color="blue"
        )
    img_bg.paste(map_img, (75, -100), mask=map_img)
    print(players[0])

    for index, player in enumerate(players):
        play_bg = Image.open(TEXTURE / "icon" / "main1.png").resize((700, 100))
        head = (await save_img(player["avatar"], "avatar")).resize((50, 50))
        play_bg.paste(head, (25, 25), mask=head)
        await simple_paste_img(play_bg, "昵称", (100, 20))
        await simple_paste_img(play_bg, player["nickName"][:8], (100, 60))
        await simple_paste_img(play_bg, "K/D/A", (280, 20))
        await simple_paste_img(
            play_bg,
            f"{player['kill']}/{player['death']}/{player['assist']}",
            (280, 60),
        )
        await simple_paste_img(play_bg, "首K/D", (380, 20))
        await simple_paste_img(
            play_bg,
            f"{player['entryKill']}/{player['entryDeath']}",
            (380, 60),
        )
        await simple_paste_img(play_bg, "爆头率", (470, 20))
        await simple_paste_img(
            play_bg, f"{player['headShotRatio']:.2f}%", (470, 60)
        )
        await simple_paste_img(play_bg, "WE", (550, 20))
        await simple_paste_img(play_bg, f"{player['we']:.2f}", (550, 60))
        await simple_paste_img(play_bg, "RT", (630, 20))
        await simple_paste_img(play_bg, f"{player['rating']:.2f}", (630, 60))

        if index >= 5:
            ex_spwan = 100
        else:
            ex_spwan = 0
        img_bg.paste(
            play_bg, (100, 400 + index * 110 + ex_spwan), mask=play_bg
        )

    return await convert_img(await add_detail(img_bg))
