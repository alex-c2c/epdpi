import logging
import time

from gpiozero import Button
from consts import *
from display import clear_display, draw_time, draw_image_with_time


logging.basicConfig(level=logging.DEBUG)


button1 = Button(2)
button2 = Button(3)
button3 = Button(5)


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


while True:
    if button1.is_pressed:
        logging.debug(f"Button 1 pressed")
    elif button2.is_pressed:
        logging.debug(f"Button 2 pressed")
    elif button3.is_pressed:
        logging.debug(f"Button 3 pressed")

    time.sleep(0.1)