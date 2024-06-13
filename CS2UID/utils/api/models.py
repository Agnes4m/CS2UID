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
