import os
import sys

from logging import Logger, getLogger
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from consts import *


logger: Logger = getLogger(__name__)


DIR_FONT: str = os.path.join(
	os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "font"
)
DIR_LIB: str = os.path.join(
	os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(DIR_LIB):
	sys.path.append(DIR_LIB)


font_9_sect = ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 80)
font_6_sect = ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 130)
font_4_sect = ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 130)

font_full_1 = ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 200)
font_full_2 = ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 250)
font_full_3 = ImageFont.truetype(os.path.join(DIR_FONT, "Roboto-Bold.ttf"), 300)


def get_time_pos(mode: TimeMode, epd) -> tuple[int, int]:
	# 9 Section
	if mode == TimeMode.SECT_9_TOP_LEFT:
		return 0 * epd.width / 3 + SECT_9_OFFSET_X, 0 * epd.height / 3 + SECT_9_OFFSET_Y
	elif mode == TimeMode.SECT_9_TOP_CENTER:
		return 1 * epd.width / 3 + SECT_9_OFFSET_X, 0 * epd.height / 3 + SECT_9_OFFSET_Y
	elif mode == TimeMode.SECT_9_TOP_RIGHT:
		return 2 * epd.width / 3 + SECT_9_OFFSET_X, 0 * epd.height / 3 + SECT_9_OFFSET_Y
	elif mode == TimeMode.SECT_9_MIDDLE_LEFT:
		return 0 * epd.width / 3 + SECT_9_OFFSET_X, 1 * epd.height / 3 + SECT_9_OFFSET_Y
	elif mode == TimeMode.SECT_9_MIDDLE_CENTER:
		return 1 * epd.width / 3 + SECT_9_OFFSET_X, 1 * epd.height / 3 + SECT_9_OFFSET_Y
	elif mode == TimeMode.SECT_9_MIDDLE_RIGHT:
		return 2 * epd.width / 3 + SECT_9_OFFSET_X, 1 * epd.height / 3 + SECT_9_OFFSET_Y
	elif mode == TimeMode.SECT_9_BOTTOM_LEFT:
		return 0 * epd.width / 3 + SECT_9_OFFSET_X, 2 * epd.height / 3 + SECT_9_OFFSET_Y
	elif mode == TimeMode.SECT_9_BOTTOM_CENTER:
		return 1 * epd.width / 3 + SECT_9_OFFSET_X, 2 * epd.height / 3 + SECT_9_OFFSET_Y
	elif mode == TimeMode.SECT_9_BOTTOM_RIGHT:
		return 2 * epd.width / 3 + SECT_9_OFFSET_X, 2 * epd.height / 3 + SECT_9_OFFSET_Y

	# 6 Section
	elif mode == TimeMode.SECT_6_TOP_LEFT:
		return 0 * epd.width / 2 + SECT_6_OFFSET_X, 0 * epd.height / 3 + SECT_6_OFFSET_Y
	elif mode == TimeMode.SECT_6_TOP_RIGHT:
		return 1 * epd.width / 2 + SECT_6_OFFSET_X, 0 * epd.height / 3 + SECT_6_OFFSET_Y
	elif mode == TimeMode.SECT_6_MIDDLE_LEFT:
		return 0 * epd.width / 2 + SECT_6_OFFSET_X, 1 * epd.height / 3 + SECT_6_OFFSET_Y
	elif mode == TimeMode.SECT_6_MIDDLE_RIGHT:
		return 1 * epd.width / 2 + SECT_6_OFFSET_X, 1 * epd.height / 3 + SECT_6_OFFSET_Y
	elif mode == TimeMode.SECT_6_BOTTOM_LEFT:
		return 0 * epd.width / 2 + SECT_6_OFFSET_X, 2 * epd.height / 3 + SECT_6_OFFSET_Y
	elif mode == TimeMode.SECT_6_BOTTOM_RIGHT:
		return 1 * epd.width / 2 + SECT_6_OFFSET_X, 2 * epd.height / 3 + SECT_6_OFFSET_Y

	# 4 Section
	elif mode == TimeMode.SECT_4_TOP_LEFT:
		return 0 * epd.width / 2 + SECT_4_OFFSET_X, 0 * epd.height / 2 + SECT_4_OFFSET_Y
	elif mode == TimeMode.SECT_4_TOP_RIGHT:
		return (
			1 * epd.width / 2 + +SECT_4_OFFSET_X,
			0 * epd.height / 2 + SECT_4_OFFSET_Y,
		)
	elif mode == TimeMode.SECT_4_BOTTOM_LEFT:
		return (
			0 * epd.width / 2 + +SECT_4_OFFSET_X,
			1 * epd.height / 2 + SECT_4_OFFSET_Y,
		)
	elif mode == TimeMode.SECT_4_BOTTOM_RIGHT:
		return (
			1 * epd.width / 2 + +SECT_4_OFFSET_X,
			1 * epd.height / 2 + SECT_4_OFFSET_Y,
		)

	# Full Screen
	elif mode == TimeMode.FULL_1:
		return 150, 100
	elif mode == TimeMode.FULL_2:
		return 88, 65
	elif mode == TimeMode.FULL_3:
		return 15, 30
	else:
		return 0, 0


def get_font(mode: TimeMode) -> FreeTypeFont:
	if mode == TimeMode.FULL_1:
		return font_full_1
	elif mode == TimeMode.FULL_2:
		return font_full_2
	elif mode == TimeMode.FULL_3:
		return font_full_3
	elif (
		mode == TimeMode.SECT_4_TOP_LEFT
		or mode == TimeMode.SECT_4_TOP_RIGHT
		or mode == TimeMode.SECT_4_BOTTOM_LEFT
		or mode == TimeMode.SECT_4_BOTTOM_RIGHT
	):
		return font_4_sect
	elif (
		mode == TimeMode.SECT_6_TOP_LEFT
		or mode == TimeMode.SECT_6_TOP_RIGHT
		or mode == TimeMode.SECT_6_MIDDLE_LEFT
		or mode == TimeMode.SECT_6_MIDDLE_RIGHT
		or mode == TimeMode.SECT_6_BOTTOM_LEFT
		or mode == TimeMode.SECT_6_BOTTOM_RIGHT
	):
		return font_6_sect
	else:
		return font_9_sect


def get_color(color: TextColor, epd) -> int:
	if color == TextColor.BLACK:
		return epd.BLACK
	elif color == TextColor.WHITE:
		return epd.WHITE
	elif color == TextColor.YELLOW:
		return epd.YELLOW
	elif color == TextColor.RED:
		return epd.RED
	elif color == TextColor.BLUE:
		return epd.BLUE
	elif color == TextColor.GREEN:
		return epd.GREEN
	else:
		logger.warning(f"Selected unknown {color=}")
		return epd.BLACK


def draw_grids(draw: ImageDraw, epd) -> None:
	# White every 10px
	for x in range(80):
		x_p: int = (x + 1) * 10
		draw.line((x_p, 0, x_p, 480), epd.WHITE, 1)
	for y in range(48):
		y_p: int = (y + 1) * 10
		draw.line((0, y_p, 800, y_p), epd.WHITE, 1)

	# Black 1/3
	draw.line((266, 0, 266, 480), epd.BLACK, 1)
	draw.line((532, 0, 532, 480), epd.BLACK, 1)
	draw.line((0, 159, 800, 159), epd.BLACK, 1)
	draw.line((0, 319, 800, 319), epd.BLACK, 1)

	# Red 1/2
	draw.line((400, 0, 400, 480), epd.RED, 1)
	draw.line((0, 240, 800, 240), epd.RED, 1)


def clear() -> int:
	try:
		from waveshare_epd.epd7in3e import EPD

		epd = EPD()
		epd.init()
		epd.clear()
		epd.sleep()
		return RETURN_CODE_SUCCESS, None

	except IOError as error:
		logger.error(msg=f"Unable to clear display. {error=}")
		return RETURN_CODE_EXCEPTION, error


def draw_time(
	time: str,
	mode: TimeMode = TimeMode.FULL_3,
	color: TextColor = TextColor.BLACK,
	shadow: TextColor = TextColor.NONE,
	draw_grid: bool = False,
) -> int:

	try:
		from waveshare_epd.epd7in3e import EPD

		epd = EPD()
		epd.init()

		#  Create Empty Screen
		img = Image.new("RGB", (epd.width, epd.height))
		draw = ImageDraw.Draw(img)

		# Debug - draw grids
		if draw_grid:
			draw_grids(draw, epd)

		# Draw time
		if mode != TimeMode.OFF and time != "":
			x, y = get_time_pos(mode, epd)
			color: int = get_color(color, epd)
			font: ImageFont = get_font(mode)

			if shadow is not TextColor.NONE:
				shadow: int = get_color(shadow, epd)
				draw.text(
					(x + SHADOW_OFFSET_X, y + SHADOW_OFFSET_Y), time, shadow, font
				)

			draw.text((x, y), time, color, font)

		# Send to display
		epd.display(epd.getbuffer(img))

		# Sleep
		epd.sleep()

		logger.debug(f"Finished drawing time")

		return RETURN_CODE_SUCCESS, None

	except IOError as error:
		logger.error(msg=f"Unable to draw time. {error=}")
		return RETURN_CODE_EXCEPTION, error


def draw_image_with_time(
	file_path: str,
	time: str,
	mode: TimeMode = TimeMode.FULL_3,
	color: TextColor = TextColor.WHITE,
	shadow: TextColor = TextColor.NONE,
	draw_grid: bool = False,
) -> int:
	try:
		from waveshare_epd.epd7in3e import EPD

		epd = EPD()
		epd.init()

		#  Create image
		img = Image.open(file_path)
		draw = ImageDraw.Draw(img)

		# Debug - draw grids
		if draw_grid:
			draw_grids(draw, epd)

		# Draw time
		if mode != TimeMode.OFF and time != "":
			x, y = get_time_pos(mode, epd)
			logger.debug(f"{x=}, {y=}")
			color: int = get_color(color, epd)
			font: ImageFont = get_font(mode)

			if shadow is not TextColor.NONE:
				shadow: int = get_color(shadow, epd)
				draw.text(
					(x + SHADOW_OFFSET_X, y + SHADOW_OFFSET_Y), time, shadow, font
				)

			draw.text((x, y), time, color, font)

		# Send to display
		epd.display(epd.getbuffer(img))

		# Sleep
		epd.sleep()

		logger.debug(f"Finish drawing image with time")

		return RETURN_CODE_SUCCESS, None

	except IOError as error:
		logger.error(msg=f"Unable to draw image with time. {error=}")
		return RETURN_CODE_EXCEPTION, error
