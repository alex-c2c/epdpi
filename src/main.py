#!/usr/bin/python

import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv("ID") is None:   
	logging.error("Missing var \"ID\" in .env")
	exit(-1)
	
import redis
import logging
import display

from consts import *
from logging import Logger, getLogger

logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


def is_machine_valid() -> bool:
	return "IS_RASPBERRYPI" in os.environ


def redis_publish(key: str, *args) -> None:
	global redis_client

	id: str = os.getenv("ID")
	if len(args) > 0:
		msg: str = f"{id}^{key}^{'^'.join(args)}"
	else:
		msg: str = f"{id}^{key}"

	logging.info(f"redis_publish {R_CH_PUB=} {msg=}")
	redis_client.publish(R_CH_PUB, msg)


def set_epd_busy(busy: bool) -> None:
	os.environ[EPD_BUSY] = "1" if busy else "0"


def get_epd_busy() -> bool:
	return False if os.environ.get(EPD_BUSY, "0") == "0" else True


def can_draw() -> bool:
	if not is_machine_valid():
		logging.warning("Invalid machine")
		redis_publish(
			R_MSG_RESULT,
			R_MSG_CLEAR,
			f"{RETURN_CODE_INVALID_MACHINE}",
			"Invalid machine.",
		)
		return False

	if get_epd_busy():
		logging.warning("EPD is busy")
		redis_publish(
			R_MSG_RESULT,
			R_MSG_CLEAR,
			f"{RETURN_CODE_EPD_BUSY}",
			"E-Paper display is busy.",
		)
		return False
	
	return True


def epd_clear() -> None:
	logging.info(f"epd_clear")

	if not can_draw():
		return

	set_epd_busy(True)

	result, error = display.clear()

	set_epd_busy(False)

	if result == RETURN_CODE_SUCCESS:
		redis_publish(R_MSG_RESULT, R_MSG_CLEAR, f"{RETURN_CODE_SUCCESS}")
	else:
		redis_publish(R_MSG_RESULT, R_MSG_CLEAR, f"{RETURN_CODE_EXCEPTION}", f"{error}")


def epd_draw(buffer:list[int]) -> None:
	logging.info(f"epd_draw")

	if not can_draw():
		return

	set_epd_busy(True)
	
	result, error = display.draw(buffer)

	set_epd_busy(False)

	if result == RETURN_CODE_SUCCESS:
		redis_publish(R_MSG_RESULT, R_MSG_DRAW, f"{RETURN_CODE_SUCCESS}")
	else:
		redis_publish(R_MSG_RESULT, R_MSG_DRAW, f"{RETURN_CODE_EXCEPTION}", f"{error}")


def redis_event_handler(msg: dict[str, str]) -> None:
	logging.info(f"Received redis {msg=}")

	if msg["type"] != "message" or msg["channel"] != f"{R_CH_SUB}":
		return

	data: list[str] = msg["data"].split("^")

	if data[0] == R_MSG_CLEAR:
		epd_clear()

	elif data[0] == R_MSG_DRAW:
		buffer: list[int] = list(int(e) for e in data[1].split(":"))
		
		epd_draw(buffer)
		

def redis_exception_handler(ex, pubsub, thread) -> None:
	logging.error(f"{ex=}")
	thread.stop()
	thread.join(timeout=1.0)
	pubsub.close()


if __name__ == "__main__":
	# Set epd_busy to FALSE by default
	set_epd_busy(False)

	# Initialize Redis
	redis_client = redis.Redis(host="localhost", port=6379, password=os.getenv("REDIS_PASSWORD"), decode_responses=True)
	redis_pubsub = redis_client.pubsub()
	redis_pubsub.subscribe(**{f"{R_CH_SUB}": redis_event_handler})
	redis_thread = redis_pubsub.run_in_thread(
		sleep_time=1, exception_handler=redis_exception_handler
	)
	redis_thread.name = "redis pubsub thread"
