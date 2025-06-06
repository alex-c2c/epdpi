#!/usr/bin/python

import redis
import logging
import image
import display

from consts import *
from logging import Logger, getLogger


logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


def is_machine_valid() -> bool:
	return "IS_RASPBERRYPI" in os.environ


def redis_publish(key: str, *args) -> None:
	global redis_client

	if len(args) > 0:
		msg: str = f"{key}^{'^'.join(args)}"
	else:
		msg: str = f"{key}"

	logging.info(f"redis_publish {R_CHANNEL_CLOCKPI=} {msg=}")
	redis_client.publish(R_CHANNEL_CLOCKPI, msg)


def set_epd_busy(busy: bool) -> None:
	global redis_client

	logging.info(f"Settings EPD {busy=}")
	redis_client.set(R_SETTINGS_EPD_BUSY, "1" if busy else "0")
	redis_publish(R_MSG_BUSY, R_MSG_UPDATED)


def get_epd_busy() -> bool:
	global redis_client

	busy: bool = True if redis_client.get(R_SETTINGS_EPD_BUSY) == "1" else False
	logging.info(f"Getting EPD {busy=}")
	return busy


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


def epd_draw_image(
	file_path: str | None,
	time: str,
	mode: TimeMode,
	color: TextColor,
	shadow: TextColor,
	draw_grids: bool,
) -> None:
	logging.info(f"epd_draw_image")
 
	if not can_draw():
		return

	img = image.process_image(file_path, time, mode, color, shadow, draw_grids)
	buffer: list[int] = image.convert_image_to_buffer(img)

	set_epd_busy(True)
	
	result, error = display.draw(buffer)

	set_epd_busy(False)

	if result == RETURN_CODE_SUCCESS:
		redis_publish(R_MSG_RESULT, R_MSG_DRAW, f"{RETURN_CODE_SUCCESS}")
	else:
		redis_publish(R_MSG_RESULT, R_MSG_DRAW, f"{RETURN_CODE_EXCEPTION}", f"{error}")
  

def epd_draw_buffer(
	buffer:list[int]
) -> None:
	logging.info(f"epd_draw_buffer")
 
	if not can_draw():
		return

	set_epd_busy(True)
	
	result, error = display.draw(buffer)

	set_epd_busy(False)

	if result == RETURN_CODE_SUCCESS:
		redis_publish(R_MSG_RESULT, R_MSG_DRAW_BUFFER, f"{RETURN_CODE_SUCCESS}")
	else:
		redis_publish(R_MSG_RESULT, R_MSG_DRAW_BUFFER, f"{RETURN_CODE_EXCEPTION}", f"{error}")


def redis_event_handler(msg: dict[str, str]) -> None:
	logging.info(f"Received redis {msg=}")

	if msg["type"] != "message" or msg["channel"] != R_CHANNEL_EPDPI:
		return

	data: list[str] = msg["data"].split("^")

	if data[0] == R_MSG_CLEAR:
		epd_clear()

	elif data[0] == R_MSG_DRAW:
		file_path: str | None = None if data[1] == "" or not os.path.isfile(data[1]) else data[1]
		time: str = data[2]
		mode: TimeMode = TimeMode(int(data[3]))
		color: TextColor = TextColor(int(data[4]))
		shadow: TextColor = TextColor(int(data[5]))
		draw_grids: bool = True if data[6] == "1" else False

		epd_draw_image(file_path, time, mode, color, shadow, draw_grids)
  
	elif data[0] == R_MSG_DRAW_BUFFER:
		buffer: list[int] = list(int(e) for e in data[1].split(":"))
		
		epd_draw_buffer(buffer)
		

def redis_exception_handler(ex, pubsub, thread) -> None:
	logging.error(f"{ex=}")
	thread.stop()
	thread.join(timeout=1.0)
	pubsub.close()


redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
redis_pubsub = redis_client.pubsub()
redis_pubsub.subscribe(**{f"{R_CHANNEL_EPDPI}": redis_event_handler})
redis_thread = redis_pubsub.run_in_thread(
	sleep_time=1, exception_handler=redis_exception_handler
)
redis_thread.name = "redis pubsub thread"

# Reset "epd_busy" to False during startup
set_epd_busy(False)
