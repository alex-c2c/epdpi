#!/usr/bin/python

import redis
import logging

from consts import *
from display import clear, draw_time, draw_image_with_time
from mybutton import MyButton
from logging import Logger, getLogger


logging.basicConfig(level=logging.INFO)
logger: Logger = getLogger(__name__)


def is_machine_valid() -> bool:
    return "IS_RASPBERRYPI" in os.environ


def redis_publish(key: str, *args) -> None:
    global redis_client

    if len(args) > 0:
        msg: str = f"{key}^{'^'.join(args)}"
    else:
        msg: str = f"{key}"

    logging.info(f"redis_publish {CHANNEL_CLOCKPI=} {msg=}")
    redis_client.publish(CHANNEL_CLOCKPI, msg)


def set_epd_busy(busy: bool) -> None:
    global redis_client

    logging.info(f"Settings EPD {busy=}")
    redis_client.set(SETTINGS_EPD_BUSY, "1" if busy else "0")
    redis_publish(MSG_BUSY, MSG_UPDATED)


def get_epd_busy() -> bool:
    global redis_client

    busy: bool = True if redis_client.get(SETTINGS_EPD_BUSY) == "1" else False
    logging.info(f"Getting EPD {busy=}")
    return busy


def epd_clear() -> None:
    logging.debug(f"Attempting to clear display")

    if not is_machine_valid():
        logging.warning("Invalid machine")
        redis_publish(
            MSG_RESULT, MSG_CLEAR, f"{RETURN_CODE_INVALID_MACHINE}", "Invalid machine."
        )
        return

    if get_epd_busy():
        logging.warning("EPD is busy")
        redis_publish(
            MSG_RESULT, MSG_CLEAR, f"{RETURN_CODE_EPD_BUSY}", "E-Paper display is busy."
        )
        return

    set_epd_busy(True)

    logging.info(f"Clearing display")
    result, error = clear()
    logging.info(f"Finished clearing display")

    set_epd_busy(False)

    if result == RETURN_CODE_SUCCESS:
        redis_publish(MSG_RESULT, MSG_CLEAR, f"{RETURN_CODE_SUCCESS}")
    else:
        redis_publish(MSG_RESULT, MSG_CLEAR, f"{RETURN_CODE_EXCEPTION}", f"{error}")


def epd_draw(
    file_path: str,
    time: str,
    mode: TimeMode,
    color: TextColor,
    shadow: TextColor,
    draw_grids: bool,
) -> None:
    logging.debug(f"Attempting to draw")
    if not is_machine_valid():
        logging.warning(f"Unable to draw on an invalid machine")
        redis_publish(
            MSG_RESULT, MSG_DRAW, f"{RETURN_CODE_INVALID_MACHINE}", "Invalid machine."
        )
        return

    if get_epd_busy():
        logging.warning(f"Unable to draw as EPD is busy")
        redis_publish(
            MSG_RESULT, MSG_DRAW, f"{RETURN_CODE_EPD_BUSY}", "E-Paper display is busy."
        )
        return

    set_epd_busy(True)

    if file_path == "":
        logging.debug(f"Drawing time")
        result, error = draw_time(time, mode, color, shadow, draw_grids)
        logging.debug((f"Finished drawing time"))

    else:
        logging.debug(f"Drawing image with time")
        result, error = draw_image_with_time(
            file_path, time, mode, color, shadow, draw_grids
        )
        logging.debug(f"Finished drawing image with time")

    set_epd_busy(False)

    if result == RETURN_CODE_SUCCESS:
        redis_publish(MSG_RESULT, MSG_DRAW, f"{RETURN_CODE_SUCCESS}")
    else:
        redis_publish(MSG_RESULT, MSG_DRAW, f"{RETURN_CODE_EXCEPTION}", f"{error}")


def redis_event_handler(msg: dict[str, str]) -> None:
    logging.info(f"Received redis {msg=}")

    if msg["type"] != "message" or msg["channel"] != CHANNEL_EPDPI:
        return

    data: list[str] = msg["data"].split("^")

    if data[0] == MSG_CLEAR:
        epd_clear()

    elif data[0] == MSG_DRAW:
        file_path: str = data[1]
        time: str = data[2]
        mode: TimeMode = TimeMode(int(data[3]))
        color: TextColor = TextColor(int(data[4]))
        shadow: TextColor = TextColor(int(data[5]))
        draw_grids: bool = True if data[6] == "1" else False

        epd_draw(file_path, time, mode, color, shadow, draw_grids)


def redis_exception_handler(ex, pubsub, thread) -> None:
    logging.error(f"{ex=}")
    thread.stop()
    thread.join(timeout=1.0)
    pubsub.close()


def btn_cb_next_img() -> None:
    logging.info(f"Button Next Pressed")
    redis_publish(MSG_BTN, MSG_BTN_NEXT)


def btn_cb_prev_img() -> None:
    logging.info(f"Button Previous Pressed")
    redis_publish(MSG_BTN, MSG_BTN_PREV)


def btn_cb_change_mode() -> None:
    logging.info(f"Button Change Mode Pressed()")
    redis_publish(MSG_BTN, MSG_BTN_CHANGE)


btn_next_img = MyButton(2, btn_cb_next_img)
btn_prev_img = MyButton(3, btn_cb_prev_img)
btn_change_mode = MyButton(5, btn_cb_change_mode)


redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
redis_pubsub = redis_client.pubsub()
redis_pubsub.subscribe(**{f"{CHANNEL_EPDPI}": redis_event_handler})
redis_thread = redis_pubsub.run_in_thread(
    sleep_time=1, exception_handler=redis_exception_handler
)
redis_thread.name = "redis pubsub thread"


"""
if __name__ == "__main__":
    while True:
        time.sleep(1.0)
"""
