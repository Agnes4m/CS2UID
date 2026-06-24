"""csgo_info/utils.py 工具函数单元测试。"""

import pytest

from CS2UID.csgo_info.utils import (
    assign_rank,
    parse_s_value,
    rank_to_color,
    scoce_to_color,
)


def test_parse_s_value():
    assert parse_s_value("S5") == "5"
    assert parse_s_value("s5") == "5"
    assert parse_s_value("S10") == "10"
    assert parse_s_value("S+3") == "+3"
    assert parse_s_value("S-2") == "-2"
    assert parse_s_value("Sabc") == ""
    assert parse_s_value("") == ""
    assert parse_s_value("S5abc") == "5"
    assert parse_s_value("123") == ""


@pytest.mark.asyncio
async def test_assign_rank_unranked():
    assert await assign_rank(0, is_rank=False) == ("未定级", 0)


@pytest.mark.asyncio
async def test_assign_rank_d():
    name, progress = await assign_rank(500)
    assert name == "D"
    assert 0 <= progress <= 1


@pytest.mark.asyncio
async def test_assign_rank_c():
    name, _ = await assign_rank(1100)
    assert name == "C"


@pytest.mark.asyncio
async def test_assign_rank_c_plus():
    name, _ = await assign_rank(1250)
    assert name == "C+"


@pytest.mark.asyncio
async def test_assign_rank_b_minus():
    name, _ = await assign_rank(1500)
    assert name == "B-"


@pytest.mark.asyncio
async def test_assign_rank_b():
    name, _ = await assign_rank(1700)
    assert name == "B"


@pytest.mark.asyncio
async def test_assign_rank_a_minus():
    name, _ = await assign_rank(2000)
    assert name == "A-"


@pytest.mark.asyncio
async def test_assign_rank_a():
    name, _ = await assign_rank(2150)
    assert name == "A"


@pytest.mark.asyncio
async def test_assign_rank_a_plus():
    name, _ = await assign_rank(2300)
    assert name == "A+"


@pytest.mark.asyncio
async def test_assign_rank_s():
    name, _ = await assign_rank(2500)
    assert name == "S"


@pytest.mark.asyncio
async def test_assign_rank_boundary():
    name, _ = await assign_rank(1000)
    assert name == "D"


@pytest.mark.asyncio
async def test_rank_to_color():
    assert await rank_to_color("A") == "green"
    assert await rank_to_color("a") == "green"
    assert await rank_to_color("B") == "blue"
    assert await rank_to_color("C") == "red"
    assert await rank_to_color("D") == "black"


@pytest.mark.asyncio
async def test_scoce_to_color():
    assert await scoce_to_color(2.0, 2.0, 1.0) == "green"
    assert await scoce_to_color(1.0, 2.0, 1.0) == "blue"
    assert await scoce_to_color(0.0, 2.0, 1.0) == "red"
    assert await scoce_to_color(0.5, 2.0, 1.0) == "black"
