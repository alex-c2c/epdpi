import argparse
import os
import sys
import logging
import redis
import time
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from consts import *
from gpiozero import Button


logging.basicConfig(level=logging.DEBUG)


DIR_FONT: str = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "font"
)
DIR_LIB: str = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(DIR_LIB):
    sys.path.append(DIR_LIB)


logging.debug(f"{DIR_FONT=}")
logging.debug(f"{DIR_LIB=}")


button1 = Button(2)
button2 = Button(3)
button3 = Button(5)


font_9_sect = ImageFont.truetype(os.path.join("font", "Roboto-Bold.ttf"), 80)
font_6_sect = ImageFont.truetype(os.path.join("font", "Roboto-Bold.ttf"), 130)
font_4_sect = ImageFont.truetype(os.path.join("font", "Roboto-Bold.ttf"), 130)

font_full_1 = ImageFont.truetype(os.path.join("font", "Roboto-Bold.ttf"), 200)
font_full_2 = ImageFont.truetype(os.path.join("font", "Roboto-Bold.ttf"), 250)
font_full_3 = ImageFont.truetype(os.path.join("font", "Roboto-Bold.ttf"), 300)


def is_machine_valid() -> bool:
    return "IS_RASPBERRYPI" in os.environ


def redis_event_handler(msg: dict[str, str]) -> None:
    if msg["type"] != "message" or msg["channel"] != CHANNEL_EPDPI:
        return

    data: list[str] = msg["data"].split("^")

    if data[0] == MSG_CLEAR:
        clear_display()

    elif data[0] == MSG_DRAW:
        file_path: str = data[1]
        time: str = data[2]
        mode: TimeMode = TimeMode(int(data[3]))
        color: int = int(data[4])
        shadow: int = int(data[5])
        draw_grids: bool = True if data[6] == "1" else False

        if file_path == "":
            draw_time(time, mode, color, shadow, draw_grids)
        else:
            draw_image_with_time(file_path, time, mode, color, shadow, draw_grids)


def redis_exception_handler(ex, pubsub, thread):
    logging.error(f"{ex=}")
    thread.stop()
    thread.join(timeout=1.0)
    pubsub.close()


redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
redis_pubsub = redis_client.pubsub()
redis_pubsub.subscribe(**{f"{CHANNEL_EPDPI}": redis_event_handler})
redis_thread = redis_pubsub.run_in_thread(
    sleep_time=1, exception_handler=redis_exception_handler
)
redis_thread.name = "redis pubsub thread"


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
        return 20, 30
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


def get_color(color: int, epd) -> int:
    if color == COLOR_BLACK:
        return epd.BLACK
    elif color == COLOR_WHITE:
        return epd.WHITE
    elif color == COLOR_YELLOW:
        return epd.YELLOW
    elif color == COLOR_RED:
        return epd.RED
    elif color == COLOR_BLUE:
        return epd.BLUE
    elif color == COLOR_GREEN:
        return epd.GREEN
    else:
        logging.warning(f"Selected unknown {color=}")
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


def update_epd_busy(busy: bool) -> None:
    logging.debug(f"Settings EPD {busy=}")
    value: str = "1" if busy else "0"
    os.environ["epd_busy"] = value
    redis_client.publish(CHANNEL_CLOCKPI, f"busy^{value}")


def get_epd_busy() -> bool:
    busy: bool = True if os.environ.get("epd_busy") == "1" else False
    logging.debug(f"Getting EPD {busy=}")
    return busy


def clear_display() -> int:
    logging.debug(f"Attempting to clear display")

    if not is_machine_valid():
        logging.warning("Invalid machine")
        return RETURN_CODE_INVALID_MACHINE

    if get_epd_busy():
        logging.warning("EPD is busy")
        return RETURN_CODE_EPD_BUSY

    try:
        update_epd_busy(True)

        from waveshare_epd.epd7in3e import EPD

        epd = EPD()
        epd.init()
        epd.clear()
        epd.sleep()

        update_epd_busy(False)

        logging.debug(f"Finished clearing display")

        return RETURN_CODE_SUCCESS

    except IOError as e:
        logging.error(e)
        update_epd_busy(False)
        return RETURN_CODE_EXCEPTION


def draw_time(
    time: str,
    mode: TimeMode = TimeMode.FULL_3,
    color: int = COLOR_BLACK,
    shadow: int = COLOR_NONE,
    draw_grid: bool = False,
) -> int:
    logging.debug(f"Attempting to draw time")

    if not is_machine_valid():
        logging.warning(f"Invalid machine")
        return RETURN_CODE_INVALID_MACHINE

    if get_epd_busy():
        logging.warning(f"EPD is busy")
        return RETURN_CODE_EPD_BUSY

    try:
        update_epd_busy(True)

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

            if shadow is not COLOR_NONE:
                shadow: int = get_color(shadow, epd)
                draw.text(
                    (x + SHADOW_OFFSET_X, y + SHADOW_OFFSET_Y), time, shadow, font
                )

            draw.text((x, y), time, color, font)

        # Send to display
        epd.display(epd.getbuffer(img))

        # Sleep
        epd.sleep()

        update_epd_busy(False)

        logging.debug(f"Finished drawing time")

        return RETURN_CODE_SUCCESS

    except IOError as e:
        update_epd_busy(False)
        logging.error(e)
        return RETURN_CODE_EXCEPTION


def draw_image_with_time(
    file_path: str,
    time: str,
    mode: TimeMode = TimeMode.FULL_3,
    color: int = COLOR_WHITE,
    shadow: int = COLOR_NONE,
    draw_grid: bool = False,
) -> int:
    logging.debug(f"Attempting to draw image with time")

    if not is_machine_valid():
        logging.warning(f"Invalid machine")
        return RETURN_CODE_INVALID_MACHINE

    if get_epd_busy():
        logging.warning(f"EPD is busy")
        return RETURN_CODE_EPD_BUSY

    try:
        update_epd_busy(True)

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
            logging.debug(f"{x=}, {y=}")
            color: int = get_color(color, epd)
            font: ImageFont = get_font(mode)

            if shadow is not COLOR_NONE:
                shadow: int = get_color(shadow, epd)
                draw.text(
                    (x + SHADOW_OFFSET_X, y + SHADOW_OFFSET_Y), time, shadow, font
                )

            draw.text((x, y), time, color, font)

        # Send to display
        epd.display(epd.getbuffer(img))

        # Sleep
        epd.sleep()

        update_epd_busy(False)

        logging.debug(f"Finish drawing image with time")

        return RETURN_CODE_SUCCESS

    except IOError as e:
        update_epd_busy(False)
        logging.error(e)
        return RETURN_CODE_EXCEPTION


while True:
    if button1.is_pressed:
        logging.debug(f"Button 1 pressed")
    elif button2.is_pressed:
        logging.debug(f"Button 2 pressed")
    elif button3.is_pressed:
        logging.debug(f"Button 3 pressed")

    time.sleep(0.1)


"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="EPD",
        description="Draws to E-Paper 7\"3 E6 Display\n\
                    --image: if empty or invalid, no images will be drawn.\n\
                    --time: If empty of invalid, no time will drawn.\n\
                    --mode: default=FULL_SCREEN_3.\n\
                    --color: default=WHITE.\n\
                    --shadow: default-BLACK.\n\
                    --grid: If included, draw grids to display\n\
                    --off: If included, clear screen, overwrites all other options."
    )
    parser.add_argument("-i", "--image", type=str, help="<Optional> Path to image file, accepted extension: *.bmp", default="", required=False)
    parser.add_argument("-t", "--time", type=str, help="<Optional> Display time, accepted format is 'HH:MM'", default="", required=False)
    parser.add_argument("-m", "--mode", type=int, help="<Optional> Set text display mode", default=TimeMode.FULL_3, required=False)
    parser.add_argument("-c", "--color", type=int, help="<Optional> Set text color", default=2, required=False)
    parser.add_argument("-s", "--shadow", type=int, help="<Optional> Set text shadow color", default=1, required=False)
    parser.add_argument("-g", "--grid", help="<Optional> Draw grids on screen", action="store_true",required=False)
    parser.add_argument("-o", "--off", help="<Optional> Clear screen. This option over writes all other options", action="store_true", required=False)

    args = parser.parse_args()
    
    if args.test:
        busy:bool = get_epd_busy()
        
        logging.debug(f"get_epd_busy() - {busy=}")
        
        exit(RETURN_CODE_SUCCESS)
    
    if args.off:
        result:int = clear_display()
        exit(result)
    
    image_path:str = args.image
    if not os.path.isfile(image_path) or image_path.rsplit(".", 1)[1] not in ALLOWED_EXTENSIONS:
        image_path = ""
        
    time:str = args.time
    if len(time) != 5 or time[2] != ':':
        time = ""
        
    mode:TimeMode = TimeMode(args.mode)
    color:int = args.color
    shadow:int = args.shadow
    draw_grids:bool = args.grid
    
    result:int = 0
    if image_path == "":
        result = draw_time(time, mode, color, shadow, draw_grids)
    else:
        result = draw_image_with_time(image_path, time, mode, color, shadow, draw_grids)
    
    exit(result)
"""
