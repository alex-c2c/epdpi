import redis
import logging
from .main import clear_display, draw_image_with_time, draw_time
from .consts import *


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


def redis_exception_handler(ex, pubsub, thread) -> None:
    logging.error(f"{ex=}")
    thread.stop()
    thread.join(timeout=1.0)
    pubsub.close()


def publish_epd_busy(busy:bool) -> None:
    redis_client.publish(CHANNEL_CLOCKPI, f'busy^{"1" if busy else "0"}')


redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
redis_pubsub = redis_client.pubsub()
redis_pubsub.subscribe(**{f"{CHANNEL_EPDPI}": redis_event_handler})
redis_thread = redis_pubsub.run_in_thread(
    sleep_time=1, exception_handler=redis_exception_handler
)
redis_thread.name = "redis pubsub thread"