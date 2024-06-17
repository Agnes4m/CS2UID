HOST = 'https://pwaweblogin.wmpvp.com'
APIHOST = "https://api.wmpvp.com"
STEAMCNHOST = "https://gwapi.pwesports.cn"

UserInfoAPI = f"{HOST}/user-info"
UserSeasonScoreAPI = f'{HOST}/user-info/season-ladder-score-list'
DailyStatsAPI = f'{HOST}/user-info/daily-stats'


# post
UserDetailAPI = f'{APIHOST}/api/csgo/home/pvp/detailStats'


# get
u1 = "appdecoration/steamcn/csgo/decoration/getSteamInventoryPreview"
UserSteamPreview = f"{STEAMCNHOST}/{u1}"
