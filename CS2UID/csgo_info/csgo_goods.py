from contextlib import suppress
from pathlib import Path

from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import draw_pic_with_ring, easy_paste

from ..utils.api.models import SteamGet, UserHomedetailData
from ..utils.csgo_api import api_5e, pf_api
from ..utils.csgo_font import csgo_font_20, csgo_font_30, csgo_font_42
from ..utils.error_reply import get_error
from .csgo_path import TEXTURE
from .utils import (
    batch_download_images,
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


async def get_csgo_goods_img(uid: str) -> str | bytes:
    detail = await pf_api.get_steamgoods(uid)
    base = await pf_api.get_csgohomedetail(uid)
    logger.debug(detail)

    if isinstance(detail, int):
        return get_error(detail)
    if isinstance(base, int):
        return get_error(base)
    if detail["result"] is None:
        return "该用户设置了steam隐私，无法查看"
    return await draw_csgo_goods_img(detail["result"], base["data"])


async def draw_csgo_goods_img(
    detail: SteamGet, base: UserHomedetailData
) -> bytes | str:
    """绘制PF库存图片。"""
    if not detail:
        return "token已过期"
    if not detail["previewItem"]:
        return "你的库存空空如也"

    totalCount = detail["totalCount"]
    totalPrice = detail["totalPrice"]
    name = base["nickName"]
    uid = base["steamId"]
    uid_masked = f"{uid[:4]}********{uid[12:]}"
    avatar = base["avatar"]
    items = detail["previewItem"]

    # 收集并下载图片
    url_list: list[tuple[str, str]] = [(avatar, "avatar")]
    for one_get in items:
        pic = one_get.get("picUrl") or one_get.get("pic_url") or ""
        if pic:
            url_list.append((pic, "good"))
    downloaded = await batch_download_images(url_list) if url_list else {}

    # 动态画布: 20px gap + 60px footer 紧贴底部
    max_items = min(len(items), 24)
    rows = (max_items + 2) // 3
    grid_y = 560
    footer_h = 60
    canvas_h = grid_y + rows * 200 + 20 + footer_h
    canvas_h = max(canvas_h, 900)

    # 背景
    img = Image.open(TEXTURE / "base" / "bg.jpg").resize((1000, canvas_h))
    img_bg = Image.open(TEXTURE / "bg" / "3.jpg").resize((1000, canvas_h))
    new_alpha = Image.new("L", img_bg.size, 128)
    img_bg_out = Image.merge("RGBA", img_bg.split()[:3] + (new_alpha,))
    img.paste(img_bg_out, (0, 0), img_bg_out)

    # 标题 (与 cs查询 一致)
    titel_img = Image.open(TEXTURE / "base" / "title_bg.png")
    head = downloaded.get(
        avatar, Image.new("RGBA", (200, 600), (0, 0, 0, 255))
    )
    round_head = await draw_pic_with_ring(head, 100)
    easy_paste(titel_img, round_head, (112, 108), "cc")
    head_draw = ImageDraw.Draw(titel_img)
    head_draw.text((250, 50), name, (255, 255, 255, 255), csgo_font_42)
    head_draw.text(
        (250, 100), f"ID: {uid_masked}", (255, 255, 255, 255), csgo_font_30
    )
    head_draw.line([(250, 150), (550, 150)], fill="white", width=2)
    img.paste(titel_img, (0, 55), titel_img)

    # banner
    banner = Image.open(TEXTURE / "base" / "banner.png")
    banner_draw = ImageDraw.Draw(banner)
    banner_draw.text((50, 10), "库存", (255, 255, 255, 255), csgo_font_42)
    img.paste(banner, (0, 340), banner)

    # 三个统计框 — 简洁半透明底
    box_w, box_h = 300, 90
    box_y = 420
    gap = (1000 - box_w * 3) // 4
    total_steam_val = sum(it.get("steamPrice", 0) or 0 for it in items) / 100
    for i, (label, value) in enumerate(
        [
            ("库存数量", str(totalCount)),
            ("完美价值", f"¥{totalPrice / 100:.1f}"),
            ("Steam价值", f"¥{total_steam_val:.1f}"),
        ]
    ):
        bx = gap + i * (box_w + gap)
        box = Image.new("RGBA", (box_w, box_h), (255, 255, 255, 20))
        box_draw = ImageDraw.Draw(box)
        box_draw.text(
            (box_w // 2, 28), label, (180, 180, 180, 255), csgo_font_20, "mm"
        )
        box_draw.text(
            (box_w // 2, 60), value, (255, 255, 255, 255), csgo_font_42, "mm"
        )
        img.paste(box, (bx, box_y), box)

    # 物品格子
    for idx in range(max_items):
        one_get = items[idx]
        x = 15 + (idx % 3) * 325
        y = grid_y + (idx // 3) * 200

        box = Image.open(TEXTURE / "base" / "weapon_bg.png").resize((310, 180))
        box_draw = ImageDraw.Draw(box)

        pic_url = one_get.get("picUrl") or one_get.get("pic_url") or ""
        if pic_url and pic_url in downloaded:
            good_img = await resize_image_to_percentage(
                downloaded[pic_url], 15
            )
            good_img = good_img.resize((70, 52))
            box.paste(good_img, (20, 30), good_img)

        tag_data = process_tags(one_get["decorationTags"])
        quality = tag_data.get("品质", "_default") or "_default"
        qua_color, _ = quality_mapping.get(
            quality, quality_mapping["_default"]
        )
        color_bar = Image.new("RGBA", (4, 16), qua_color)
        box.paste(color_bar, (16, 36))

        name_out = one_get["name"].split("|")
        if len(name_out) == 1:
            box_draw.text(
                (110, 40), name_out[0], (255, 255, 255, 255), csgo_font_20
            )
        else:
            box_draw.text(
                (110, 30),
                name_out[0].replace("（StatTrak™）", ""),
                (255, 255, 255, 255),
                csgo_font_20,
            )
            box_draw.text(
                (110, 55),
                name_out[-1].strip(),
                (200, 150, 255, 255),
                csgo_font_20,
            )

        wear = tag_data.get("外观", "")
        if wear:
            wear_color = wear_color_mapping.get(
                wear, wear_color_mapping["_default"]
            )
            box_draw.text((110, 85), wear, wear_color, csgo_font_20)

        box_draw.text(
            (110, 115),
            f"¥{one_get.get('suggestPrice', 0) / 100:.2f}",
            (255, 255, 255, 255),
            csgo_font_20,
        )
        sp = one_get.get("steamPrice", 0)
        if sp:
            box_draw.text(
                (200, 115),
                f"{one_get['suggestPrice'] / sp * 100:.1f}%",
                (180, 180, 180, 255),
                csgo_font_20,
            )

        img.paste(box, (x, y), box)

    # foot 贴底
    footer_y = canvas_h - footer_h
    img_up = Image.open(TEXTURE / "base" / "footer.png")
    img.paste(img_up, (0, footer_y), img_up)

    return await convert_img(img)


def process_tags(tags: list) -> dict:
    """处理物品标签"""
    tag_data = {}
    for item in tags:
        key = category_to_key.get(item["category"])
        if key:
            tag_data[key] = item["name"]
    return tag_data


async def get_csgo_goods_5e_img(domain: str) -> str | bytes:
    """获取5E平台库存信息并绘制图片。"""
    detail = await api_5e.get_user_detail(domain)
    if isinstance(detail, int):
        return get_error(detail)

    inventory = await api_5e.get_inventory(domain, limit=30)
    if isinstance(inventory, int):
        return get_error(inventory)

    inv_data = inventory.get("data", inventory)
    items = inv_data.get("list", inv_data.get("previewItem", []))
    total = inv_data.get("total", len(items))

    if not items:
        return f"5E库存为空 (用户: {detail.get('user', {}).get('username', domain)})"

    return await draw_csgo_goods_5e_img(detail, items, total)


async def draw_csgo_goods_5e_img(
    detail: dict, items: list, total: int
) -> bytes | str:
    """绘制5E库存图片。"""
    user_info = detail.get("user", {})
    username = user_info.get("username", "?")
    domain_val = user_info.get("domain", "?")
    avatar = user_info.get("avatar_url", "")

    # 收集并下载图片
    url_list: list[tuple[str, str]] = []
    if avatar:
        url_list.append((avatar, "avatar"))
    for item in items:
        pic = (
            item.get("picUrl")
            or item.get("pic_url")
            or item.get("image_url")
            or ""
        )
        if pic:
            url_list.append((pic, "good"))
    downloaded = await batch_download_images(url_list) if url_list else {}

    # 动态画布
    max_items = min(len(items), 24)
    rows = (max_items + 2) // 3
    grid_y = 560
    footer_h = 60
    canvas_h = grid_y + rows * 200 + 20 + footer_h
    canvas_h = max(canvas_h, 900)

    # 背景
    img = Image.open(TEXTURE / "base" / "bg.jpg").resize((1000, canvas_h))
    img_bg = Image.open(Path(TEXTURE / "bg" / "5.jpg")).resize(
        (1000, canvas_h)
    )
    new_alpha = Image.new("L", img_bg.size, 90)
    img_bg_out = Image.merge("RGBA", img_bg.split()[:3] + (new_alpha,))
    img.paste(img_bg_out, (0, 0), img_bg_out)

    # 标题 (与 cs查询5e 一致)
    titel_img = Image.open(TEXTURE / "base" / "title_bg.png")
    if avatar and avatar in downloaded:
        head_img = downloaded[avatar]
    else:
        head_img = Image.new("RGBA", (200, 200), (60, 60, 60, 255))
    round_head = await draw_pic_with_ring(head_img, 80)
    easy_paste(titel_img, round_head, (112, 108), "cc")
    head_draw = ImageDraw.Draw(titel_img)
    head_draw.text((250, 50), username, (255, 255, 255, 255), csgo_font_42)
    head_draw.text(
        (250, 100), f"id: {domain_val}", (255, 255, 255, 255), csgo_font_30
    )
    head_draw.line([(250, 150), (550, 150)], fill="white", width=2)
    img.paste(titel_img, (0, 55), titel_img)

    # banner
    banner = Image.open(TEXTURE / "base" / "banner.png")
    banner_draw = ImageDraw.Draw(banner)
    banner_draw.text((50, 10), "库存", (255, 255, 255, 255), csgo_font_42)
    img.paste(banner, (0, 340), banner)

    # 计算总价
    total_5e_price = 0.0
    total_steam_price = 0.0
    for it in items:
        p = (
            it.get("suggestPrice")
            or it.get("suggest_price")
            or it.get("price")
            or 0
        )
        sp = it.get("steamPrice") or it.get("steam_price") or 0
        with suppress(TypeError, ValueError):
            total_5e_price += float(p)
        with suppress(TypeError, ValueError):
            total_steam_price += float(sp)

    # 三个统计框 — 简洁半透明底
    box_w, box_h = 300, 90
    box_y = 420
    gap = (1000 - box_w * 3) // 4
    for i, (label, value) in enumerate(
        [
            ("库存数量", str(total)),
            ("5E 总价", f"¥{total_5e_price:.1f}" if total_5e_price else "--"),
            (
                "Steam总价",
                f"¥{total_steam_price:.1f}" if total_steam_price else "--",
            ),
        ]
    ):
        bx = gap + i * (box_w + gap)
        box = Image.new("RGBA", (box_w, box_h), (255, 255, 255, 20))
        box_draw = ImageDraw.Draw(box)
        box_draw.text(
            (box_w // 2, 28), label, (180, 180, 180, 255), csgo_font_20, "mm"
        )
        box_draw.text(
            (box_w // 2, 60), value, (255, 255, 255, 255), csgo_font_42, "mm"
        )
        img.paste(box, (bx, box_y), box)

    # 物品格子
    for idx in range(max_items):
        item = items[idx]
        x = 15 + (idx % 3) * 325
        y = grid_y + (idx // 3) * 200

        box = Image.open(TEXTURE / "base" / "weapon_5ebg.png").resize(
            (310, 180)
        )
        box_draw = ImageDraw.Draw(box)

        pic_url = (
            item.get("picUrl")
            or item.get("pic_url")
            or item.get("image_url")
            or ""
        )
        if pic_url and pic_url in downloaded:
            good_img = await resize_image_to_percentage(
                downloaded[pic_url], 15
            )
            good_img = good_img.resize((70, 52))
            box.paste(good_img, (20, 30), good_img)

        name = item.get(
            "name", item.get("marketName", item.get("market_name", "?"))
        )
        if "|" in name:
            parts = name.split("|")
            box_draw.text(
                (110, 30), parts[0].strip(), (255, 255, 255, 255), csgo_font_20
            )
            box_draw.text(
                (110, 55),
                parts[-1].strip(),
                (200, 150, 255, 255),
                csgo_font_20,
            )
        else:
            box_draw.text((110, 40), name, (255, 255, 255, 255), csgo_font_20)

        price = (
            item.get("suggestPrice")
            or item.get("suggest_price")
            or item.get("price")
            or 0
        )
        with suppress(TypeError, ValueError):
            box_draw.text(
                (110, 115),
                f"¥{float(price):.2f}",
                (255, 255, 255, 255),
                csgo_font_20,
            )

        steam_price = item.get("steamPrice") or item.get("steam_price") or 0
        with suppress(TypeError, ValueError):
            sp_f = float(steam_price)
            if sp_f:
                box_draw.text(
                    (200, 115),
                    f"¥{sp_f:.2f}",
                    (180, 180, 180, 255),
                    csgo_font_20,
                )

        img.paste(box, (x, y), box)

    # foot 贴底
    footer_y = canvas_h - footer_h
    img_up = Image.open(TEXTURE / "base" / "footer5e.png")
    img.paste(img_up, (0, footer_y), img_up)

    return await convert_img(img)
