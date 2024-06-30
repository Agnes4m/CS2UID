import re
import json
from pathlib import Path
from typing import Dict, List, Union

from PIL import Image
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.data_store import get_res_path
from gsuid_core.utils.image.convert import convert_img

from .message import (
    map_dict,
    tag_lists,
    tag_list_1,
    tag_list_2,
    find_map_key,
    custom_sort_key,
    build_map_pattern,
    find_possible_items,
)

res_img_path = get_res_path("CS2UID")
config_item_path = res_img_path / "item.json"


async def black_match(tag_list: List[str]) -> Union[str, Image.Image]:
    # 地图
    tag_list[1] = tag_list[1].replace("a", "A").replace("b", "B")
    tag_list[2] = tag_list[2].replace("a", "A").replace("b", "B")
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
        return "暂时还没有该点位道具呢"

    tag_pos_2_list: List[str] = []

    for item in Path(img_map_path / tag_pos_1).iterdir():
        if tag_list[2] == item.name:
            tag_pos_2_list = [item.name]
            break
        if tag_list[2] in item.name:
            tag_pos_2_list.append(item.name)
    print("待选图片", tag_pos_2_list)
    if not tag_pos_2_list:
        return "暂时还没有该目的点位道具呢"

    # 同目的点位多方式分类
    grouped_tags: Dict[str, List[str]] = {}
    for tag in tag_pos_2_list:
        prefix, _ = tag.split('_', 1)
        if prefix not in grouped_tags:
            grouped_tags[prefix] = []
        grouped_tags[prefix].append(tag)

    # 将字典的值（即分类后的列表）转换为列表的列表
    grouped_lists: List[List[str]] = list(grouped_tags.values())

    # 道具
    item_list: List[List[str]] = []
    max_number = 0
    filter_keyword = tag_list[3]

    for one_group in grouped_lists:

        if filter_keyword == "快烟":
            # 如果关键词是"快烟"，则保留含有"快烟"的项
            filtered_group = [one for one in one_group if "快烟" in one]
        else:
            # 如果关键词不是"快烟"，则排除含有"快烟"的项，同时保留包含filter_keyword的项
            filtered_group = [
                one
                for one in one_group
                if "快烟" not in one and filter_keyword in one
            ]

        print("fil", len(filtered_group))
        # 如果filtered_group非空，则添加到item_list中
        if filtered_group:
            filtered_group = sorted(filtered_group, key=custom_sort_key)
            item_list.append(filtered_group)

        if len(filtered_group) > max_number:
            max_number = len(filtered_group)

    print(item_list)
    # 生成图片
    img_out = Image.new("RGB", (672 * len(item_list), 375 * max_number))
    print(f"生成{len(item_list) + 1} * {(max_number + 1)}")
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
            if img_path.exists():
                paste_img = Image.open(img_path).resize((672, 375))

                img_out.paste(paste_img, (i * 672, index * 375))
    return img_out


async def re_match(texts: str, bot: Bot):
    """正则匹配，目前有误,tag1+tag2无法正确读取
    目前暂时使用空格匹配"""
    map_pattern = await build_map_pattern()

    tag_pattern = re.compile(
        rf'^{("|".join(re.escape(tag) for tag in tag_lists))}\b', re.IGNORECASE
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
        for k, v in map_dict.items():
            if any(map_match.group().lower() in alias.lower() for alias in v):
                map_name = k
                break

        if map_name:
            # A大 警家 烟
            remaining_text = texts[map_match.end() :].strip()  # noqa: E203
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


async def start_json():
    """初始化道具索引"""
    index: Dict[str, Dict[str, List[str]]] = {}

    for first_dir in Path(res_img_path / "res").iterdir():

        if not first_dir.is_dir():
            continue

        index[first_dir.name] = {}

        for second_dir in first_dir.iterdir():
            if not second_dir.is_dir():
                continue
            if not any(second_dir.glob('*')):
                continue
            index_set = set()

            for file in second_dir.glob('*'):
                if file.is_file():
                    prefix = (
                        file.name.split('_')[0]
                        if '_' in file.name
                        else file.name
                    )
                    index_set.add(prefix)
                if index_set:
                    index[first_dir.name][second_dir.name] = sorted(
                        list(index_set)
                    )

    for first_level, second_levels in index.items():
        for second_level, prefixes in second_levels.items():
            index[first_level][second_level] = sorted(list(prefixes))

    with config_item_path.open('w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=4)
    logger.success("已生成道具索引")
