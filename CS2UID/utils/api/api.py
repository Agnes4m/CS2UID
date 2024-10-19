HOST = 'https://pwaweblogin.wmpvp.com'
APIHOST = "https://api.wmpvp.com"
STEAMCNHOST = "https://gwapi.pwesports.cn"

UserInfoAPI = f"{HOST}/user-info"
UserSeasonScoreAPI = f'{HOST}/user-info/season-ladder-score-list'
DailyStatsAPI = f'{HOST}/user-info/daily-stats'


# post
UserDetailAPI = f'{APIHOST}/api/csgo/home/pvp/detailStats'
UserHomematchApi = f"{APIHOST}/api/csgo/home/match/list"
UserHomeApi = f"{APIHOST}/api/csgo/home/official/detailStats"
UserSearchApi = "https://appengine.wmpvp.com/steamcn/app/search/user"
MatchDetailAPI = f"{APIHOST}/api/v1/csgo/match"

# get
u1 = "appdecoration/steamcn/csgo/decoration/getSteamInventoryPreview"
UserSteamPreview = f"{STEAMCNHOST}/{u1}"
CsgoFall = f"{STEAMCNHOST}/appdatacenter/csgo/official/fall/userCsgoInfo"
MatchTitelAPI = f"{APIHOST}/api/v1/csgo/mvp/stats"
MatchAdvanceAPI = f"{APIHOST}/api/v1/csgo/mvp/advance"

# login
LoginAPI = "https://passport.pwesports.cn/account/login"

# 5e search
SearchAPI = "https://app.5eplay.com/api/csgo/data/search"
HomeDetailAPI = (
    "https://ya-api-app.5eplay.com/v0/mars/api/csgo/data/player_home"
)
HomePageAPI = (
    "https://ya-api-app.5eplay.com/v1/user/steam/inventory/homepage/record"
)
