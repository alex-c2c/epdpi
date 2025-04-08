import logging
import time
import redis

from gpiozero import Button
from consts import *
from display import clear, draw_time, draw_image_with_time

logging.basicConfig(level=logging.DEBUG)

button1 = Button(2)
button2 = Button(3)
button3 = Button(5)

def is_machine_valid() -> bool:
    return "IS_RASPBERRYPI" in os.environ


def set_epd_busy(busy: bool) -> None:
    logging.debug(f"Settings EPD {busy=}")
    os.environ["epd_busy"] = "1" if busy else "0"
    redis_publish("busy", os.environ.get("epd_busy"))


def get_epd_busy() -> bool:
    busy: bool = True if os.environ.get("epd_busy") == "1" else False
    logging.debug(f"Getting EPD {busy=}")
    return busy


def epd_clear() -> None:
    logging.debug(f"Attempting to clear display")

    if not is_machine_valid():
        logging.warning("Invalid machine")
        redis_publish("result", "clear", f"{RETURN_CODE_INVALID_MACHINE}", "Invalid machine.")

    if get_epd_busy():
        logging.warning("EPD is busy")
        redis_publish("result", "clear", f"{RETURN_CODE_EPD_BUSY}", "E-Paper display is busy.")
    
    set_epd_busy(True)
    result, error = clear()
    set_epd_busy(False)
    
    logging.debug(f"Finished clearing display")
    
    if result == RETURN_CODE_SUCCESS:
        redis_publish("result", "draw", f"{RETURN_CODE_SUCCESS}")
    else:
        redis_publish("result", "draw", f"{RETURN_CODE_EXCEPTION}", f"{error}")
    

def epd_draw(file_path:str, time:str, mode: TimeMode, color: int, shadow: int, draw_grids: bool) -> None:
    if not is_machine_valid():
        logging.warning(f"Invalid machine")
        redis_publish("result", "draw", f"{RETURN_CODE_INVALID_MACHINE}", "Invalid machine.")
        return

    if get_epd_busy():
        logging.warning(f"EPD is busy")
        redis_publish("result", "draw", f"{RETURN_CODE_EPD_BUSY}", "E-Paper display is busy.")
        return
    
    set_epd_busy(True)

    if file_path == "":
        logging.debug(msg=f"Attempting to draw time")
        result, error = draw_time(time, mode, color, shadow, draw_grids)
        logging.debug((f"Finished drawing time"))
    
    else:
        logging.debug(msg=f"Attempting to draw image with time")
        result, error = draw_image_with_time(file_path, time, mode, color, shadow, draw_grids)
        logging.debug(f"Finished drawing image with time")

    set_epd_busy(False)
    
    if result == RETURN_CODE_SUCCESS:
        redis_publish("result", "draw", f"{RETURN_CODE_SUCCESS}")
    else:
        redis_publish("result", "draw", f"{RETURN_CODE_EXCEPTION}", f"{error}")
    

def redis_event_handler(msg: dict[str, str]) -> None:
    logging.debug(f"redis_event_handler {msg=}")
    
    if msg["type"] != "message" or msg["channel"] != CHANNEL_EPDPI:
        return

    data: list[str] = msg["data"].split("^")

    if data[0] == MSG_CLEAR:
        epd_clear()

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


def redis_exception_handler(ex, pubsub, thread) -> None:
    logging.error(f"{ex=}")
    thread.stop()
    thread.join(timeout=1.0)
    pubsub.close()


def redis_publish(key: str, *args) -> None:
    msg: str = f"{key}^{'^'.join(args)}"
    logging.debug(f"redis_publish {CHANNEL_CLOCKPI=} {msg=}")
    redis_client.publish(CHANNEL_CLOCKPI, msg)
        

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
redis_pubsub = redis_client.pubsub()
redis_pubsub.subscribe(**{f"{CHANNEL_EPDPI}": redis_event_handler})
redis_thread = redis_pubsub.run_in_thread(
    sleep_time=1, exception_handler=redis_exception_handler
)
redis_thread.name = "redis pubsub thread"


if __name__ == "__main__":
    while True:
        if button1.is_pressed:
            logging.debug(f"Button 1 pressed")
        elif button2.is_pressed:
            logging.debug(f"Button 2 pressed")
        elif button3.is_pressed:
            logging.debug(f"Button 3 pressed")
