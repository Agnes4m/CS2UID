from typing import List, Optional, TypedDict


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
    """最后登录时间"""
    identity: int
    last_game_time: str
    is_green: int
    pwLevel: int
    """完美平台等级"""
    pre_rank: bool
    score: int
    grade: int
    ladderGrade: str
    """魔王C+"""


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
    """评分"""
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
    """1v1胜率"""
    summary: str
    """评价文字"""
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

    statusCode: str
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


class UserHomeMatch(TypedDict):
    matchId: str
    playerId: str
    honor: str
    k4: int
    k5: int
    matchScore: float
    mapUrl: str
    """地图url"""
    mapLogo: str
    """地图logo url"""
    mapName: str
    """地图中文名"""
    team: int
    """1,2表示队伍"""
    winTeam: int
    score1: int
    score2: int
    rating: float
    startTime: str
    """2024-06-13 21:10:39"""
    endTime: str
    timeStamp: int
    pageTimeStamp: int
    kill: int
    """击杀数"""
    death: int
    """死亡数"""
    assist: int
    """助攻数"""
    duration: int
    dataSource: int
    mode: str
    """游戏模式 国服竞技"""
    mvp: bool
    """是否是MVP"""


class UserHomematchData(TypedDict):
    dataPublic: bool
    matchList: List[UserHomeMatch]


class UserHomeRequest(TypedDict):
    statusCode: int
    errorMessage: str
    data: UserHomematchData


class UserhomeMap(TypedDict):
    map: str
    """地图英文名"""
    mapImage: str
    """地图url"""
    mapLogo: str
    """地图logo url"""
    mapName: str
    """地图中文名"""
    totalMatch: int
    """场次"""
    winCount: int
    """胜场"""
    totalKill: int
    """击杀"""
    totalAdr: float
    """adr总和"""
    rank: int
    """等级，0为无段位"""
    ratingSum: float
    """ration总和"""
    rwsSum: float
    """rws总和"""
    deathNum: int
    """死亡"""
    firstKillNum: int
    """首杀"""
    firstDeathNum: int
    """首死"""
    headshotKillNum: int
    """爆头"""
    matchMvpNum: int
    """mvp次数"""
    threeKillNum: int
    """三杀数"""
    fourKillNum: int
    """四杀数"""
    fiveKillNum: int
    """五杀数"""
    v3Num: int
    """1v3残局"""
    v4Num: int
    """1v4残局"""
    v5Num: int
    """1v5残局"""


class UserhomeWeapon(TypedDict):
    weaponImage: str
    """图片url"""
    weaponName: str
    """名称"""
    weaponKill: int
    """击杀"""
    weaponHeadShot: int
    """爆头"""
    totalMatch: int
    """击杀场次"""


class UserHomedetailData(TypedDict):
    steamId: str
    historyWinCount: int
    """胜场"""
    cnt: int
    """总场次"""
    kd: float
    """kd"""
    winRate: float
    """胜方Rate"""
    rating: float
    kills: int
    """击杀数"""
    deaths: int
    """死亡数"""
    assists: int
    """助攻数"""
    rws: float
    adr: float
    kast: int
    endingWin: int
    """残局胜场"""
    k3: int
    """回合3杀"""
    k4: int
    """回合4杀"""
    k5: int
    """回合5杀"""
    vs3: int
    vs4: int
    vs5: int
    multiKill: int
    headShotRatio: float
    """爆头率"""
    entryKillRatio: float
    """首杀率"""
    awpKillRatio: float
    """狙首杀率"""
    flashSuccessRatio: float
    """闪白率"""
    hotMaps: List[UserhomeMap]
    hotWeapons: List[UserhomeWeapon]
    historyRatings: List[float]
    historyRanks: List[int]
    historyComprehensiveScores: list
    historyRws: List[float]
    historyDates: List[str]
    """2024-06-13 21:10:39"""
    refreshed: bool
    entryKillAvg: float
    matchList: list
    nickName: str
    """姓名"""
    avatar: str
    """头像url"""
    friendCode: str
    """好友码"""
    hours: int
    """游戏时间"""
    rank: int
    """- 1-6 白银 Silver
    - 7-10 黄金 Gold Nova
    - 11 ak Master Guardian I
    - 12 麦穗ak  Master Guardian II
    - 13 双ak Master Guardian Elite
    - 14 菊花 Distinguished Master Guardian
    - 15 老鹰 Legendary Eagle
    - 16 大老鹰 Legendary Eagle Master
    - 17 小地球 Supreme Master First Class
    - 18 大地球 The Global Elite"""
    authStats: int


class UserHomedetailRequest(TypedDict):
    statusCode: int
    errorMessage: str
    data: UserHomedetailData


class UserFall(TypedDict):
    """官匹箱子刷新"""

    curLevel: int
    """当前等级"""
    levelUpProgress: int
    """当前经验百分比"""
    refreshTimePoint: int
    """刷新时间"""
    statusDesc: str
    """掉落说明中文"""
    levelTitle: str
    """军衔中文"""
    levelIcon: str
    """图片url"""


class UserFallRequest(TypedDict):
    code: int
    message: str
    result: UserFall


class Match(TypedDict):
    matchId: str
    """完美匹配id"""
    playerId: str
    """玩家id"""
    honor: Optional[str]
    k4: int
    k5: int
    matchScore: int
    mapUrl: str
    mapLogo: str
    mapName: str
    """地图中文名"""
    steamName: Optional[str]
    steamAvatar: Optional[str]
    team: int
    winTeam: int
    score1: int
    score2: int
    rating: float
    pwRating: float
    startTime: str
    """2024-06-13 21:10:39"""
    endTime: str
    timeStamp: int
    pageTimeStamp: int
    kill: int
    death: int
    assist: int
    duration: int
    """游戏分钟"""
    dataSource: int
    """3是完美平台，1是国服官匹"""
    mode: str
    """天梯普通对局"""
    pvpMvp: bool
    """是否是MVP"""
    greenMatch: bool
    pvpScore: int
    """匹配结束分数"""
    pvpScoreChange: int
    """分数变化"""
    pvpScoreChangeType: int
    """未知，0"""
    pvpStars: int
    """星级"""
    group: bool
    """是否组队"""
    rank: int
    oldrank: int
    pvpGrading: int
    we: float
    """we评分"""
    status: int


class UserMatch(TypedDict):
    dataPublic: bool
    matchList: List[Match]


class UserMatchRequest(TypedDict):
    statusCode: int
    errorMessage: str
    data: UserMatch


class UserSearch(TypedDict):
    steamId: str
    """64位steamid"""
    pvpNickName: str
    """完美名称"""
    pvpAvatar: str
    """头像"""
    steamNickName: str
    """null"""
    steamAvatar: str
    """null"""
    appNickName: str
    """手机端名称"""
    userId: int
    ladderType: int


class UserSearchRequest(TypedDict):
    code: int
    message: str
    result: List[UserSearch]


class MatchTitelSats(TypedDict):
    statsDesc: str
    """统计描述"""
    dataDesc: str
    """数据描述"""
    type: int
    """描述类型
    1:好兄弟
    2:铁哥们
    11:输出机器
    """


class MatchTitel(TypedDict):
    steamid: str
    """MVP的steamid"""
    greenType: int
    """是否是绿色"""
    nickName: str
    """MVP的昵称"""
    avatar: str
    """MVP的头像"""
    kill: int
    """击杀数"""
    death: int
    """死亡数"""
    weSeason: bool
    """是否是天梯"""
    isVip: bool
    """是否是vip"""
    avatarFrame: str
    """头像框，空是null"""
    rating: float
    """评分"""
    pwRating: float
    """完美平台评分"""
    adpr: float
    """平均伤害"""
    rws: float
    """RWS"""
    we: float
    """WE评分"""
    pvpScore: int
    """对局分段"""
    map: str
    """地图名称"""
    mapZh: str
    """地图中文名称"""
    mapUrl: str
    """地图url"""
    mapLogo: str
    """地图logo url"""
    startTime: str
    """开始时间"""
    endTime: str
    """结束时间"""
    duration: int
    """游戏时间,单位分钟"""
    mode: str
    """模式：天梯普通对局"""
    gameMode: int
    """1"""
    mvpCnt: int
    """mvp数量"""
    statsDesc: str
    """统计描述"""
    dataDesc: str
    """数据描述"""
    type: int
    """描述类型"""


class MatchPlayer(TypedDict):
    playerId: str
    """玩家id"""
    highlightsData: str
    """未知，我的数据是null"""
    nickName: str
    """玩家昵称"""
    avatar: str
    """玩家头像"""
    vac: bool
    """是否被vac封禁"""
    team: int
    """队伍,1或者2"""
    kill: int
    """击杀数"""
    botKill: int
    """机器人击杀数"""
    negKill: int
    """击杀数"""
    entryKill: int
    """首杀数"""
    death: int
    """死亡数"""
    entryDeath: int
    """首死数"""
    assist: int
    """助攻数"""
    headShot: int
    """爆头数"""
    headShotRatio: float
    """爆头率"""
    rating: float
    """评分"""
    pwRating: float
    """完美平台评分"""
    damage: int
    itemThrow: int
    flash: int
    flashTeammate: int
    """闪白队友数"""
    flashSuccess: int
    """闪白数"""
    endGame: int
    mvpValue: int
    """mvp回合数"""
    score: int
    userForbidDTO: str
    """null"""
    banType: int
    """未知，我的数据是0"""
    twoKill: int
    """回合2杀数量"""
    threeKill: int
    """回合3杀数量"""
    fourKill: int
    """回合4杀数量"""
    fiveKill: int
    """回合5杀数量"""
    multiKills: int
    """残局连杀数量"""
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
    headShotCount: int
    """爆头数"""
    dmgArmor: int
    """甲伤"""
    dmgHealth: int
    """血伤"""
    adpr: int
    """平均回合伤害"""
    fireCount: int
    """可能是火伤"""
    hitCount: int
    """可能射击命中次数"""
    rws: float
    """RWS胜利贡献"""
    pvpTeam: int
    """完美平台队伍id"""
    honor: str
    """未知，我的数据是1,4,2"""
    pvpScore: int
    """完美平台段位分"""
    pvpScoreChange: int
    """完美平台段位分变化"""
    matchScore: float
    """0.0"""
    we: float
    """we评分"""
    weapons: str
    """null"""
    throwsCnt: int
    """投掷数"""
    isVip: bool
    """是否是vip"""
    avatarFrame: str
    """头像框，空是null"""
    teamId: int
    """队伍id"""
    pvpNormalRank: str
    snipeNum: int
    """狙杀数"""
    firstDeath: int
    """首死数"""
    mvp: bool
    """是否是mvp"""


class MatchDetail(TypedDict):
    matchId: str
    """完美匹配id"""
    map: str
    """地图名称"""
    mapEn: str
    """地图英文名称"""
    mapUrl: str
    """地图url"""
    matchType: str
    """不知道是啥，反正我这是null"""
    mapLogo: str
    """地图logo url"""
    startTime: str
    """开始时间"""
    endTime: str
    """结束时间"""
    duration: int
    """游戏时间,单位分钟"""
    winTeam: int
    """胜利队伍"""
    score1: int
    """胜利队伍1回合"""
    score2: int
    """胜利队伍2回合"""
    halfScore1: int
    """半场队伍1胜利回合"""
    halfScore2: int
    """半场队伍2胜利回合"""
    extraScore1: int
    """加时赛队伍1胜利回合"""
    extraScore2: int
    """加时赛队伍2胜利回合"""
    team1PvpId: int
    """队伍1完美平台id"""
    team2PvpId: int
    """队伍2完美平台id"""
    pvpLadder: bool
    """是否是完美平台天梯"""
    halfCamp1: int
    """未知，我的数据是3"""
    greenMatch: bool
    """是否是绿色对局"""


class MatchTotal(TypedDict):
    base: MatchDetail
    players: List[MatchPlayer]


class MatchAdvance(TypedDict):
    """其他数据"""

    steamId: str
    """64位steamid"""
    hitRate: float
    """扫射率"""
    scramRate: float
    """急停率"""
    tradeRate: float
    """拉枪率"""
    tradeFragRate: float
    """补枪率"""


class AccountInfo(TypedDict):
    """账号信息"""

    userId: int
    """账号id"""
    steamId: int
    """steam64位Id"""
    mobilePhone: str
    """手机号"""
    token: str
    """token"""
    create: int


class Logininfo(TypedDict):
    userType: int
    """用户类型，1为手机号登录"""
    accountInfo: AccountInfo


class LoginResult(TypedDict):
    """登录结果"""

    loginResult: Logininfo


class LoginDetail(TypedDict):
    """登录返回信息"""

    code: int
    """- 0:成功
    - 20001: 验证码错误
    - 1015: 手机号错误
    - 90001: 服务器繁忙"""
    description: str
    """成功位`Success`，失败则输出报错信息"""
    result: LoginResult
    """登录结果"""


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

    list: List[Highlight5]
    need_create_count: int
    """总数量"""


class MatchData5(TypedDict):
    """匹配数据"""

    ach_icon_list: List[str]
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
    season_list: List[SeasonList5]
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
    icon_data: List[str]
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
    match_data: List[MatchData5]
    person_comment_status: int
    """个人评论状态(1)"""
    quick_entrance: List[QuickEntrance5]
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

    elo: List[Elo5]
    flags: List[str]
    "标记, rws,rating,elo"
    rating: List[Elo5]
    rws: List[Elo5]


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
    maps_data: List[MapsData5]
    match_data: MatchData
    match_detail: MatchDetail5
    max_data: MaxData5
    weapons_data: List[WeaponsData5]
