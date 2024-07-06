from pathlib import Path
from typing import Union

from PIL import Image
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.csgo_api import pf_api
from .config import TEXTURE, ICON_PATH
from ..utils.api.models import UserDetailData
from ..utils.error_reply import not_msg, get_error
from .utils import (
    add_detail,
    assign_rank,
    new_para_img,
    make_head_img,
    load_groudback,
    make_weapen_img,
    simple_paste_img,
)


async def get_csgo_info_img(uid: str) -> Union[str, bytes]:
    detail = await pf_api.get_userdetail(uid)

    # print(detail)
    if isinstance(detail, int):
        return get_error(detail)

    try:
        if detail['statusCode'] != 0:
            return f"数据过期，错误代码为{detail['statusCode']}"
    except Exception:
        logger.warning("获取用户详情失败！")

    if len(detail['data']['scoreList']) == 0:
        return not_msg
    return await draw_csgo_info_img(detail['data'])


async def draw_csgo_info_img(detail: UserDetailData) -> bytes | str:
    if not detail:
        return "token已过期"
    name = detail["name"]
    uid = detail["steamId"]
    uid = uid[:4] + "********" + uid[12:]
    avatar = detail["avatar"]

    # 背景图
    img = await load_groudback(Path(TEXTURE / "bg" / "1.jpg"))

    # 头像

    head_img = await make_head_img(f"uid：  {uid}", f"昵称：  {name}", avatar)

    img.paste(head_img, (0, 0), head_img)
    rank_scoce = detail["pvpScore"]
    rank = await assign_rank(rank_scoce)

    await simple_paste_img(
        img=img,
        msg=f"天梯段位:{rank}  天梯段位分:{rank_scoce}  星数:{detail['stars']}",
        site=(50, 100),
        size=30,
        fonts="head",
    )

    # 基础信息表
    main_img = Image.open(ICON_PATH / "main1.png").resize((800, 420))
    img.paste(main_img, (50, 270), main_img)

    await simple_paste_img(img, f"赛季：{detail['seasonId']}", (100, 350))
    await simple_paste_img(img, f"场次：{detail['cnt']}", (100, 380))
    await simple_paste_img(img, f"胜率：{detail['winRate']}", (100, 410))
    await simple_paste_img(img, f"完美RT：{detail['pwRating']}", (100, 440))
    await simple_paste_img(img, f"RWS：{detail['rws']}", (100, 470))
    await simple_paste_img(img, f"ADR：{detail['adr']}", (100, 500))
    await simple_paste_img(img, f"WE评价：{detail['avgWe']}", (100, 530))

    await simple_paste_img(img, f"K/D：{detail['kd']}", (300, 350))
    await simple_paste_img(img, f"击杀数：{detail['kills']}", (300, 380))
    await simple_paste_img(img, f"死亡数：{detail['deaths']}", (300, 410))
    await simple_paste_img(img, f"助攻数：{detail['assists']}", (300, 440))
    await simple_paste_img(img, f"MVP数：{detail['mvpCount']}", (300, 470))
    await simple_paste_img(
        img, f"爆头率：{detail['headShotRatio']}", (300, 500)
    )
    await simple_paste_img(
        img, f"首杀率：{detail['entryKillRatio']}", (300, 530)
    )

    """武器"""
    for i in range(8):
        site_x = 20
        site_y = 720
        s = i
        if s >= 4:
            site_y += 310
            s -= 4
        site_x += 220 * s

        usr_weapon = detail['hotWeapons2'][i]

        one_weapen_img = await make_weapen_img(usr_weapon)
        img.paste(one_weapen_img, (site_x, site_y), one_weapen_img)

    """地图战绩"""
    map_msg_list = detail['hotMaps']
    print(f"地图种数{len(map_msg_list)}")

    if map_msg_list is None:
        pass
    s = min(4, len(map_msg_list))
    for i in range(s):
        site_x = 10 + i * 220
        site_y = 1350
        usr_map = map_msg_list[i]
        map_img = await new_para_img(usr_map['mapImage'], usr_map['mapLogo'])
        img.paste(map_img, (site_x, site_y), map_img)

        #     await paste_img(img, "地图战绩", 20, (site_x, site_y))
        #     await paste_img(
        #         img, f"地图：{usr_map['mapName']}", 20, (site_x, site_y + 30)
        #     )
        Match = usr_map['totalMatch']
        await simple_paste_img(
            img,
            f"场次：{usr_map['totalMatch']}",
            (site_x + 10, site_y + 200),
            color=(255, 255, 255, 255),
        )
        win_percent = usr_map['winCount'] / Match
        await simple_paste_img(
            img,
            f"胜率：{win_percent*100:.2f}%",
            (site_x + 10, site_y + 240),
            color=(255, 255, 255, 255),
        )
        await simple_paste_img(
            img,
            f"K/D：{usr_map['totalKill']} / {usr_map['deathNum']}",
            (site_x + 10, site_y + 280),
            color=(255, 255, 255, 255),
        )
        await simple_paste_img(
            img,
            f"首杀：{usr_map['firstKillNum']}",
            (site_x + 10, site_y + 320),
            color=(255, 255, 255, 255),
        )
        headshotpercent = usr_map['headshotKillNum'] / usr_map['totalKill']
        await simple_paste_img(
            img,
            f"爆头率：{headshotpercent*100:.2f}%",
            (site_x + 10, site_y + 360),
            color=(255, 255, 255, 255),
        )
        await simple_paste_img(
            img,
            f"MVP：{usr_map['matchMvpNum']}",
            (site_x + 10, site_y + 400),
            color=(255, 255, 255, 255),
        )
        rws = usr_map['rwsSum'] / Match
        await simple_paste_img(
            img,
            f"RWS：{rws:.2f}",
            (site_x + 10, site_y + 440),
            color=(255, 255, 255, 255),
        )
        adr = usr_map['totalAdr'] / Match
        await simple_paste_img(
            img,
            f"ARD：{adr:.2f}",
            (site_x + 10, site_y + 480),
            color=(255, 255, 255, 255),
        )
        rt = usr_map['ratingSum'] / Match
        await simple_paste_img(
            img,
            f"RT：{rt:.2f}",
            (site_x + 10, site_y + 520),
            color=(255, 255, 255, 255),
        )
    """最近战绩"""
    # await paste_img(img, "最近战绩", 20, (60, 1350))
    # print(f"交战记录{len(detail['scoreList'])}")
    # if len(detail['scoreList']) < 20:
    #     x = len(detail['scoreList'])
    # else:
    #     x = 20
    # for i in range(x):
    #     s = i
    #     site_x = 60
    #     site_y = 1400
    #     if s >= 10:
    #         site_x += 400
    #         s -= 10
    #     while s > 0:
    #         s -= 1
    #         site_y += 30

    #     match = detail['scoreList'][i]
    #     real_time = datetime.datetime.fromtimestamp(match['time'])
    #     if match['score'] == 0:
    #         msg = f"{i+1}. 无段位 . 时间{real_time}"
    #     else:
    #         msg = f"{i+1}. 得分{match['score']} . 时间{real_time}"

    #     await paste_img(img, msg, 20, (site_x, site_y))

    return await convert_img(await add_detail(img))
