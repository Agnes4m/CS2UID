import asyncio
from datetime import datetime, timedelta, timezone
from io import BytesIO

from PIL import Image, ImageDraw

from gsuid_core.utils.image.convert import convert_img

from ..utils.csgo_font import (
    csgo_font_20,
    csgo_font_24,
    csgo_font_30,
    csgo_font_36,
)
from .csgo_path import TEXTURE
from .utils import _download_img

WIDTH = 900
MARGIN = 30
CARD_H = 110
HEADER_H = 60
TITLE_H = 120
PADDING = 20
LOGO_SIZE = (60, 60)
CARD_RADIUS = 12

BG_COLOR = (18, 20, 23)
CARD_BG = (30, 33, 38)
CARD_BORDER = (45, 50, 55)
TEXT_WHITE = (220, 220, 225)
TEXT_GRAY = (140, 142, 147)
TEXT_GREEN = (100, 200, 130)
TEXT_RED = (220, 90, 90)
TEXT_YELLOW = (240, 200, 60)
TEXT_BLUE = (80, 160, 240)
WINNER_GOLD = (255, 215, 50)

tz_cn = timezone(timedelta(hours=8))
_status_map = {1: "待定", 2: "即将开始", 3: "已结束"}
_bo_map = {"bo1": "BO1", "bo3": "BO3", "bo5": "BO5", "def": "DEF"}


def _format_ts(ms: int) -> str:
    return (
        datetime.fromtimestamp(ms / 1000, tz_cn).strftime("%H:%M")
        if ms
        else "TBD"
    )


def _rounded_rect(draw: ImageDraw, xy: tuple, r: int, fill: tuple):
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def _draw_match_card(
    img: Image.Image,
    draw: ImageDraw,
    m: dict,
    logos: dict[str, Image.Image],
    y: int,
):
    s1 = m["score1"] if m["score1"] is not None else "-"
    s2 = m["score2"] if m["score2"] is not None else "-"
    bo = _bo_map.get(m["bo"], m["bo"])
    status = _status_map.get(m["status"], f"状态{m['status']}")
    t1_name = m["team1DTO"]["name"]
    t2_name = m["team2DTO"]["name"]
    time_str = _format_ts(m["startTime"])
    t1_logo_url = m["team1DTO"]["logoBlack"] or m["team1DTO"]["logoWhite"]
    t2_logo_url = m["team2DTO"]["logoBlack"] or m["team2DTO"]["logoWhite"]

    is_finished = m["status"] == 3
    is_live = m["status"] == 2
    winner_id = m.get("winnerTeamId")
    t1_win = bool(is_finished and winner_id and winner_id == m["team1Id"])
    t2_win = bool(is_finished and winner_id and winner_id == m["team2Id"])

    cx = WIDTH // 2

    card_x = MARGIN
    card_w = WIDTH - 2 * MARGIN

    _rounded_rect(
        draw, (card_x, y, card_x + card_w, y + CARD_H), CARD_RADIUS, CARD_BG
    )
    draw.rounded_rectangle(
        (card_x, y, card_x + card_w, y + CARD_H),
        radius=CARD_RADIUS,
        outline=CARD_BORDER,
        width=1,
    )

    status_color = (
        TEXT_RED if is_finished else (TEXT_GREEN if is_live else TEXT_BLUE)
    )
    status_text = f"{'● ' if is_live else ''}{status}"
    draw.text(
        (card_x + PADDING, y + 10),
        status_text,
        fill=status_color,
        font=csgo_font_20,
    )
    draw.text(
        (card_x + PADDING + 150, y + 10),
        time_str,
        fill=TEXT_GRAY,
        font=csgo_font_20,
    )
    draw.text(
        (card_x + PADDING + 240, y + 10), bo, fill=TEXT_GRAY, font=csgo_font_20
    )

    t1_color = WINNER_GOLD if t1_win else TEXT_WHITE
    t2_color = WINNER_GOLD if t2_win else TEXT_WHITE
    t1_prefix = "★ " if t1_win else ""
    t2_prefix = "★ " if t2_win else ""

    if t1_logo_url:
        logo1 = logos.get(t1_logo_url)
        if logo1:
            logo1_resized = logo1.resize(LOGO_SIZE)
            img.paste(logo1_resized, (card_x + PADDING, y + 40), logo1_resized)
    if t2_logo_url:
        logo2 = logos.get(t2_logo_url)
        if logo2:
            logo2_resized = logo2.resize(LOGO_SIZE)
            img.paste(logo2_resized, (cx + 75, y + 40), logo2_resized)

    draw.text(
        (card_x + PADDING + 90, y + 48),
        f"{t1_prefix}{t1_name}",
        fill=t1_color,
        font=csgo_font_24,
    )
    draw.text(
        (cx + 165, y + 48),
        f"{t2_prefix}{t2_name}",
        fill=t2_color,
        font=csgo_font_24,
    )

    score_color = TEXT_YELLOW if is_finished else TEXT_WHITE
    score_text = f"{s1} : {s2}" if s1 != "-" or s2 != "-" else "VS"
    score_bbox = draw.textbbox((0, 0), score_text, font=csgo_font_36)
    score_w = score_bbox[2] - score_bbox[0]
    score_x = cx - score_w // 2
    draw.text(
        (score_x, y + 40), score_text, fill=score_color, font=csgo_font_36
    )


async def get_csgo_event_img(dto_list: list) -> bytes:
    now = datetime.now(tz_cn)
    date_str = now.strftime("%m-%d")

    events: dict[str, list] = {}
    for m in dto_list:
        event_name = m["csgoEventDTO"]["nameZh"]
        events.setdefault(event_name, []).append(m)

    logo_urls: list[str] = []
    for m in dto_list:
        t1_logo = m["team1DTO"]["logoBlack"] or m["team1DTO"]["logoWhite"]
        t2_logo = m["team2DTO"]["logoBlack"] or m["team2DTO"]["logoWhite"]
        if t1_logo:
            logo_urls.append(t1_logo)
        if t2_logo:
            logo_urls.append(t2_logo)
    downloaded: dict[str, Image.Image] = {}
    if logo_urls:
        results = await asyncio.gather(
            *[_download_img(url) for url in set(logo_urls)],
            return_exceptions=True,
        )
        for url, img in zip(set(logo_urls), results, strict=True):
            if isinstance(img, Image.Image):
                downloaded[url] = (
                    img.convert("RGBA") if img.mode != "RGBA" else img
                )

    total_h = TITLE_H + 20
    for _, matches in events.items():
        total_h += HEADER_H + 10
        total_h += len(matches) * (CARD_H + 8)
    total_h += 40

    img = Image.new("RGBA", (WIDTH, total_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    bg_img = Image.open(TEXTURE / "bg" / "1.jpg").resize((WIDTH, total_h))
    bg_img.putalpha(80)
    img.paste(bg_img, (0, 0), bg_img)

    draw.text((MARGIN, 30), "CS2 今日赛事", fill=TEXT_WHITE, font=csgo_font_36)
    draw.text(
        (MARGIN, 75),
        f"{date_str} 共 {len(dto_list)} 场对局",
        fill=TEXT_GRAY,
        font=csgo_font_20,
    )

    y = TITLE_H
    for event_name, matches in events.items():
        _rounded_rect(
            draw,
            (MARGIN, y, WIDTH - MARGIN, y + HEADER_H),
            CARD_RADIUS,
            (40, 45, 55),
        )
        draw.text(
            (MARGIN + PADDING, y + 12),
            event_name,
            fill=TEXT_WHITE,
            font=csgo_font_30,
        )
        draw.text(
            (WIDTH - MARGIN - PADDING - 100, y + 15),
            f"{len(matches)} 场",
            fill=TEXT_GRAY,
            font=csgo_font_20,
        )
        y += HEADER_H + 10

        for m in matches:
            _draw_match_card(img, draw, m, downloaded, y)
            y += CARD_H + 8

    result = BytesIO()
    img.save(result, format="PNG")
    return await convert_img(result.getvalue())
