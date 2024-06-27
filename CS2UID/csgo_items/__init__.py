import re
from pathlib import Path
from typing import Dict, List, NamedTuple

from PIL import Image
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.data_store import get_res_path
from gsuid_core.utils.image.convert import convert_img

from .message import (
    map_list,
    tag_list,
    tag_list_1,
    tag_list_2,
    find_map_key,
    custom_sort_key,
    build_map_pattern,
    find_possible_items,
)

res_img_path = get_res_path("CS2UID")
res_img_path.parent.mkdir(parents=True, exist_ok=True)

download_url = "https://github.com/Agnes4m/CS2UID/releases"


class CSGOItem(NamedTuple):
    map_name: str
    team: str
    """t/ct"""
    from_position: str
    to_position: str
    item_type: str
    """烟/火/闪"""


csgo_download = SV('cs资源下载')


@csgo_download.on_command(('资源下载'), block=True)
async def csgo_download_all(bot: Bot, ev: Event): ...


csgo_item = SV('cs道具教学')


@csgo_item.on_command(('道具'), block=True)
async def csgo_item_all(bot: Bot, ev: Event):
    texts = ev.text.strip()
    # 判断点位格式
    # 通常： 地图 + 点位 + 目的点位 + 烟/火/瞬爆闪
    # 例如
    # 沙2 匪口 b门 烟
    # 沙2 A大 警家 烟
    tag_list = texts.split()
    print(tag_list)
    if len(tag_list) == 3:
        tag_list = [tag_list[0], tag_list[1], tag_list[1], tag_list[2]]

    if len(tag_list) != 4:
        await bot.send(
            "参数不正确，请输入【csgo道具 地图名 点位 目的点位 烟/火/闪】/n例如：沙2 匪口 b门 烟"
        )
        return
    # 地图
    tag_list[1] = tag_list[1].replace("a","A").replace("b","B")
    tag_list[2] = tag_list[2].replace("a","A").replace("b","B")
    tag_map = await find_map_key(tag_list[0])

    img_map_path = res_img_path / "res" / tag_map
    # 点位
    tag_pos_1 = ""
    for item in img_map_path.iterdir():
        if item.is_dir():
            if tag_list[1] in item.name:
                tag_pos_1 = item.name
                break
    if not tag_pos_1:
        return await bot.send("暂时还没有该点位道具呢")

    tag_pos_2_list: List[str] = []
    print(img_map_path / tag_pos_1)
    for item in Path(img_map_path / tag_pos_1).iterdir():
        if tag_list[2] == item.name:
            tag_pos_2_list = [item.name]
            break
        if tag_list[2] in item.name:
            tag_pos_2_list.append(item.name)
    print(tag_pos_2_list)
    if not tag_pos_2_list:
        return await bot.send("暂时还没有该目的点位道具呢")
    
    # 同目的点位多方式分类
    grouped_tags: Dict[str,List[str]] = {}  
    for tag in tag_pos_2_list:  
        prefix, _ = tag.split('_', 1) 
        if prefix not in grouped_tags:  
            grouped_tags[prefix] = []  
        grouped_tags[prefix].append(tag)  
    
    # 将字典的值（即分类后的列表）转换为列表的列表  
    grouped_lists = list(grouped_tags.values()) 
    
    # 道具
    item_list:List[List[str]] = []
    max_number = 0
    for i, one_group in enumerate(grouped_lists, start=1):
        tag_item_list: List[str] = []
        for one in one_group:
            if tag_list[3] in one:
                tag_item_list.append(one)
        print(tag_item_list)
        x = len(tag_item_list)
        if x <= 0:
            break
        if max_number < x:
            max_number = x
        tag_pos_2_list = sorted(tag_item_list, key=custom_sort_key)
        item_list.append(tag_pos_2_list)
        
    # 生成图片
    img_out = Image.new("RGB", (672*len(item_list), 375 * max_number))
    for i, one_list in enumerate(item_list):
        for index, one_path in enumerate(one_list):
            img_path = Path(
                res_img_path,
                "res",
                tag_map,
                tag_pos_1,
                one_path,
            )
            print(img_path)
            paste_img = Image.open(img_path).resize((672, 375))
            img_out.paste(paste_img, (i*672, index * 375))

    if img_path.exists():
        await bot.send(await convert_img(img_out))
    else:
        await bot.send("暂时还没有该攻略呢")


async def re_match(texts: str, bot: Bot):
    """正则匹配，目前有误,tag1+tag2无法正确读取
    目前暂时使用空格匹配"""
    map_pattern = await build_map_pattern()

    tag_pattern = re.compile(
        rf'^{("|".join(re.escape(tag) for tag in tag_list))}\b', re.IGNORECASE
    )
    pattern_list_1 = '|'.join(re.escape(tag) for tag in tag_list_1)
    pattern_list_2 = '|'.join(re.escape(tag) for tag in tag_list_2)

    # 构建匹配tag_list_1中的标签后跟tag_list_2中的标签的正则表达式，但不要求\b在tag_list_2后
    tag_pattern_combo = re.compile(
        rf'\b({pattern_list_1})({pattern_list_2})(?!\w)', re.IGNORECASE
    )

    map_match = map_pattern.match(texts)
    if map_match:
        map_name = None
        for k, v in map_list.items():
            if any(map_match.group().lower() in alias.lower() for alias in v):
                map_name = k
                break

        if map_name:
            # A大 警家 烟
            remaining_text = texts[map_match.end() :].strip()
            print("点位参数", remaining_text)

            single_matches = tag_pattern.findall(remaining_text)[:2]
            print(single_matches)

            remaining_text = remaining_text.replace(single_matches[0], "")
            print(remaining_text)
            if len(single_matches) < 2:
                positions = single_matches
                combo_matches = tag_pattern_combo.findall(remaining_text)
                print(combo_matches)
                if len(combo_matches) >= 1:
                    for i in range(2):
                        positions.append(combo_matches[i])
                        if len(positions) == 2:
                            break

            positions = [
                match.group() for match in tag_pattern.finditer(remaining_text)
            ][:2]
            print(positions)
            if len(positions) == 2:
                tag_set_1 = set(tag_list_1)
                tag_set_2 = set(tag_list_2)
                pos1, pos2 = positions
                is_match = (pos1 in tag_set_1 and pos2 in tag_set_2) or (
                    pos1 in tag_set_2 and pos2 in tag_set_1
                )

                if is_match:
                    # 查找pos2的结束位置并更新remaining_text
                    pos2_end = None
                    for match in tag_pattern.finditer(remaining_text):
                        if match.group() == pos2:
                            pos2_end = match.end()
                            break  # 找到了匹配的pos2，跳出循环

                    if pos2_end is not None:
                        # 更新remaining_text，去除两个位置后的部分
                        remaining_text = remaining_text[pos2_end:].strip()
                        items = await find_possible_items(remaining_text)

                        # 构造并检查文件路径
                        for item in items:
                            img_path = Path(
                                res_img_path,
                                "res",
                                map_name,
                                pos1,
                                f'{pos2}{item}.png',
                            )
                            if img_path.exists():
                                print(f"攻略路径{img_path}")
                                await bot.send(await convert_img(img_path))
                                return
                        await bot.send(
                            "参数不正确，没有正确的道具信息（烟火闪雷）"
                        )
            await bot.send("参数不正确,没有位置信息或者缺少（至少有两个位置）")
            return
        await bot.send("参数不正确,没有地图信息")
        return None
