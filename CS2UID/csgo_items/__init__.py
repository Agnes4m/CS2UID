import json
from pathlib import Path
from typing import Dict, List, NamedTuple

from PIL import Image
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.server import on_core_start
from gsuid_core.utils.image.convert import text2pic, convert_img

from .message import map_dict, find_map_key
from .utils import black_match, res_img_path

res_img_path.parent.mkdir(parents=True, exist_ok=True)
config_item_path = res_img_path / "item.json"
root_path = res_img_path / "res"
download_url = "https://github.com/Agnes4m/CS2UID/releases"


class CSGOItem(NamedTuple):
    map_name: str
    team: str
    """t/ct"""
    from_position: str
    to_position: str
    item_type: str
    """烟/火/闪"""


@on_core_start
async def build_directory_index():
    """初始化道具索引"""
    index: Dict[str, Dict[str, List[str]]] = {}
    Path(res_img_path / "res").mkdir(parents=True, exist_ok=True)
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
                    )  # noqa: E501

    for first_level, second_levels in index.items():
        for second_level, prefixes in second_levels.items():
            index[first_level][second_level] = sorted(list(prefixes))

    with config_item_path.open('w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=4)
    logger.success("已生成道具索引")


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
    if not config_item_path.exists():
        await bot.send("没有资源捏，请使用【csgo下载全部资源】指令")
        return
    tag_list = texts.split()

    with config_item_path.open('r', encoding='utf-8') as f:
        data: Dict[str, Dict[str, List[str]]] = json.load(f)

    # 查询地图点位

    print("关键词", tag_list)
    map_all_list: List[str] = []
    if len(tag_list) == 0:

        for _, one_map in map_dict.items():
            map_all_list.append(one_map[0])
        msg = f"当前支持的地图有：\n{','.join(map_all_list)}\n请输入【csgo道具 + 地图】查询"
        await bot.send(await text2pic(msg), at_sender=True)
        return

    elif len(tag_list) == 1:
        map_name = await find_map_key(tag_list[0])
        if map_name in data:
            points = [
                point_folder.name
                for point_folder in (root_path / map_name).glob('*/')
                if point_folder.is_dir()
            ]
            msg = (
                f"当前地图{map_name}支持的点位有：\n"
                + ','.join(points)
                + "\n请输入【csgo道具 + 地图 + 点位】查询"
            )
            await bot.send(await text2pic(msg), at_sender=True)
            return
        else:
            await bot.send(
                f"地图不存在: {map_name},请输入【csgo道具】获取全部地图"
            )
            return

    elif len(tag_list) == 2:

        map_name = await find_map_key(tag_list[0])
        if (
            map_name not in data
        ):  # 如果没有找到匹配的地图，find_map_key 可能返回原始别名
            await bot.send("没有该地图，请使用指令【csgo道具】查询地图")
            return

        map_post = data[map_name]
        maybe_pos = []
        for point_case in [str.upper, str.lower]:
            point_name = point_case(tag_list[-1])

            # 匹配点位

            for i, one in map_post.items():
                if point_name == i:
                    maybe_pos = [point_name]
                    break
                if point_name in i:
                    maybe_pos.append(i)

            if not maybe_pos:
                await bot.send(
                    f"没有该点位，请使用指令【csgo道具 {map_name}】查询点位"
                )
                return

        pos_list = map_post[maybe_pos[0]]
        msg = (
            f"当前点位{map_name}{maybe_pos[0]}支持的点位有：\n"
            + ','.join(pos_list)
            + "\n请输入【csgo道具 + 地图 + 点位】查询"
        )
        await bot.send(await text2pic(msg))
        return

    # 具体查询
    elif len(tag_list) == 3:
        tag_list = [tag_list[0], tag_list[1], tag_list[1], tag_list[2]]

    if len(tag_list) != 4:
        await bot.send(
            "参数不正确，请输入【csgo道具 地图名 点位 目的点位 烟/火/闪】/n例如：沙2 匪口 b门 烟"
        )
        return

    if len(tag_list) == 4:
        img_out = await black_match(tag_list)
    if isinstance(img_out, Image.Image):
        await bot.send(await convert_img(img_out))
    elif isinstance(img_out, str):
        await bot.send(img_out)
    else:
        await bot.send("暂时还没有该攻略呢")
