"""error_reply.py 单元测试。"""

import pytest

from CS2UID.utils.error_reply import (
    CK_HINT,
    SK_HINT,
    UID_HINT,
    error_dict,
    get_error,
    not_msg,
    not_player,
    try_send,
)


def test_uid_hint():
    assert "绑定" in UID_HINT


def test_ck_hint():
    assert "TK" in CK_HINT.upper() or "添加tk" in CK_HINT


def test_sk_hint():
    assert "SK" in SK_HINT.upper() or "添加sk" in SK_HINT


def test_get_error_known_code():
    assert get_error(-51) == UID_HINT
    assert get_error(-511) == CK_HINT
    assert get_error(4001) == "4001 - 登录已失效，请重新添加sk"
    assert (
        get_error(8000102)
        == "8000102 - auth check failed!\n该tk失效或不正确, 请检查错误tk!"
    )


def test_get_error_unknown_code():
    msg = get_error(99999)
    assert "99999" in msg
    assert "未知错误" in msg


def test_get_error_accepts_string():
    """部分上游会传字符串错误码。"""
    msg = get_error("404")
    assert "404" in msg


def test_not_msg_and_not_player():
    assert isinstance(not_msg, str) and not_msg
    assert isinstance(not_player, str) and not_player


def test_error_dict_codes_match_documented():
    for code in (-51, -511, 4001, 8000102, 500, 1):
        assert code in error_dict


@pytest.mark.asyncio
async def test_try_send_passes_through():
    class FakeBot:
        def __init__(self):
            self.sent = []

        async def send(self, msg):
            self.sent.append(msg)

    bot = FakeBot()
    await try_send(bot, "hello")
    assert bot.sent == ["hello"]


@pytest.mark.asyncio
async def test_try_send_swallows_exception():
    class FailingBot:
        async def send(self, msg):
            raise RuntimeError("network down")

    bot = FailingBot()
    await try_send(bot, "hi")
