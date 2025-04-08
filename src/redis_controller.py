import redis
import logging
from main import redis_event_handler
from consts import *


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