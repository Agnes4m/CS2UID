import math
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw

# from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import easy_paste, draw_pic_with_ring

from .csgo_path import TEXTURE
from ..utils.csgo_api import api_5e
from ..utils.error_reply import get_error
from ..utils.api.models import UserHomeDetail5, UserSeason5
from .utils import save_img, resize_image_to_percentage
from ..utils.csgo_font import csgo_font_20, csgo_font_30, csgo_font_42


async def get_csgo_5einfo_img(uid: str, season: str = "") -> Union[str, bytes]:
    detail = await api_5e.get_user_detail(uid)
    
    # logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)
    
    year, season = detail["season_data"]["now_season_v1"].split(" ")
    season = season.replace("S", "").strip()
    info = await api_5e.get_user_homeall(uid, year, season)
    if isinstance(info, int):
        return get_error(info)
    return await draw_csgo_5einfo_img(detail, info)


async def draw_csgo_5einfo_img(detail: UserHomeDetail5, info: UserSeason5) -> bytes | str:
    if not detail:
        return "token已过期"
    user_info = detail["user"]
    total_info = detail["career_data"]
    season_info = detail["season_data"]
    name = user_info["username"]
    uid = f"id: {user_info['domain']}"
    avatar = user_info["avatar_url"]

    # 背景图
    img = Image.open(TEXTURE / "base" / "bg.jpg")
    img_bg = Image.open(Path(TEXTURE / "bg" / "5.jpg")).resize((1000, 2400))
    new_alpha = Image.new('L', img_bg.size, 128)
    img_bg_out = Image.merge('RGBA', (img_bg.split()[:3] + (new_alpha,)))
    img.paste(img_bg_out, (0, 0), img_bg_out)

    # 标题
    titel_img = Image.open(TEXTURE / "base" / "title_bg.png")
    head = await save_img(avatar, "avatar")
    round_head = await draw_pic_with_ring(head, 80)

    easy_paste(titel_img, round_head, (112, 108), "cc")
    head_draw = ImageDraw.Draw(titel_img)
    head_draw.text((250, 50), name, (255, 255, 255, 255), csgo_font_42)
    head_draw.text((250, 100), uid, (255, 255, 255, 255), csgo_font_30)
    head_draw.line([(250, 150), (550, 150)], fill='white', width=2)
    img.paste(titel_img, (0, 55), titel_img)
    # 颜色小标识

    # 最高信息表
    main1_img = Image.open(TEXTURE / "base" / "banner.png")
    main1_draw = ImageDraw.Draw(main1_img)
    main1_draw.text((50, 10), "历史最高", (255, 255, 255, 255), csgo_font_42)

    img.paste(main1_img, (0, 330), main1_img)

    main11_img = Image.open(TEXTURE / "base" / "base5e_bg.png")
    main11_draw = ImageDraw.Draw(main11_img)
    main11_draw.text(
        (260, 80),
        f"{total_info['match_time_total']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main11_draw.text(
        (415, 80),
        f"{total_info['rating']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main11_draw.text(
        (570, 80),
        f"{total_info['match_total']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main11_draw.text(
        (725, 80),
        f"{total_info['per_win_match']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main11_draw.text(
        (880, 80),
        f"{total_info['elo']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    level_img = await save_img(total_info["level_url"], "level")
    level_img = await resize_image_to_percentage(level_img, 60)
    main11_img.paste(level_img, (50, 30), level_img)
    img.paste(main11_img, (0, 410), main11_img)

    # 赛季信息
    main2_img = Image.open(TEXTURE / "base" / "banner.png")
    main2_draw = ImageDraw.Draw(main2_img)
    main2_draw.text(
        (50, 10), season_info["now_season"], (255, 255, 255, 255), csgo_font_42
    )

    img.paste(main2_img, (0, 620), main2_img)

    # 赛季主信息
    main22_img = Image.open(TEXTURE / "base" / "base_5ebg.png")

    main22_draw = ImageDraw.Draw(main22_img)
    season_list = season_info["season_list"][0]

    # 等级和优先分数
    level_img = await save_img(season_list['level_url'], "level")
    level_img = await resize_image_to_percentage(level_img, 60)
    main22_img.paste(level_img, (50, 40), level_img)
    level_bg = await save_img(season_list['level_bg_url'], "level_bg")
    # logger.info(season_list['level_bg_url'])
    level_bg = await resize_image_to_percentage(level_bg, 60)
    level_draw = ImageDraw.Draw(level_bg)
    level_draw.text(
        (70, 25),
        season_list['elo'],
        (255, 255, 255, 255),
        csgo_font_30,
        "mm",
    )
    main22_img.paste(level_bg, (50, 200), level_bg)

    # main22_draw.text(
    #     (260, 80),
    #     f"{detail['avgWe']:.1f}",
    #     (255, 255, 255, 255),
    #     csgo_font_42,
    #     "mm",
    # )
    main22_draw.text(
        (415, 80),
        f"{detail['career_data']['rating']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main22_draw.text(
        (570, 80),
        f"{season_list['rws']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main22_draw.text(
        (725, 80),
        f"{season_list['adr']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    # main22_draw.text(
    #     (880, 80),
    #     f"{season_list['entryKillRatio']}%",
    #     (255, 255, 255, 255),
    #     csgo_font_42,
    #     "mm",
    # ) # 爆头率

    main22_draw.text(
        (260, 230),
        str(season_list['match_total']),
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main22_draw.text(
        (415, 230),
        f"{season_list['per_win_match']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    # main22_draw.text(
    #     (570, 230),
    #     f"{detail['kd']:.2f}",
    #     (255, 255, 255, 255),
    #     csgo_font_42,
    #     "mm",
    # )  KD
    # main22_draw.text(
    #     (725, 230),
    #     f"{detail['headShotRatio'] * 100:.1f}%",
    #     (255, 255, 255, 255),
    #     csgo_font_42,
    #     "mm",
    # ) 爆头率
    # main22_draw.text(
    #     (880, 230),
    #     f"{detail['mvpCount']}",
    #     (255, 255, 255, 255),
    #     csgo_font_42,
    #     "mm",
    # ) MVP

    img.paste(main22_img, (0, 700), main22_img)

    # 地图信息表
    # main1_img = Image.open(TEXTURE / "base" / "banner.png")
    # main1_draw = ImageDraw.Draw(main1_img)
    # main1_draw.text((50, 10), "地图", (255, 255, 255, 255), csgo_font_42)

    # img.paste(main1_img, (0, 780), main1_img)

    # 地图
    # map_info = detail["match_data"]
    # for i in range(min(4, len(map_info))):
    #     map_detail = map_info[i]
    #     usr_map = map_detail['map_desc']
    #     # map_layer = Image.new("RGBA", (480, 180), (0, 0, 0, 0))
    #     # 750*480

    #     map_img = (
    #        await save_img(f"{map_detail['map_name'].lower()}.png", "map")
    #       ).resize(
    #         (470, 180)
    #     )
    #     new_alpha = Image.new('L', map_img.size, 128)
    #     map_img = Image.merge('RGBA', (map_img.split()[:3] + (new_alpha,)))

    #     map_logo = (
    #       await save_img(usr_map['mapLogo'],
    #       "map")).resize((50, 50))
    #     easy_paste(map_img, map_logo, (40, 100), "cc")
    #     map_draw = ImageDraw.Draw(map_img)
    #     map_draw.text(
    #         (110, 100),
    #         usr_map['mapName'],
    #         (255, 255, 255, 255),
    #         csgo_font_20,
    #         "mm",
    #     )
    #     map_draw.text(
    #         (180, 80),
    #         str(usr_map['totalMatch']),
    #         (255, 255, 255, 255),
    #         csgo_font_30,
    #         "mm",
    #     )
    #     map_draw.text((180, 120), "场次", "white", csgo_font_20, "mm")
    #     avg_win = usr_map['winCount'] / usr_map['totalMatch']
    #     map_draw.text(
    #         (260, 80),
    #         f"{avg_win * 100:.1f}%",
    #         (255, 255, 255, 255),
    #         csgo_font_30,
    #         "mm",
    #     )
    #     map_draw.text(
    #         (260, 120), "胜率", (255, 255, 255, 255), csgo_font_20, "mm"
    #     )
    #     avg_rat = usr_map['ratingSum'] / usr_map['totalMatch']
    #     adr = usr_map['totalAdr'] / usr_map['totalMatch']
    #     map_draw.text(
    #         (380, 80),
    #         f"{avg_rat:.2f} / {adr:.0f}",
    #         (255, 255, 255, 255),
    #         csgo_font_30,
    #         "mm",
    #     )
    #     map_draw.text(
    #         (380, 120), "RT/ADR", (255, 255, 255, 255), csgo_font_20, "mm"
    #     )
    #     if i % 2 == 0:
    #         site_x = 20
    #     else:
    #         site_x = 520
    #     site_y = 1090 + 200 * (i // 2 - 1)
    #     img.paste(map_img, (site_x, site_y), map_img)

    # 武器信息表
    # main3_img = Image.open(TEXTURE / "base" / "banner.png")
    # main3_draw = ImageDraw.Draw(main3_img)
    # main3_draw.text((50, 10), "武器", (255, 255, 255, 255), csgo_font_42)

    # img.paste(main3_img, (0, 1300), main3_img)

    # 武器
    # for i in range(min(8, len(detail['hotWeapons2']))):

    #     usr_weapon = detail['hotWeapons2'][i]

    #     base_img = Image.open(TEXTURE / "base" / "weapon_bg.png").resize(
    #         (500, 110)
    #     )
    #     weapon_img = await save_img(usr_weapon['image'], "weapon")
    #     weapon_img = weapon_img.resize(
    #         (int(weapon_img.size[0] * 0.2), int(weapon_img.size[1] * 0.2))
    #     )
    #     easy_paste(base_img, weapon_img, (100, 70), "cc")

    #     weapon_draw = ImageDraw.Draw(base_img)
    #     weapon_draw.text(
    #         (77, 17),
    #         usr_weapon['nameZh'],
    #         (255, 255, 255, 255),
    #         csgo_font_20,
    #         "mm",
    #     )
    #     weapon_draw.text(
    #         (204, 60),
    #         str(usr_weapon['killNum']),
    #         (255, 255, 255, 255),
    #         csgo_font_20,
    #         "mm",
    #     )
    #     weapon_draw.text(
    #         (375, 60),
    #         f"{usr_weapon['avgTimeToKill']}ms",
    #         (255, 255, 255, 255),
    #         csgo_font_20,
    #         "mm",
    #     )
    #     fsa = (
    #         f"{usr_weapon['firstShotAccuracy'] * 100:.2f}%"
    #         if usr_weapon['firstShotAccuracy'] is not None
    #         else "N/A"
    #     )
    #     if usr_weapon['sprayAccuracy'] is None:
    #         weapon_draw.text(
    #             (285, 60),
    #             fsa,
    #             (255, 255, 255, 255),
    #             csgo_font_20,
    #             "mm",
    #         )
    #     else:
    #         weapon_draw.text(
    #             (285, 60),
    #             f"{usr_weapon['sprayAccuracy'] * 100:.2f}%",
    #             (255, 255, 255, 255),
    #             csgo_font_20,
    #             "mm",
    #         )
    #     hdr = (
    #         f"{usr_weapon['headshotRate'] * 100:.2f}"
    #         if usr_weapon['headshotRate'] is not None
    #         else 0
    #     )
    #     weapon_draw.text(
    #         (430, 31), f"{hdr}", (255, 255, 255, 255), csgo_font_20, "mm"
    #     )

    #     if i % 2 == 0:
    #         site_x = 0
    #     else:
    #         site_x = 500
    #     site_y = 1510 + 120 * (i // 2 - 1)
    #     img.paste(base_img, (site_x, site_y), base_img)

    # 天梯段位
    # main4_img = Image.open(TEXTURE / "base" / "banner.png")
    # main4_draw = ImageDraw.Draw(main4_img)
    # main4_draw.text((50, 10), "分数曲线", (255, 255, 255, 255), csgo_font_42)
    # img.paste(main4_img, (0, 1880), main4_img)

    # score_list = detail['historyScores']
    # if len(score_list) > 0:
    #     score_list = score_list[:10]
    #     max_score = max(score_list)
    #     min_score = min(score_list)

    #     y_start = (min_score // 10) * 10
    #     y_end = ((max_score // 10) + 1) * 10

    #     width = 700
    #     height = 480
    #     padding = 100
    #     img_line = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    #     draw = ImageDraw.Draw(img_line)
    #     scale = (height - 2 * padding) / (y_end - y_start)

    #     draw.line(
    #         [(padding, height - padding),
    #           (width - padding, height - padding)],
    #         fill='black',
    #     )
    #     draw.line(
    #         [(padding, padding), (padding, height - padding)], fill='black'
    #     )

    #     for i in range(y_start, y_end + 1, 10):
    #         y = height - padding - (i - y_start) * scale
    #         draw.line([(padding - 5, y), (padding, y)], fill='black')
    #         draw.text(
    #             (padding - 50, y - 15), str(i),
    #               fill='white', font=csgo_font_20
    #         )

    #     for i in range(len(score_list)):
    #         x = padding + i * (width - 2 * padding) / (len(score_list) - 1)
    #         draw.line(
    #             [(x, height - padding), (x, height - padding + 5)],
    #             fill='black',
    #         )
    #         draw.text(
    #             (x - 10, height - padding + 10),
    #             str(i),
    #             fill='white',
    #             font=csgo_font_20,
    #         )

    #     points = []
    #     for i, score in enumerate(reversed(score_list)):
    #         x = padding + i * (width - 2 * padding) / (len(score_list) - 1)
    #         y = height - padding - (score - y_start) * scale
    #         points.append((x, y))

    #         draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill='blue')
    #         draw.text(
    #             (x - 15, y - 30), str(score), fill='white', font=csgo_font_20
    #         )

    #     draw.line(points, fill='yellow', width=3)
    #     img.paste(img_line, (0, 1900), img_line)

    # 五数据图
    selected_keys = [
        "awp_ratio",
        "end_ratio",
        "headshot_ratio",
        "kill_ratio",
        "mvp_ratio",
        "per_assist",
    ]
    if season_list['power']:
        filter_data = {key: season_list['power'][key] for key in selected_keys}
        selected_keys = {
            "awp_ratio": "枪法",
            "end_ratio": "致胜",
            "headshot_ratio": "突破",
            "kill_ratio": "狙杀",
            "mvp_ratio": "道具",
            "per_assist": "助攻",
        }
        filtered_data = {
            selected_keys[key]: filter_data[key] for key in selected_keys
        }
        width = 400
        height = 400
        # padding = 50
        center = (width // 2, height // 2)
        radius = 100  # 半径

        five_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(five_img)

        num_vars = len(filtered_data)
        angle = 2 * math.pi / num_vars
        points = []

        for i, (label, value) in enumerate(filtered_data.items()):
            x = center[0] + radius * (value / 10) * math.cos(
                i * angle - math.pi / 2
            )
            y = center[1] + radius * (value / 10) * math.sin(
                i * angle - math.pi / 2
            )
            points.append((x, y))

            draw.line([center, (x, y)], fill='black', width=2)

        template_points = []
        for i in range(num_vars):
            x = center[0] + radius * math.cos(i * angle - math.pi / 2)
            y = center[1] + radius * math.sin(i * angle - math.pi / 2)
            template_points.append((x, y))

        draw.polygon(
            template_points, fill=(200, 200, 200, 255), outline='black'
        )

        draw.polygon(points, fill=(135, 206, 250, 128), outline='blue')

        draw.line(points + [points[0]], fill='blue', width=2)

        for i, (label, value) in enumerate(filtered_data.items()):
            x = center[0] + (radius + 30) * math.cos(i * angle - math.pi / 2)
            y = center[1] + (radius + 30) * math.sin(i * angle - math.pi / 2)

            text = f"{value:.2f}\n{label}"

            text_size = draw.textbbox((0, 0), text, font=csgo_font_20)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]

            text_x = x - text_width / 2
            text_y = y - text_height / 2

            draw.text((text_x, text_y), text, fill='white', font=csgo_font_20)
        img.paste(five_img, (600, 1950), five_img)

    # 底
    img_up = Image.open(TEXTURE / "base" / "footer5e.png")
    img.paste(img_up, (0, 2340), img_up)

    return await convert_img(img)
