from pathlib import Path
from typing import Dict, Union

from PIL import Image
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error
from .csgo_path import TEXTURE, ICON_PATH
from ..utils.api.models import SteamGet, UserHomedetailData
from .utils import (
    save_img,
    add_detail,
    make_head_img,
    load_groudback,
    simple_paste_img,
    resize_image_to_percentage,
)

quality_mapping = {
    "高级": ("blue", None),
    "奇异": ("hotpink", None),
    "卓越": ("purple", None),
    "非凡": ("hotpink", "☆"),
    "工业级": ("royalblue", ""),
    "军规级": ("MediumBlue", ""),
    "受限": ("mediumorchid", ""),
    "保密": ("fuchsia", ""),
    "隐秘": ("red", ""),
    "违禁": ("yellow", ""),
    "_default": ("black", None),
}

wear_color_mapping = {
    "崭新出厂": "DarkGreen",
    "略有磨损": "green",
    "久经沙场": "Olive",
    "破损不堪": "Red",
    "战痕累累": "FireBrick",
    "_default": "black",
}

category_to_key = {
    "Type": "类型",
    "Quality": "类别",
    "Rarity": "品质",
    "Weapon": "武器",
    "ItemSet": "收藏品",
    "Exterior": "外观",
}


async def get_csgo_goods_img(uid: str) -> Union[str, bytes]:
    detail = await pf_api.get_steamgoods(uid)
    base = await pf_api.get_csgohomedetail(uid)
    logger.debug(detail)

    if isinstance(detail, int):
        return get_error(detail)
    if isinstance(base, int):
        return get_error(base)
    if detail['result'] is None:
        return "该用户设置了steam隐私，无法查看"
    # try:
    return await draw_csgo_goods_img(detail['result'], base['data'])
    # except Exception as e:
    #     logger.error(e)
    #     return "出现意外错误，请重启core正常使用该功能"


async def draw_csgo_goods_img(
    detail: SteamGet, base: UserHomedetailData
) -> bytes | str:
    if not detail:
        return "token已过期"
    if not detail["previewItem"]:
        return "你的库存空空如也"
    totalCount = detail["totalCount"]
    totalPrice = detail["totalPrice"]
    name = base["nickName"]
    uid = base["steamId"]
    uid = uid[:4] + "********" + uid[12:]
    avatar = base["avatar"]

    # 背景图
    img = await load_groudback(Path(TEXTURE / "bg" / "3.jpg"))

    # 头像
    head_img = await make_head_img(f"uid：  {uid}", f"昵称：  {name}", avatar)

    img.paste(head_img, (0, 0), head_img)

    # 主信息
    level_img = Image.open(ICON_PATH / "main1.png").resize((700, 220))
    await simple_paste_img(level_img, "steam库存信息", (100, 30), 40)
    await simple_paste_img(
        level_img, f"总物品数量：{totalCount}", (100, 90), 40
    )
    await simple_paste_img(
        level_img, f"总物品价值：{totalPrice/100}馒头", (100, 150), 40
    )

    img.paste(level_img, (100, 300), level_img)

    for index, one_get in enumerate(detail["previewItem"], start=0):
        site_x = 70
        site_y = 550

        row = index // 3  # 当前行数
        col = index % 3  # 当前列数

        site_x += 260 * col
        site_y += 200 * row

        good_img = Image.open(ICON_PATH / "main1.png").resize((220, 180))

        # 物品图标
        good = await save_img(one_get['picUrl'], "good")
        good_logo = await resize_image_to_percentage(good, 12)

        good_logo = good_logo.resize((61, 46))
        # weap_out = await draw_pic_with_ring(weap_out, 5)
        good_img.paste(good_logo, (130, 20), good_logo)

        tag = one_get["decorationTags"]
        tag_data: Dict[str, str] = {}
        special_types = ["音乐盒", "收藏品", "武器箱", "涂鸦"]

        # 遍历标签
        for item in tag:
            key = category_to_key.get(item["category"])
            if key:
                tag_data[key] = item["name"]

            if tag_data.get("类型") in special_types:
                tag_data["武器"] = ""
                tag_data["收藏品"] = ""
                tag_data["外观"] = ""

        if tag_data.get("类型") in special_types:
            tag_data["武器"] = ""
            tag_data["收藏品"] = ""
            tag_data["外观"] = ""

        # 品质
        name_out = one_get["name"].split("|")
        qua_color, qua_text_replacement = quality_mapping.get(
            tag_data["品质"], quality_mapping["_default"]
        )
        if qua_text_replacement is not None:
            tag_data["品质"] = qua_text_replacement
        img_qua = Image.new("RGB", (5, 15), color=qua_color)
        good_img.paste(img_qua, (4, 6))

        # 名称+种类
        st = "ST™"
        if len(name_out) == 1:
            await simple_paste_img(good_img, name_out[0], (20, 25))
        else:
            msg1 = name_out[0].replace("（StatTrak™）", "")
            msg2 = name_out[-1]
            if tag_data["类型"] in ["音乐盒", "武器箱"]:
                msg1, msg2 = msg2, msg1

            deta = str(one_get['description'])
            head_x = 12
            if tag_data['类别'] == "StatTrak™":
                if "该物品记录已认证杀敌数" in deta:
                    pass
                elif tag_data["类型"] == "音乐盒":
                    st_nub2 = deta.split("官方竞技MVP次数：")
                    st_nub3 = st_nub2[-1]
                    st_nub1 = st_nub3.strip().split("</p >")[0].strip()
                    await simple_paste_img(
                        good_img, f"{st_nub1}个", (33, 5), color="red", size=13
                    )
                    head_x += len(st_nub1 * 14)
                else:
                    st_nub2 = deta.split("已认证杀敌数：")
                    st_nub3 = st_nub2[-1]
                    st_nub1 = st_nub3.strip().split("</p >")[0].strip()
                    await simple_paste_img(
                        good_img, f"{st_nub1}个", (33, 5), color="red", size=13
                    )
                    head_x += len(st_nub1 * 13)
            await simple_paste_img(
                good_img,
                msg1,
                (20, 60),
                color=qua_color,
            )
            await simple_paste_img(good_img, msg2, (20, 25), color="Purple")

        # st + 磨损

        if tag_data["类型"] in ["音乐盒", "收藏品", "武器箱", "涂鸦"]:
            pass
        else:
            if tag_data['类别'] != "普通":
                await simple_paste_img(
                    good_img, st, (10, 7), size=10, color="Purple"
                )
                head_x += 25

            mosun = tag_data.get('外观', "_default")
            mo_color = wear_color_mapping.get(
                mosun, wear_color_mapping["_default"]
            )

            try:
                await simple_paste_img(
                    good_img, mosun, (head_x, 6), size=13, color=mo_color
                )
            except Exception as e:
                logger.error(f"Error pasting wear condition: {e}")

        # 价格
        await simple_paste_img(
            good_img,
            f"cn价格: {one_get['suggestPrice']/100}馒头",
            (20, 110),
        )
        if one_get['steamPrice'] == 0:
            await simple_paste_img(good_img, "steam比例: 无", (20, 140))
        else:
            bili = one_get['suggestPrice'] / one_get['steamPrice'] * 100
            await simple_paste_img(
                good_img,
                f"steam比例: {bili:.2f}%",
                (20, 140),
            )

        # 其他
        if index % 10 == 0:
            logger.info(f"已读取{index}件物品")

        img.paste(good_img, (site_x, site_y), good_img)
    logger.info(f"{totalCount}件物品已读取完毕，准备输出")

    return await convert_img(await add_detail(img))
