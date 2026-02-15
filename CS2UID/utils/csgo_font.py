from pathlib import Path

from PIL import ImageFont

FONT_MAIN_PATH = Path(__file__).parent / "fonts/loli.ttf"
FONT_TIELE_PATH = Path(__file__).parent / "fonts/title.ttf"


def csgo_font_main(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_MAIN_PATH), size=size)


def csgo_font_title(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_TIELE_PATH), size=size)


csgo_font_12 = csgo_font_main(12)
csgo_font_14 = csgo_font_main(14)
csgo_font_15 = csgo_font_main(15)
csgo_font_18 = csgo_font_main(18)
csgo_font_20 = csgo_font_main(20)
csgo_font_22 = csgo_font_main(22)
csgo_font_23 = csgo_font_main(23)
csgo_font_24 = csgo_font_main(24)
csgo_font_25 = csgo_font_main(25)
csgo_font_26 = csgo_font_main(26)
csgo_font_28 = csgo_font_main(28)
csgo_font_30 = csgo_font_main(30)
csgo_font_32 = csgo_font_main(32)
csgo_font_34 = csgo_font_main(34)
csgo_font_36 = csgo_font_main(36)
csgo_font_38 = csgo_font_main(38)
csgo_font_40 = csgo_font_main(40)
csgo_font_42 = csgo_font_main(42)
csgo_font_44 = csgo_font_main(44)
csgo_font_50 = csgo_font_main(50)
