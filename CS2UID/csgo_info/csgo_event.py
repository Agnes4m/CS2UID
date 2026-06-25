import asyncio
from datetime import datetime, timedelta, timezone
from io import BytesIO

from PIL import Image, ImageDraw

from gsuid_core.utils.image.convert import convert_img

from ..utils.csgo_font import (
    csgo_font_14,
    csgo_font_18,
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
    match_id = m.get("matchId", "")
    if match_id:
        draw.text(
            (card_x + PADDING + 310, y + 10),
            f"ID: {match_id}",
            fill=TEXT_GREEN,
            font=csgo_font_20,
        )

    t1_color = WINNER_GOLD if t1_win else TEXT_WHITE
    t2_color = WINNER_GOLD if t2_win else TEXT_WHITE
    t1_prefix = "★ " if t1_win else ""
    t2_prefix = "★ " if t2_win else ""

    if t1_logo_url:
        logo1 = logos.get(t1_logo_url)
        if logo1:
            lx = card_x + PADDING
            ly = y + 40
            draw.rounded_rectangle(
                (lx - 2, ly - 2, lx + LOGO_SIZE[0] + 2, ly + LOGO_SIZE[1] + 2),
                radius=8,
                fill=(255, 255, 255, 240),
            )
            logo1_resized = logo1.resize(LOGO_SIZE)
            img.paste(logo1_resized, (lx, ly), logo1_resized)
    if t2_logo_url:
        logo2 = logos.get(t2_logo_url)
        if logo2:
            lx = cx + 75
            ly = y + 40
            draw.rounded_rectangle(
                (lx - 2, ly - 2, lx + LOGO_SIZE[0] + 2, ly + LOGO_SIZE[1] + 2),
                radius=8,
                fill=(255, 255, 255, 240),
            )
            logo2_resized = logo2.resize(LOGO_SIZE)
            img.paste(logo2_resized, (lx, ly), logo2_resized)

    t1_full = f"{t1_prefix}{t1_name}"
    t2_full = f"{t2_prefix}{t2_name}"
    t1_font = csgo_font_18 if len(t1_name) > 16 else csgo_font_24
    t2_font = csgo_font_18 if len(t2_name) > 16 else csgo_font_24
    draw.text(
        (card_x + PADDING + 90, y + 48),
        t1_full,
        fill=t1_color,
        font=t1_font,
    )
    draw.text(
        (cx + 165, y + 48),
        t2_full,
        fill=t2_color,
        font=t2_font,
    )

    score_color = TEXT_YELLOW if is_finished else TEXT_WHITE
    score_text = f"{s1} : {s2}" if s1 != "-" or s2 != "-" else "VS"
    score_bbox = draw.textbbox((0, 0), score_text, font=csgo_font_36)
    score_w = score_bbox[2] - score_bbox[0]
    score_x = cx - score_w // 2
    draw.text(
        (score_x, y + 40), score_text, fill=score_color, font=csgo_font_36
    )


async def get_csgo_event_img(dto_list: list, query_date: str = "") -> bytes:
    if query_date:
        parts = query_date.split("-")
        if len(parts) >= 2:
            date_str = f"{parts[1]}-{parts[2]}"
        else:
            date_str = query_date[-5:]
    else:
        date_str = datetime.now(tz_cn).strftime("%m-%d")

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
    FOOTER_H = 60
    total_h += FOOTER_H

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

    footer = Image.open(TEXTURE / "base" / "footer.png").resize((WIDTH, 50))
    img.paste(footer, (0, total_h - 55), footer)

    result = BytesIO()
    img.save(result, format="PNG")
    return await convert_img(result.getvalue())


_EVENT_LOGO_SIZE = (50, 50)
_TEAM_LOGO_SM = (36, 36)
_CAL_CARD_PAD = 16


def _format_dt(ms: int) -> str:
    return (
        datetime.fromtimestamp(ms / 1000, tz_cn).strftime("%m-%d")
        if ms
        else "TBD"
    )


def _draw_event_card(
    img: Image.Image,
    draw: ImageDraw,
    evt: dict,
    logos: dict[str, Image.Image],
    y: int,
) -> int:
    name = evt.get("name", "未知")
    level = evt.get("level") or ""
    prize = evt.get("prize", "")
    start = _format_dt(evt.get("startTime", 0))
    end = _format_dt(evt.get("endTime", 0))
    logo_url = evt.get("logo", "")
    teams = evt.get("teamDTOList", [])
    event_id = evt.get("eventId", "")
    region = evt.get("region") or {}
    location = region.get("location") or ""

    card_x = MARGIN
    card_w = WIDTH - 2 * MARGIN

    team_lines = max(1, (len(teams) + 3) // 4) if teams else 0
    card_h = 120 + team_lines * 46

    _rounded_rect(
        draw, (card_x, y, card_x + card_w, y + card_h), CARD_RADIUS, CARD_BG
    )
    draw.rounded_rectangle(
        (card_x, y, card_x + card_w, y + card_h),
        radius=CARD_RADIUS,
        outline=CARD_BORDER,
        width=1,
    )

    elx = card_x + _CAL_CARD_PAD
    ely = y + _CAL_CARD_PAD
    if logo_url:
        ev_logo = logos.get(logo_url)
        if ev_logo:
            el_resized = ev_logo.resize(_EVENT_LOGO_SIZE)
            draw.rounded_rectangle(
                (
                    elx - 2,
                    ely - 2,
                    elx + _EVENT_LOGO_SIZE[0] + 2,
                    ely + _EVENT_LOGO_SIZE[1] + 2,
                ),
                radius=6,
                fill=(255, 255, 255, 240),
            )
            img.paste(el_resized, (elx, ely), el_resized)

    name_x = elx + _EVENT_LOGO_SIZE[0] + 12 if logo_url else elx
    draw.text((name_x, ely), name, fill=TEXT_WHITE, font=csgo_font_24)

    if level:
        level_x = (
            name_x + draw.textbbox((0, 0), name, font=csgo_font_24)[2] + 10
        )
        lv_color = TEXT_YELLOW if level in ("Major", "T1") else TEXT_BLUE
        draw.text((level_x, ely + 2), level, fill=lv_color, font=csgo_font_18)
        if level in ("Major", "T1"):
            hot_x = (
                level_x
                + draw.textbbox((0, 0), level, font=csgo_font_18)[2]
                + 6
            )
            draw.text((hot_x, ely + 2), "🔥", fill=TEXT_RED, font=csgo_font_18)

    info_y1 = ely + 28
    range_text = f"📅 {start} ~ {end}"
    draw.text((name_x, info_y1), range_text, fill=TEXT_BLUE, font=csgo_font_20)
    if location:
        loc_x = (
            name_x
            + draw.textbbox((0, 0), range_text, font=csgo_font_20)[2]
            + 16
        )
        draw.text(
            (loc_x, info_y1),
            f"🏟 {location}",
            fill=TEXT_GREEN,
            font=csgo_font_20,
        )
    info_y2 = ely + 52
    id_text = f"ID: {event_id}"
    if prize:
        draw.text(
            (name_x, info_y2),
            f"💰 {prize}",
            fill=TEXT_YELLOW,
            font=csgo_font_20,
        )
        pw = draw.textbbox((0, 0), f"💰 {prize}", font=csgo_font_20)[2]
        draw.text(
            (name_x + pw + 16, info_y2),
            id_text,
            fill=(255, 150, 100),
            font=csgo_font_20,
        )
    else:
        draw.text(
            (name_x, info_y2),
            id_text,
            fill=(255, 150, 100),
            font=csgo_font_20,
        )

    if teams:
        team_y = y + 96
        for i, team in enumerate(teams):
            tx = card_x + _CAL_CARD_PAD + (i % 4) * 210
            ty = team_y + (i // 4) * 46
            t_logo_url = team.get("logoBlack") or team.get("logoWhite")
            if t_logo_url:
                t_logo = logos.get(t_logo_url)
                if t_logo:
                    t_resized = t_logo.resize(_TEAM_LOGO_SM)
                    draw.rounded_rectangle(
                        (
                            tx - 1,
                            ty - 1,
                            tx + _TEAM_LOGO_SM[0] + 1,
                            ty + _TEAM_LOGO_SM[1] + 1,
                        ),
                        radius=4,
                        fill=(255, 255, 255, 240),
                    )
                    img.paste(t_resized, (tx, ty), t_resized)
            t_name = team.get("name", "")
            t_font = csgo_font_14 if len(t_name) > 12 else csgo_font_18
            draw.text(
                (tx + _TEAM_LOGO_SM[0] + 6, ty + 6),
                t_name,
                fill=TEXT_GRAY,
                font=t_font,
            )

    return card_h + 8


async def get_csgo_calendar_img(groups: list, start: str, end: str) -> bytes:
    logo_urls: list[str] = []
    for group in groups:
        for evt in group.get("eventCardDetails", []):
            logo_url = evt.get("logo", "")
            if logo_url:
                logo_urls.append(logo_url)
            for team in evt.get("teamDTOList", []):
                t_logo = team.get("logoBlack") or team.get("logoWhite")
                if t_logo:
                    logo_urls.append(t_logo)

    downloaded: dict[str, Image.Image] = {}
    if logo_urls:
        results = await asyncio.gather(
            *[_download_img(url) for url in set(logo_urls)],
            return_exceptions=True,
        )
        for url, img_obj in zip(set(logo_urls), results, strict=True):
            if isinstance(img_obj, Image.Image):
                downloaded[url] = (
                    img_obj.convert("RGBA")
                    if img_obj.mode != "RGBA"
                    else img_obj
                )

    total_h = TITLE_H + 20
    for group in groups:
        details = group.get("eventCardDetails", [])
        if not details:
            continue
        total_h += HEADER_H + 10
        for evt in details:
            teams = evt.get("teamDTOList", [])
            team_lines = max(1, (len(teams) + 3) // 4) if teams else 0
            total_h += 120 + team_lines * 46 + 8
    FOOTER_H = 60
    total_h += FOOTER_H

    img = Image.new("RGBA", (WIDTH, total_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    bg_img = Image.open(TEXTURE / "bg" / "1.jpg").resize((WIDTH, total_h))
    bg_img.putalpha(80)
    img.paste(bg_img, (0, 0), bg_img)

    draw.text((MARGIN, 30), "CS2 赛事日历", fill=TEXT_WHITE, font=csgo_font_36)
    draw.text(
        (MARGIN, 75),
        f"{start} ~ {end}",
        fill=TEXT_GRAY,
        font=csgo_font_20,
    )

    y = TITLE_H
    for group in groups:
        month = group.get("matchDate", "")
        details = group.get("eventCardDetails", [])
        if not details:
            continue

        _rounded_rect(
            draw,
            (MARGIN, y, WIDTH - MARGIN, y + HEADER_H),
            CARD_RADIUS,
            (40, 45, 55),
        )
        draw.text(
            (MARGIN + PADDING, y + 12),
            month,
            fill=TEXT_WHITE,
            font=csgo_font_30,
        )
        draw.text(
            (WIDTH - MARGIN - PADDING - 100, y + 15),
            f"{len(details)} 赛事",
            fill=TEXT_GRAY,
            font=csgo_font_20,
        )
        y += HEADER_H + 10

        for evt in details:
            card_h = _draw_event_card(img, draw, evt, downloaded, y)
            y += card_h

    footer = Image.open(TEXTURE / "base" / "footer.png").resize((WIDTH, 50))
    img.paste(footer, (0, total_h - 55), footer)

    result = BytesIO()
    img.save(result, format="PNG")
    return await convert_img(result.getvalue())


_SUBTYPE_NAMES = {
    5: "热门",
    4: "Major",
    1: "Blast",
    2: "ESL",
    3: "IEM",
    6: "PGL",
    7: "PWE",
    8: "SL",
    9: "FISSURE",
    10: "其他",
    0: "全部",
}


async def get_csgo_eventlist_img(dto_list: list, label: str = "热门") -> bytes:
    logo_urls = []
    for evt in dto_list:
        url = evt.get("logo", "")
        if url:
            logo_urls.append(url)

    downloaded = {}
    if logo_urls:
        results = await asyncio.gather(
            *[_download_img(url) for url in set(logo_urls)],
            return_exceptions=True,
        )
        for url, img_obj in zip(set(logo_urls), results, strict=True):
            if isinstance(img_obj, Image.Image):
                downloaded[url] = (
                    img_obj.convert("RGBA")
                    if img_obj.mode != "RGBA"
                    else img_obj
                )

    CARD_H = 100
    FOOTER_H = 60
    total_h = TITLE_H + 20 + len(dto_list) * (CARD_H + 8) + FOOTER_H

    img = Image.new("RGBA", (WIDTH, total_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    bg_img = Image.open(TEXTURE / "bg" / "1.jpg").resize((WIDTH, total_h))
    bg_img.putalpha(80)
    img.paste(bg_img, (0, 0), bg_img)

    draw.text(
        (MARGIN, 30), f"CS2 {label}赛事", fill=TEXT_WHITE, font=csgo_font_36
    )
    draw.text(
        (MARGIN, 75),
        f"共 {len(dto_list)} 个赛事",
        fill=TEXT_GRAY,
        font=csgo_font_20,
    )

    y = TITLE_H
    for evt in dto_list:
        name = evt.get("nameZh", evt.get("name", "未知"))
        logo_url = evt.get("logo", "")
        start = _format_dt(evt.get("startTime", 0))
        end = _format_dt(evt.get("endTime", 0))
        prize = evt.get("prize", "")
        region = evt.get("regionDTO") or {}
        location = region.get("locationCn") or region.get("location") or ""
        hot = evt.get("hot", False)
        evt_sub = evt.get("eventSubType", 0)

        _rounded_rect(
            draw, (MARGIN, y, WIDTH - MARGIN, y + CARD_H), CARD_RADIUS, CARD_BG
        )
        draw.rounded_rectangle(
            (MARGIN, y, WIDTH - MARGIN, y + CARD_H),
            radius=CARD_RADIUS,
            outline=CARD_BORDER,
            width=1,
        )

        elx = MARGIN + PADDING
        ely = y + 12
        if logo_url:
            ev_logo = downloaded.get(logo_url)
            if ev_logo:
                el_resized = ev_logo.resize((40, 40))
                draw.rounded_rectangle(
                    (elx - 2, ely - 2, elx + 42, ely + 42),
                    radius=6,
                    fill=(255, 255, 255, 240),
                )
                img.paste(el_resized, (elx, ely), el_resized)

        name_x = elx + 52 if logo_url else elx
        draw.text((name_x, ely), name, fill=TEXT_WHITE, font=csgo_font_24)

        sub_tag = _SUBTYPE_NAMES.get(evt_sub, "")
        nx2 = name_x + draw.textbbox((0, 0), name, font=csgo_font_24)[2] + 8
        if sub_tag:
            draw.text(
                (nx2, ely + 2), sub_tag, fill=TEXT_BLUE, font=csgo_font_18
            )
            nx2 += draw.textbbox((0, 0), sub_tag, font=csgo_font_18)[2] + 6
        if hot:
            draw.text((nx2, ely + 2), "🔥", fill=TEXT_RED, font=csgo_font_18)

        iy = ely + 30
        range_text = f"📅 {start} ~ {end}"
        draw.text((name_x, iy), range_text, fill=TEXT_BLUE, font=csgo_font_20)
        seg_x = (
            name_x
            + draw.textbbox((0, 0), range_text, font=csgo_font_20)[2]
            + 12
        )
        if location:
            draw.text(
                (seg_x, iy),
                f"🏟 {location}",
                fill=TEXT_GREEN,
                font=csgo_font_20,
            )
            seg_x += (
                draw.textbbox((0, 0), f"🏟 {location}", font=csgo_font_20)[2]
                + 12
            )
        if prize:
            draw.text(
                (seg_x, iy), f"💰 {prize}", fill=TEXT_YELLOW, font=csgo_font_20
            )

        y += CARD_H + 8

    footer = Image.open(TEXTURE / "base" / "footer.png").resize((WIDTH, 50))
    img.paste(footer, (0, total_h - 55), footer)

    result = BytesIO()
    img.save(result, format="PNG")
    return await convert_img(result.getvalue())
