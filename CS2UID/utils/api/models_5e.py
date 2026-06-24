"""5E 平台 API 响应数据模型"""

from typing import TypedDict

__all__ = [
    "CareerData5",
    "ChartInfo5",
    "CollegeVerify5",
    "Elo5",
    "Highlight5",
    "HighlightMain5",
    "MapsData5",
    "MatchData",
    "MatchData5",
    "MatchDetail5",
    "MaxData5",
    "Power5",
    "QuickEntrance5",
    "SearchRequest5",
    "SeasonData5",
    "SeasonList5",
    "User5",
    "UserHomeDetail5",
    "UserSeason5",
    "WeaponsData5",
]


class SearchRequest5(TypedDict):
    uuid: str
    """uuid"""
    avatar_url: str
    """头像"""
    username: str
    """昵称"""
    gender: int
    """性别"""
    domain: str
    """域名"""


class CareerData5(TypedDict):
    """职业数据"""

    elo: str
    """elo最高分数"""
    level_id: str
    """等级id"""
    level_url: str
    """等级url"""
    match_time_total: str
    """游戏总时间"""
    match_total: str
    """游戏总次数"""
    match_type: str
    """游戏类型(9)"""
    per_win_match: str
    """胜率"""
    rating: str
    """评分"""


class Highlight5(TypedDict):
    """高光时刻"""

    code_url: str
    """代码url"""
    cover_url: str
    """封面url"""
    group1_all_score: str
    """第一组总分"""
    group2_all_score: str
    """第二组总分"""
    id: str
    """id"""
    is_win: str
    """是否胜利"""
    map: str
    """地图
    de_vertigo
    """
    match_code: str
    """匹配编号"""
    match_name: str
    """匹配名称(优先排位)"""
    match_type: str
    """匹配类型(9)"""
    round: str
    """回合"""
    start_time: str
    """开始时间(时间戳)"""
    status: str
    """状态(0:未开始,1:进行中,2:已结束)"""
    type: str
    """类型(sus_hl)"""
    type_name: str
    """类型名称(高光集锦)"""
    video_url: str
    """视频url"""
    weapon: str
    """武器
    4杀/5杀有，其他为空
    """


class HighlightMain5(TypedDict):
    """高光时刻总"""

    list: list[Highlight5]
    need_create_count: int
    """总数量"""


class MatchData5(TypedDict):
    """匹配数据"""

    ach_icon_list: list[str]
    """成就图标(四杀/MVP)"""
    assist: str
    """助攻数"""
    change_elo: int
    """变化elo"""
    death: str
    """死亡数"""
    end_time: str
    """结束时间(时间戳)"""
    game_type: str
    """游戏类型(npug_c)"""
    group1_all_score: str
    """第一组总分"""
    group2_all_score: str
    """第二组总分"""
    is_credit_match: int
    """是否是积分匹配(0)"""
    is_mvp: str
    """是否是mvp(0是否)"""
    is_win: str
    """是否胜利"""
    kill: str
    """击杀数"""
    level_color: str
    """等级颜色(#EE540E)"""
    level_name: str
    """等级名称(A+)"""
    map: str
    """地图代码(de_mirage)"""
    map_desc: str
    """地图中文名"""
    map_name: str
    """地图英文名(Mirage)"""
    match_flag: str
    """匹配标记(0)"""
    match_id: str
    """匹配id"""
    match_name: str
    """匹配名称(优先排位)"""
    match_type: str
    """匹配类型(9)"""
    multi_match: bool
    """是否组队"""
    origin_elo: int
    """原始elo"""
    placement: str
    """分数排名(1)"""
    prot_card: str
    """守护卡("")"""
    rating: str
    """评分"""
    round_total: str
    """回合总数"""
    rws: str
    """RWS"""
    season: str
    """游戏赛季(2024s5)"""
    start_time: str
    """开始时间(时间戳)"""
    sx_2024s1: bool
    """是否sx2024s1"""
    time_desc: str
    """日期描述(10-18)"""


class QuickEntrance5(TypedDict):
    """快速入口"""

    icon: str
    """图标"""
    jump_link: str
    """跳转链接(app内)"""
    render_type: str
    """入口类型"""
    title: str
    """类型中文"""


class Power5(TypedDict):
    """六边形图，总和为1"""

    awp_ratio: float
    """狙杀"""
    end_ratio: float
    """残局"""
    headshot_ratio: float
    """瞄准"""
    kill_ratio: float
    """突破"""
    mvp_ratio: float
    """mvp"""
    per_assist: float
    """辅助"""
    worst_desc: str
    """建议"""


class SeasonList5(TypedDict):
    """季况列表"""

    adr: str
    """ADR"""
    elo: str
    """elo"""
    level_bg_url: str
    """等级背景图"""
    level_id: int
    """等级"""
    level_name: str
    """等级名称(A+)"""
    level_url: str
    """等级url"""
    match_total: str
    """游戏总次数"""
    match_type: int
    """游戏类型(9)"""
    name: str
    """名称(优先排位)"""
    per_win_match: str
    """胜率"""
    power: Power5
    """个人数据"""
    rank: str
    """总排名"""
    rating: str
    """rating"""
    rws: str
    """RWS"""
    sort: int
    """不知道(3)"""
    style_type: int
    """样式类型(2)"""


class SeasonData5(TypedDict):
    """季况数据"""

    now_season: str
    """当前季况(2024 S5赛季)"""
    now_season_v1: str
    """当前季况(2024 S5)"""
    season_list: list[SeasonList5]
    """list两个，第一个优先，第二个对战"""


class CollegeVerify5(TypedDict):
    """学校验证"""

    college_name: str
    """学校名称"""
    icon: str
    """学校图标"""
    verify_status: str
    """验证状态(4)"""


class User5(TypedDict):
    """用户信息"""

    account_banned: str
    """是否被ban("")"""
    advanced_identity_desc: str
    """高级身份描述("")"""
    advanced_identity_status: str
    """高级身份状态(0)"""
    anchor_id: str
    """未知id(0)"""
    avatar_spam_status: int
    """头像封禁状态(0)"""
    avatar_url: str
    """头像url"""
    college_verify: CollegeVerify5
    credit2: str
    """积分2(100)"""
    credit5_status: int
    """积分5状态(1)"""
    credit_emoji_url: str
    """积分emoji图标"""
    credit_level: str
    """积分等级(2)"""
    credit_score: int
    """积分分数(100)"""
    domain: str
    """域名"""
    follow_status: int
    """关注状态(-1)"""
    icon_data: list[str]
    """plus图标数据"""
    is_vip: int
    """1是vip"""
    match_time_total: int
    """总匹配次数"""
    placement: int
    """未知(0)"""
    priority_status: str
    """未知(1)"""
    title_id: str
    """未知(0)"""
    title_name: str
    """未知("")"""
    title_url: str
    uid: str
    """未知("")"""
    username: str
    """昵称"""
    username_spam_status: int
    """昵称是否被封禁,0是未被封禁"""
    uuid: str
    """uuid"""
    vip_level: str
    """vip等级"""


class UserHomeDetail5(TypedDict):
    """5e个人信息"""

    career_data: CareerData5
    highlight_list: HighlightMain5
    match_data: list[MatchData5]
    person_comment_status: int
    """个人评论状态(1)"""
    quick_entrance: list[QuickEntrance5]
    """跳转链接相关"""
    season_data: SeasonData5
    user: User5


class Elo5(TypedDict):
    """赛季变化数据"""

    data: str
    "elo分数"
    time: str
    "时间月日"


class ChartInfo5(TypedDict):
    """赛季变化数据"""

    elo: list[Elo5]
    flags: list[str]
    "标记, rws,rating,elo"
    rating: list[Elo5]
    rws: list[Elo5]


class MapsData5(TypedDict):
    avg_kill: str
    "平均击杀数"
    icon: str
    """地图图标"""
    map: str
    """地图代码"""
    map_name: str
    """地图英文名"""
    match_total: str
    """匹配次数"""
    per_headshot: str
    """爆头率"""
    per_match_total: int
    """未知"""
    per_win: float
    """胜率"""
    rating: str
    """rating"""
    rws: str
    """rws"""
    url: str
    """地图背景图"""


class MatchData(TypedDict):
    """当前赛季数据"""

    draw: str
    """未知"""
    elo: str
    level_bg_url: str
    level_url: str
    loses: str
    """负场"""
    match_type: str
    pre_win_match: str
    """胜率"""
    rank: str
    """排名"""
    rating: str
    """评分"""
    rws: str
    """rws"""
    season: str
    """赛季"""
    sx_2024s1: bool
    win: str
    """胜场"""


class MatchDetail5(TypedDict):
    adr: str
    avg_adr: str
    avg_assist: str
    avg_death: str
    avg_impact: str
    """侵略性"""
    avg_kill: str
    """局均击杀"""
    avg_kpr: str
    """局均击杀"""
    avg_rating: str
    avg_rws: str
    avg_sur: str
    awp_kill: str
    """狙杀数"""
    end_1v1: str
    end_1v2: str
    end_1v3: str
    end_1v4: str
    end_1v5: str
    end_kill_toal: str
    first_kill: str
    impact: str
    kast: str
    kd: str
    kill_3: str
    kill_4: str
    kill_5: str
    kill_total: str
    kills: str
    kpr: str
    match_time_total: str
    """游戏时间"""
    match_total: str
    """匹配次数"""
    max_adr: str
    max_impact: str
    max_kpr: str
    max_rating: str
    max_rws: str
    max_sur: str
    mvp: str
    """mvp占比"""
    per_headshot: str
    """爆头率"""
    power: Power5
    rating: str
    rws: str
    sur: str


class MaxData5(TypedDict):
    """最佳数据"""

    adr: str
    adr_match_id: str
    awp_kill: str
    awp_kill_match_id: str
    first_kill: str
    first_kill_match_id: str
    kill: str
    kill_match_id: str
    per_headshot: str
    per_headshot_match_id: str
    rating: str
    rating_match_id: str


class WeaponsData5(TypedDict):
    """武器数据"""

    ave_per_kill: str
    """使用频率（0-1)"""
    avg_harm: str
    """场均伤害"""
    kill: str
    """总击杀"""
    per_headshot: str
    """爆头率"""
    per_kill: str
    """击杀率"""
    weapon_name: str
    """武器名称"""
    weapon_type: str
    """武器类型(步枪，手枪)"""
    weapons_url: str
    """武器图片"""


class UserSeason5(TypedDict):
    """用户赛季数据"""

    chart_info: ChartInfo5
    maps_data: list[MapsData5]
    match_data: MatchData
    match_detail: MatchDetail5
    max_data: MaxData5
    weapons_data: list[WeaponsData5]
