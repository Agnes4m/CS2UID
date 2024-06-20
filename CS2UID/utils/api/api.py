HOST = 'https://pwaweblogin.wmpvp.com'
APIHOST = "https://api.wmpvp.com"
STEAMCNHOST = "https://gwapi.pwesports.cn"

UserInfoAPI = f"{HOST}/user-info"
UserSeasonScoreAPI = f'{HOST}/user-info/season-ladder-score-list'
DailyStatsAPI = f'{HOST}/user-info/daily-stats'


# post
UserDetailAPI = f'{APIHOST}/api/csgo/home/pvp/detailStats'
UserHomematchApi = f"{DailyStatsAPI}/api/csgo/home/match/list"
UserHomeApi = f"{APIHOST}/api/csgo/home/official/detailStats"

# get
u1 = "appdecoration/steamcn/csgo/decoration/getSteamInventoryPreview"
UserSteamPreview = f"{STEAMCNHOST}/{u1}"
CsgoFall = f"{STEAMCNHOST}/appdatacenter/csgo/official/fall/userCsgoInfo"
