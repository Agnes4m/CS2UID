import sys
import json
from pathlib import Path
from typing import Dict, List

from gsuid_core.data_store import get_res_path
from gsuid_core.utils.download_resource.download_core import download_all_file

MAIN_PATH = get_res_path() / 'CS2UID'
sys.path.append(str(MAIN_PATH))
RESOURCE_PATH = MAIN_PATH / 'res'

with open(
    Path(__file__).parent / 'item.json', mode="r", encoding="utf-8"
) as fp:
    ITEM_DICT: Dict[str, Dict[str, List[str]]] = json.load(fp)
# 去除空值
ITEM_DICT = {k: v for k, v in ITEM_DICT.items() if v}

NEW_DICT = {
    f'res/{map_name}/{section}': RESOURCE_PATH / f'{map_name}/{section}'
    for map_name, sections in ITEM_DICT.items()
    for section, points in sections.items()
    if points  # 如果 points 非空（即它包含至少一个元素）
}


async def check_use():
    await download_all_file('CS2UID', NEW_DICT)
    return 'cs全部资源下载完成!'
