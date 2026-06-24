# 先导入基础配置模型

# 设定一个配置文件（json）保存文件路径
from gsuid_core.data_store import get_res_path

# 然后添加到GsCore网页控制台中
from gsuid_core.utils.plugins_config.gs_config import StringConfig
from gsuid_core.utils.plugins_config.models import GSC

# 建立自己插件的CONFIG_DEFAULT
# 名字无所谓, 类型一定是Dict[str, GSC]，以下为示例，可以添加无数个配置
CONFIG_DEFAULT: dict[str, GSC] = {}

CONFIG_PATH = get_res_path("CS2UID") / "config.json"

# 分别传入 配置总名称（不要和其他插件重复），配置路径，以及配置模型
majs_config = StringConfig("CS2UID", CONFIG_PATH, CONFIG_DEFAULT)

# ---- 业务常量 ----
# 对局类型关键字 → 平台 tag
# 集中管理,新增/调整时只改这里。
# 平台对应 API 行为:
#   -1 全部, 41 pro, 12/0 天梯, 20 巅峰赛, 27 周末联赛, 14 自定义
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
