import asyncio
from datetime import datetime, timedelta, timezone
from io import BytesIO

from PIL import Image, ImageDraw

from gsuid_core.utils.image.convert import convert_img

from ..utils.csgo_font import (
    csgo_font_14,
    csgo_font_15,
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
TEXT_GRAY = (180, 182, 187)
TEXT_GREEN = (100, 200, 130)
TEXT_RED = (220, 90, 90)
TEXT_YELLOW = (240, 200, 60)
TEXT_DARK_YELLOW = (200, 160, 40)
TEXT_BLUE = (80, 160, 240)
WINNER_GOLD = (255, 215, 50)

tz_cn = timezone(timedelta(hours=8))
_status_map = {1: "待定", 2: "即将开始", 3: "已结束"}
_bo_map = {"bo1": "BO1", "bo3": "BO3", "bo5": "BO5", "def": "DEF"}


def _format_ts(ms: int) -> str:
    return (
        datetime.fromtimestamp(ms / 1000, tz_cn).strftime("%m-%d %H:%M")
        if ms
        else "TBD"
    )


def _format_dt(ms: int) -> str:
    return (
        datetime.fromtimestamp(ms / 1000, tz_cn).strftime("%m-%d")
        if ms
        else "TBD"
    )


def _rounded_rect(draw: ImageDraw, xy: tuple, r: int, fill: tuple):
    draw.rounded_rectangle(xy, radius=r, fill=fill)


_BG_PATH = TEXTURE / "bg" / "1.jpg"


def _load_cover_bg(total_h: int) -> Image.Image:
    bg = Image.open(_BG_PATH)
    bw, bh = bg.size
    scale = max(WIDTH / bw, total_h / bh)
    new_w, new_h = int(bw * scale), int(bh * scale)
    bg = bg.resize((new_w, new_h))
    left = (new_w - WIDTH) // 2
    top = (new_h - total_h) // 2
    bg = bg.crop((left, top, left + WIDTH, top + total_h))
    bg.putalpha(80)
    return bg


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


async def get_csgo_event_img(
    dto_list: list, query_date: str = "", title: str = "CS2 今日赛事"
) -> bytes:
    if query_date:
        parts = query_date.split("-")
        if len(parts) >= 3:
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

    bg_img = _load_cover_bg(total_h)
    img.paste(bg_img, (0, 0), bg_img)

    draw.text((MARGIN, 30), title, fill=TEXT_WHITE, font=csgo_font_36)
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

    bg_img = _load_cover_bg(total_h)
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

    bg_img = _load_cover_bg(total_h)
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


def _rating_color(r: float) -> tuple:
    return TEXT_GREEN if r >= 1.0 else TEXT_RED


async def get_csgo_match_analysis_img(
    detail_resp: dict,
    analysis_resp: dict,
    share_resp: dict | None = None,
) -> bytes:
    match_data = detail_resp.get("result", {}).get("match", {})
    team1 = match_data.get("team1DTO", {})
    team2 = match_data.get("team2DTO", {})
    s1 = (
        match_data.get("score1")
        if match_data.get("score1") is not None
        else "-"
    )
    s2 = (
        match_data.get("score2")
        if match_data.get("score2") is not None
        else "-"
    )
    bo = _bo_map.get(match_data.get("bo", ""), match_data.get("bo", ""))
    status = _status_map.get(match_data.get("status"), "未知")
    t1_logo_url = team1.get("logoBlack") or team1.get("logoWhite")
    t2_logo_url = team2.get("logoBlack") or team2.get("logoWhite")
    stats_list = match_data.get("statsDTOList") or []

    logo_urls = [u for u in [t1_logo_url, t2_logo_url] if u]
    downloaded = {}
    if logo_urls:
        results = await asyncio.gather(
            *[_download_img(u) for u in set(logo_urls)],
            return_exceptions=True,
        )
        for url, img_obj in zip(set(logo_urls), results, strict=True):
            if isinstance(img_obj, Image.Image):
                downloaded[url] = (
                    img_obj.convert("RGBA")
                    if img_obj.mode != "RGBA"
                    else img_obj
                )

    summary_stats = [
        s for s in stats_list if s.get("mapDTO", {}).get("nameEn") == "all"
    ]
    map_stats = [
        s for s in stats_list if s.get("mapDTO", {}).get("nameEn") != "all"
    ]
    n_maps = len(map_stats)
    is_upcoming = match_data.get("status") == 2
    MAP_ROW = 36
    PLAYER_ROW = 32
    TABLE_H = 28
    header_h = 160
    total_h = (
        header_h
        + 30
        + bool(summary_stats) * MAP_ROW
        + n_maps * MAP_ROW
        + 20
        + TABLE_H
    )
    analysis_data = analysis_resp.get("result", [])
    for team in analysis_data:
        total_h += (
            TABLE_H + len(team.get("playerStatsList", [])) * PLAYER_ROW + 10
        )
    total_h += 120
    if not is_upcoming and summary_stats:
        s0 = summary_stats[0]
        t1_count = len(s0.get("team1PlayerStatsDTOList", []))
        t2_count = len(s0.get("team2PlayerStatsDTOList", []))
        if t1_count + t2_count > 0:
            total_h += (t1_count + t2_count) * PLAYER_ROW + TABLE_H * 2 + 40

    img = Image.new("RGBA", (WIDTH, total_h), BG_COLOR)
    draw = ImageDraw.Draw(img)
    bg_img = _load_cover_bg(total_h)
    img.paste(bg_img, (0, 0), bg_img)

    event_title = (
        match_data.get("csgoEventDTO", {}).get("nameZh")
        or (
            share_resp.get("result", {}).get("eventName")
            if share_resp
            else None
        )
        or ""
    )
    t1_name = team1.get("name", "")
    t2_name = team2.get("name", "")
    y = 12
    if event_title:
        draw.text((MARGIN, y), event_title, fill=TEXT_WHITE, font=csgo_font_20)
        y += 28
    support_map = match_data.get("teamSupportRateMap") or {}
    ls = 40
    for logo_url, t in [(t1_logo_url, team1), (t2_logo_url, team2)]:
        tname = t.get("name", "")
        if logo_url:
            ev_logo = downloaded.get(logo_url)
            if ev_logo:
                el_resized = ev_logo.resize((ls, ls))
                draw.rounded_rectangle(
                    (MARGIN + 8, y, MARGIN + 8 + ls + 4, y + ls + 4),
                    radius=6,
                    fill=(255, 255, 255, 240),
                )
                img.paste(el_resized, (MARGIN + 10, y + 2), el_resized)
        draw.text(
            (MARGIN + ls + 24, y + 6),
            tname,
            fill=TEXT_WHITE,
            font=csgo_font_24,
        )
        y += ls + 12

    cx = WIDTH // 2
    if is_upcoming:
        score_text = "VS"
        draw.text(
            (cx - 15, 20),
            score_text,
            fill=TEXT_YELLOW,
            font=csgo_font_36,
        )
    else:
        score_text = f"{s1} : {s2}"
        sb = draw.textbbox((0, 0), score_text, font=csgo_font_36)
        draw.text(
            (cx - (sb[2] - sb[0]) // 2, 20),
            score_text,
            fill=TEXT_YELLOW,
            font=csgo_font_36,
        )
    draw.text((cx - 20, 60), bo, fill=TEXT_GRAY, font=csgo_font_20)
    draw.text((cx - 20, 80), status, fill=TEXT_GRAY, font=csgo_font_20)
    if support_map:
        t1_id = str(match_data.get("team1Id", ""))
        t2_id = str(match_data.get("team2Id", ""))
        s1_pct = support_map.get(t1_id, 50)
        s2_pct = support_map.get(t2_id, 50)
        bar_w = 260
        bar_h = 10
        bar_x = cx - bar_w // 2
        bar_y = 120
        bar_lab_y = 96
        draw.rounded_rectangle(
            (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
            radius=5,
            fill=(50, 55, 65),
        )
        fill_w = (
            int(bar_w * s1_pct / (s1_pct + s2_pct))
            if (s1_pct + s2_pct) > 0
            else bar_w // 2
        )
        draw.rounded_rectangle(
            (bar_x, bar_y, bar_x + fill_w, bar_y + bar_h),
            radius=5,
            fill=TEXT_BLUE,
        )
        draw.text(
            (bar_x, bar_lab_y),
            f"{t1_name[:10]}",
            fill=TEXT_BLUE,
            font=csgo_font_18,
        )
        draw.text(
            (bar_x + 10, bar_lab_y + 22),
            f"{s1_pct}%",
            fill=TEXT_WHITE,
            font=csgo_font_14,
        )
        draw.text(
            (bar_x + bar_w - 80, bar_lab_y),
            f"{t2_name[:10]}",
            fill=TEXT_GREEN,
            font=csgo_font_18,
        )
        draw.text(
            (bar_x + bar_w - 50, bar_lab_y + 22),
            f"{s2_pct}%",
            fill=TEXT_WHITE,
            font=csgo_font_14,
        )
        draw.text(
            (cx - 30, bar_y + 16), "支持率", fill=TEXT_GRAY, font=csgo_font_15
        )
    match_time_str = _format_ts(match_data.get("startTime", 0))
    id_text = f"🆔 {match_data.get('matchId', '')}"
    time_text = f"⏰ {match_time_str}"
    id_w = draw.textbbox((0, 0), id_text, font=csgo_font_18)[2]
    time_w = draw.textbbox((0, 0), time_text, font=csgo_font_18)[2]
    draw.text(
        (WIDTH - MARGIN - id_w, 110),
        id_text,
        fill=TEXT_GRAY,
        font=csgo_font_18,
    )
    draw.text(
        (WIDTH - MARGIN - time_w, 130),
        time_text,
        fill=TEXT_GRAY,
        font=csgo_font_18,
    )

    y = 170
    if summary_stats:
        s = summary_stats[0]
        _draw_map_row(
            draw,
            "总览",
            s.get("score1"),
            s.get("score2"),
            s.get("team1rating", 0),
            s.get("team2rating", 0),
            y,
        )
        y += MAP_ROW
    _cn = ["一", "二", "三", "四", "五"]
    for idx, ms in enumerate(map_stats, 1):
        mdto = ms.get("mapDTO", {})
        mname = mdto.get("nameZh", mdto.get("nameEn", ""))
        _draw_map_row(
            draw,
            f"图{_cn[idx - 1]}：{mname}",
            ms.get("score1"),
            ms.get("score2"),
            ms.get("team1rating", 0),
            ms.get("team2rating", 0),
            y,
        )
        y += MAP_ROW

    y += 10
    if not is_upcoming and summary_stats:
        s = summary_stats[0]
        for team_idx, team_key in enumerate(
            ["team1PlayerStatsDTOList", "team2PlayerStatsDTOList"]
        ):
            players = s.get(team_key, [])
            if not players:
                continue
            tname = (
                team1.get("name", "")
                if team_idx == 0
                else team2.get("name", "")
            )
            _rounded_rect(
                draw,
                (MARGIN, y, WIDTH - MARGIN, y + TABLE_H),
                CARD_RADIUS,
                (40, 45, 55),
            )
            draw.text(
                (MARGIN + 12, y + 2),
                f"{tname} 本场数据",
                fill=TEXT_WHITE,
                font=csgo_font_20,
            )
            y += TABLE_H
            col_defs = [
                ("选手", 10),
                ("K/D/A", 180),
                ("ADR", 310),
                ("HS", 390),
                ("Rating", 480),
            ]
            for label, x in col_defs:
                draw.text(
                    (MARGIN + x, y + 4),
                    label,
                    fill=TEXT_DARK_YELLOW,
                    font=csgo_font_15,
                )
            y += TABLE_H + 2
            for p in players:
                pdto = p.get("playerDTO", {})
                pname = pdto.get("name", "")
                k = p.get("kills", 0)
                d = p.get("deaths", 0)
                a = p.get("assists", 0)
                adr = p.get("adr", 0) or 0
                hs = p.get("hskills", 0)
                rt = p.get("rating", 0) or 0
                draw.rounded_rectangle(
                    (MARGIN + 2, y, WIDTH - MARGIN - 2, y + PLAYER_ROW),
                    radius=4,
                    fill=(35, 38, 43),
                )
                draw.text(
                    (MARGIN + 10, y + 4),
                    pname,
                    fill=TEXT_WHITE,
                    font=csgo_font_18,
                )
                draw.text(
                    (MARGIN + 180, y + 4),
                    f"{k}/{d}/{a}",
                    fill=TEXT_GRAY,
                    font=csgo_font_18,
                )
                draw.text(
                    (MARGIN + 310, y + 4),
                    f"{adr:.1f}",
                    fill=TEXT_GRAY,
                    font=csgo_font_18,
                )
                draw.text(
                    (MARGIN + 390, y + 4),
                    f"{hs}",
                    fill=TEXT_GRAY,
                    font=csgo_font_18,
                )
                draw.text(
                    (MARGIN + 480, y + 4),
                    f"{rt:.2f}",
                    fill=_rating_color(rt),
                    font=csgo_font_18,
                )
                y += PLAYER_ROW
            y += 10
    for team_idx, team in enumerate(analysis_data):
        players = team.get("playerStatsList", [])
        tname = (
            team1.get("name", "") if team_idx == 0 else team2.get("name", "")
        )
        _rounded_rect(
            draw,
            (MARGIN, y, WIDTH - MARGIN, y + TABLE_H),
            CARD_RADIUS,
            (40, 45, 55),
        )
        draw.text(
            (MARGIN + 12, y + 2),
            f"Team {team_idx + 1} ({tname}) 近期数据",
            fill=TEXT_WHITE,
            font=csgo_font_20,
        )
        y += TABLE_H

        col_defs = [
            ("选手", 10),
            ("KAST", 220),
            ("KPR", 300),
            ("DPR", 370),
            ("ADR", 440),
            ("Rating", 510),
        ]
        for label, x in col_defs:
            draw.text(
                (MARGIN + x, y + 4),
                label,
                fill=TEXT_DARK_YELLOW,
                font=csgo_font_15,
            )
        y += TABLE_H + 2

        for p in players:
            r = p.get("rating", 0) or 0
            draw.rounded_rectangle(
                (MARGIN + 2, y, WIDTH - MARGIN - 2, y + PLAYER_ROW),
                radius=4,
                fill=(35, 38, 43),
            )
            draw.text(
                (MARGIN + 10, y + 4),
                p.get("name", ""),
                fill=TEXT_WHITE,
                font=csgo_font_18,
            )
            draw.text(
                (MARGIN + 220, y + 4),
                str(p.get("kast", "")),
                fill=TEXT_GRAY,
                font=csgo_font_18,
            )
            draw.text(
                (MARGIN + 300, y + 4),
                f"{p.get('kpr', 0):.2f}",
                fill=TEXT_GRAY,
                font=csgo_font_18,
            )
            draw.text(
                (MARGIN + 370, y + 4),
                f"{p.get('dpr', 0):.2f}",
                fill=TEXT_GRAY,
                font=csgo_font_18,
            )
            draw.text(
                (MARGIN + 440, y + 4),
                f"{p.get('adr', 0):.1f}",
                fill=TEXT_GRAY,
                font=csgo_font_18,
            )
            draw.text(
                (MARGIN + 510, y + 4),
                f"{r:.2f}",
                fill=_rating_color(r),
                font=csgo_font_18,
            )
            y += PLAYER_ROW
        y += 30

    footer = Image.open(TEXTURE / "base" / "footer.png").resize((WIDTH, 50))
    img.paste(footer, (0, total_h - 55), footer)
    result = BytesIO()
    img.save(result, format="PNG")
    return await convert_img(result.getvalue())


def _draw_map_row(
    draw: ImageDraw,
    map_name: str,
    s1,
    s2,
    r1,
    r2,
    y: int,
):
    cx = WIDTH // 2
    draw.rounded_rectangle(
        (MARGIN, y, WIDTH - MARGIN, y + 32),
        radius=6,
        fill=(35, 38, 43),
    )
    draw.text(
        (MARGIN + 12, y + 4), map_name, fill=TEXT_WHITE, font=csgo_font_20
    )
    draw.text(
        (MARGIN + 160, y + 4),
        f"评分: {r1:.2f}",
        fill=_rating_color(r1),
        font=csgo_font_18,
    )
    draw.text(
        (cx - 20, y + 4), f"{s1}:{s2}", fill=TEXT_YELLOW, font=csgo_font_20
    )
    draw.text(
        (cx + 50, y + 4),
        f"评分: {r2:.2f}",
        fill=_rating_color(r2),
        font=csgo_font_18,
    )
