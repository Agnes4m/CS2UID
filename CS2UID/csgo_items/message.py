import re
from typing import List

map_list = {
    "dust2": [
        "沙2",
        "炙热沙城2",
    ],
    "inferno": ["小镇", "炼狱小镇"],
    "mirage": ["米垃圾"],
    "nuke": ["核子", "核子危机"],
    "overpass": ["op", "游乐园", "死亡游乐园"],
    "vertigo": ["大厦", "殒命大厦"],
    "ancient": ["遗迹", "远古遗迹"],
    "anubis": ["阿努比斯"],
}

tag_list_1 = [
    "A",
    "B",
]
tag_list_2 = ["大", "小", "1", "2", "门", "点", "包点", "死点", "狙位", "通"]

tag_list = [
    "匪口",
    "匪家",
    "警家",
    "警家L位",
    # 中路
    "中路",
    "中门",
    "中厅",
    "中路跳台",
    "中路石墙",
    "中路过点",
    # 常用位置
    "侧道",
    "拱门",
    "黄墙",
    "二楼阳台",
    "VIP",
    "一箱",
    "二箱",
    "三箱",
    # 以下可以带AB中路
    "沙袋",
    "油桶",
    "木桶",
    "大小坑",
    "大坑",
    "石板"
    # 沙2
    "xbox",
    "后花园",
    "蓝车",
    "假门",
    "沙地",
    "狗洞",
    "忍者位"
    # 小镇
    "香蕉道",
    "香蕉道石板",
    "棺材",
    "链接",
    "书房",
    "下水道",
    "花坛下",
    "马棚",
    "教堂"
    # 米垃圾
    "拱门内侧",
    "三明治",
    "A1台上",
    "匪跳",
    "超市",
    "超市窗户",
    "超市入口",
    "匪二楼",
    "B2窗户",
    "jungle",
]
items = [
    "烟",
    "隔断烟",
    "快烟",
    "火",
    "满烧火",
    "包点火",
    "闪",
    "瞬爆闪",
    "自助闪",
    "反清闪",
    "雷",
    "炸烟雷",
]


async def build_map_pattern():
    # 将所有地图的别名转义并合并成一个大的选择组
    escaped_aliases = [
        '(?:{})'.format(re.escape(alias))
        for aliases in map_list.values()
        for alias in aliases
    ]
    return re.compile(f'^({"|".join(escaped_aliases)})', re.IGNORECASE)


async def find_map_key(alias: str):
    if alias in map_list:
        return alias

    for key, aliases in map_list.items():
        if alias.lower() in [alias.lower() for alias in aliases]:
            return key

    return alias


async def find_possible_items(text):
    # 物品的匹配返回
    if "快烟" in text:
        return ["快烟"]

    possible_items: List[str] = []
    for item in items:
        if item == "快烟":
            continue
        if "烟" in item and "烟" in text:
            possible_items.append(item)
        elif "闪" in item and "闪" in text:
            possible_items.append(item)
        elif "火" in item and "火" in text:
            possible_items.append(item)
        elif "雷" in item and "雷" in text:
            possible_items.append(item)

    return list(set(possible_items))
