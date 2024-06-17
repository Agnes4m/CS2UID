from typing import List, TypedDict


class UsrInfo(TypedDict):
    """个人信息"""

    uid: str
    steamAccountId: int
    zqId: str
    nickname: str
    """名字"""
    avatar: str
    """头像url"""
    lastLoginTime: str
    '''最后登录时间'''
    identity: int
    last_game_time: str
    is_green: int
    pwLevel: int
    '''完美平台等级'''
    pre_rank: bool
    score: int
    grade: int
    ladderGrade: str
    '''魔王C+'''


class UserInfo(TypedDict):
    code: int
    msg: str
    data: UsrInfo


class SeasonScore(TypedDict):
    score: int
    curr_s_stars: int
    match_count: int
    user_id: int
    season: str
    curr_s_level: int


class UserSeasonScore(TypedDict):
    code: int
    msg: str
    data: List[SeasonScore]


class UserDetailMap(TypedDict):
    map: str
    """地图英文名称"""
    mapImage: str
    """地图图片url"""
    mapLogo: str
    """地图logo url"""
    mapName: str
    """地图中文名称"""
    totalMatch: int
    """该地图总场次"""
    winCount: int
    """该地图胜场"""
    totalKill: int
    """该地图总击杀"""
    totalAdr: float
    """累计adr"""
    rank: None
    """排名(大概)"""
    ratingSum: float
    """胜方评分"""
    rwsSum: float
    """胜方RWS"""
    deathNum: int
    """该地图总死亡"""
    firstKillNum: int
    """该地图首杀数"""
    firstDeathNum: int
    """该地图首死数"""
    headshotKillNum: int
    """该地图爆头数"""
    matchMvpNum: int
    """该地图MVP数"""
    threeKillNum: int
    """该地图三杀数"""
    fourKillNum: int
    """该地图四杀数"""
    fiveKillNum: int
    """该地图五杀数"""
    v3Num: int
    """该地图1V3数"""
    v4Num: int
    """该地图1V4数"""
    v5Num: int
    """该地图1V5数"""
    scuffle: bool
    """是否是混战模式"""


class UserDetailhotWeapons(TypedDict):
    """主要武器数据"""

    weaponImage: str
    """武器图片url"""
    weaponName: str
    """武器名称"""
    weaponKill: int
    """武器击杀数"""
    weaponHeadShot: int
    """武器爆头数"""
    totalMatch: int


class UserDetailscoreList(TypedDict):
    """比赛记录"""

    matchId: str
    """比赛id"""
    score: int
    """赛后段位评分"""
    time: float
    """比赛时间戳"""
    stars: int
    slevel: int


class UserDetailhotWeapons2(TypedDict):
    name: str
    """武器英文名称"""
    image: str
    """武器图片url"""
    nameZh: str
    """武器中文名称"""
    matchNum: int
    """使用场次"""
    headshotSum: int
    """爆头数"""
    headshotRate: float
    """爆头率"""
    killNum: int
    """击杀数"""
    damageSum: int
    """伤害量"""
    avgDamage: float
    """平均伤害量"""
    firstShotHitCount: int
    """首发命中数"""
    firstShotShotCount: int
    """首发射击数"""
    firstShotAccuracy: float
    """首发命中率"""
    timeToKillCount: int
    """击杀时间"""
    timeToKillTotal: int
    """击杀总时间"""
    avgTimeToKill: int
    """平均击杀时间"""
    levelAvgTimeToKill: str
    """平均击杀时间评分"""
    levelAccuracy: str
    """命中率评分"""
    accuracyType: int
    """命中率类型"""
    levelAvgDamage: str
    """平均伤害评分"""
    levelHeadshotRate: str
    """爆头率评分"""
    levelAvgKillNum: str
    """平均击杀数评分"""
    sprayAccuracy: float
    """扫射精准度"""


class UserDetailData(TypedDict):
    steamId: str
    """64位steamid"""
    seasonId: str
    """赛季S16"""
    pvpRank: int
    avatar: str
    """头像url"""
    name: str
    """名字"""
    cnt: int
    """赛季场次"""
    kd: float
    """K/D"""
    winRate: float
    """胜率"""
    rating: float
    pwRating: float
    """完美平台Rating Pro"""
    hitRate: float
    commonRating: float
    kills: int
    """击杀数"""
    deaths: int
    """死亡数"""
    assists: int
    """助攻数"""
    mvpCount: int
    """MVP数"""
    gameScore: int
    rws: float
    """RWS胜利贡献"""
    adr: float
    """ADR平均回合伤害"""
    headShotRatio: float
    """爆头率"""
    entryKillRatio: float
    """首杀率"""
    k2: int
    """回合2杀数量"""
    k3: int
    """回合3杀数量"""
    k4: int
    """回合4杀数量"""
    k5: int
    """回合5杀数量"""
    multiKill: int
    """连杀数量"""
    vs1: int
    """残局1v1数量"""
    vs2: int
    """残局1v2数量"""
    vs3: int
    """残局1v3数量"""
    vs4: int
    """残局1v4数量"""
    vs5: int
    """残局1v5数量"""
    endingWin: int
    """残局胜利数量"""
    hotMaps: List[UserDetailMap]
    """常用地图战绩"""
    historyRatings: List[float]
    historyPwRatings: List[float]
    historyScores: List[int]
    historyRws: List[float]
    historyDates: List[str]
    """"2024-06-14 21:21:49"""
    titles: list
    shot: float
    victory: float
    breach: float
    snipe: float
    prop: float
    vs1WinRate: float
    summary: str
    hotWeapons: List[UserDetailhotWeapons]
    avgWe: float
    """WE 制胜评价"""
    pvpScore: int
    """天梯段位分"""
    stars: int
    """星级"""
    scoreList: List[UserDetailscoreList]
    weList: List[float]
    """we评分变化"""
    hotWeapons2: List[UserDetailhotWeapons2]
    """武器数据2"""


class UserDetailRequest(TypedDict):
    """detail返回数据"""

    statusCode: int
    errorMessage: str
    data: UserDetailData


class TagDecoration(TypedDict):
    """
    [
    {
    "name": "装备",
    "category": "Type",
    "internal_name": "CSGO_Type_Equipment",
    "category_name": "类型"
    },
    {
    "name": "宙斯 X27 电击枪",
    "category": "Weapon",
    "internal_name": "weapon_taser",
    "category_name": "武器"
    },
    {
    "name": "千瓦收藏品",
    "category": "ItemSet",
    "internal_name": "set_community_33",
    "category_name": "收藏品"
    },
    {
    "name": "StatTrak™",
    "category": "Quality",
    "internal_name": "strange",
    "category_name": "类别"
    },
    {
    "name": "保密",
    "category": "Rarity",
    "internal_name": "Rarity_Legendary_Weapon",
    "category_name": "品质"
    },
    {
    "name": "略有磨损",
    "category": "Exterior",
    "internal_name": "WearCategory1",
    "category_name": "外观"
    }
    ],
    """

    name: str
    """中文名"""
    category: str
    """英文名"""
    internal_name: str
    """英文属性"""
    category_name: str
    """中文属性"""


class OneGet(TypedDict):
    itemId: int
    """物品id"""
    goodsId: int
    """物品种类id"""
    name: str
    """物品名称"""
    marketName: str
    """物品市场名称"""
    picUrl: str
    """图片url"""
    steamPrice: int
    """物品steam价格100倍"""
    suggestPrice: int
    """物品buff价格100倍"""
    description: str
    """物品描述"""
    decorationTags: List[TagDecoration]


class SteamGet(TypedDict):
    totalCount: int
    """物品数量"""
    totalPrice: int
    """总物品steam价格100倍"""
    previewItem: List[OneGet]


class SteamGetRequest(TypedDict):
    """steamcn库存返回数据"""

    code: int
    message: str
    result: SteamGet
