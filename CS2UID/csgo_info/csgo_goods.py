from pathlib import Path
from typing import Union

from PIL import Image
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error
from .csgo_path import TEXTURE, ICON_PATH
from ..utils.api.models import OneGet, SteamGet, UserHomedetailData
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

    for index, one_get in enumerate(detail["previewItem"]):
        site_x, site_y = calculate_position(index)

        good_img = await create_good_image(one_get)

        tag_data = process_tags(one_get["decorationTags"])
        await update_tag_data_for_special_types(tag_data)

        quality_info = await update_quality_info(one_get, tag_data)
        good_img.paste(quality_info['img_qua'], (4, 6))

        name_out = one_get["name"].split("|")
        await paste_item_name(
            good_img, name_out, tag_data, one_get['description']
        )

        # Pasting price information
        await paste_price_info(good_img, one_get)

        if index % 10 == 0:
            logger.info(f"已读取{index}件物品")

        img.paste(good_img, (site_x, site_y), good_img)

    logger.info(f"{totalCount}件物品已读取完毕，准备输出")

    return await convert_img(await add_detail(img))


def calculate_position(index: int) -> tuple[int, int]:
    """计算物品的显示位置"""
    site_x = 70 + (index % 3) * 260
    site_y = 550 + (index // 3) * 200
    return site_x, site_y


async def create_good_image(one_get: OneGet) -> Image.Image:
    """创建物品的图像"""
    good_img = Image.open(ICON_PATH / "main1.png").resize((220, 180))
    good = await save_img(one_get['picUrl'], "good")
    good_logo = await resize_image_to_percentage(good, 12)
    good_img.paste(good_logo.resize((61, 46)), (130, 20), good_logo)
    return good_img


def process_tags(tags: list) -> dict:
    """处理物品标签"""
    tag_data = {}
    for item in tags:
        key = category_to_key.get(item["category"])
        if key:
            tag_data[key] = item["name"]
    return tag_data


async def update_tag_data_for_special_types(tag_data: dict) -> None:
    """更新标签数据以处理特殊类型"""
    special_types = ["音乐盒", "收藏品", "武器箱", "涂鸦"]
    if tag_data.get("类型") in special_types:
        tag_data.update({"武器": "", "收藏品": "", "外观": ""})


async def update_quality_info(one_get: OneGet, tag_data: dict) -> dict:
    """更新物品的品质信息"""
    qua_color, qua_text_replacement = quality_mapping.get(
        tag_data.get("品质", "_default"), quality_mapping["_default"]
    )
    if qua_text_replacement is not None:
        tag_data["品质"] = qua_text_replacement
    img_qua = Image.new("RGB", (5, 15), color=qua_color)
    return {'img_qua': img_qua, 'qua_color': qua_color}


async def paste_item_name(
    good_img: Image.Image, name_out: list, tag_data: dict, description: str
) -> None:
    """粘贴物品的名称和种类"""
    st = "ST™"
    if len(name_out) == 1:
        await simple_paste_img(good_img, name_out[0], (20, 25))
    else:
        msg1, msg2 = name_out[0].replace("（StatTrak™）", ""), name_out[-1]
        if tag_data["类型"] in ["音乐盒", "武器箱"]:
            msg1, msg2 = msg2, msg1

        await process_stat_trak(
            good_img, description, tag_data, msg1, msg2, st
        )


async def process_stat_trak(
    good_img: Image.Image,
    description: str,
    tag_data: dict,
    msg1: str,
    msg2: str,
    st: str,
) -> None:
    """处理StatTrak信息的粘贴"""
    deta = str(description)
    head_x = 12
    if tag_data['类别'] != "普通":
        await simple_paste_img(good_img, st, (10, 7), size=10, color="Purple")
        head_x += 25

    st_count = extract_stat_trak_count(deta, tag_data)
    if st_count:
        await simple_paste_img(
            good_img, f"{st_count}个", (33, 5), color="red", size=13
        )

    await simple_paste_img(
        good_img, msg1, (20, 60), color=tag_data.get('品质', "Purple")
    )
    await simple_paste_img(good_img, msg2, (20, 25), color="Purple")


async def extract_stat_trak_count(deta: str, tag_data: dict) -> str:
    """提取StatTrak数量"""
    if tag_data["类型"] == "音乐盒":
        st_nub = (
            deta.split("官方竞技MVP次数：")[-1]
            .strip()
            .split("</p >")[0]
            .strip()
        )
    else:
        st_nub = (
            deta.split("已认证杀敌数：")[-1].strip().split("</p >")[0].strip()
        )
    return st_nub


async def paste_price_info(good_img: Image.Image, one_get: OneGet) -> None:
    """粘贴价格信息"""
    await simple_paste_img(
        good_img,
        f"cn价格: {one_get['suggestPrice'] / 100}馒头",
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
