from gsuid_core.data_store import get_res_path
from gsuid_core.utils.plugins_config.gs_config import StringConfig
from gsuid_core.utils.plugins_config.models import GSC

CONFIG_DEFAULT: dict[str, GSC] = {
    "EventPageSize": GSC(
        key="EventPageSize",
        name="赛事列表请求数量",
        description="cs赛事指令每次请求的赛事数量 (默认10)",
        default_value=10,
    ),
}

CONFIG_PATH = get_res_path("CS2UID") / "config.json"

majs_config = StringConfig("CS2UID", CONFIG_PATH, CONFIG_DEFAULT)

# 平台 tag: -1 全部, 41 pro, 12/0 天梯, 20 巅峰赛, 27 周末联赛, 14 自定义
DEFAULT_MATCH_TYPES: dict[str, int] = {
    "天梯": 12,
    "pro": 41,
    "巅峰": 20,
    "周末": 27,
    "自定义": 14,
}


def get_match_types() -> dict[str, int]:
    """返回当前生效的对局类型映射。

    后续如果接入 gsuid_core 配置系统,可在此处读取 majs_config 覆盖。
    当前直接返回默认值。
    """
    return dict(DEFAULT_MATCH_TYPES)
