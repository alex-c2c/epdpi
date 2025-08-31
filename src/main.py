#!/usr/bin/python

import base64
import display
import logging
import os
import redis
import socket

from dotenv import load_dotenv
from logging import Logger, getLogger

logging.basicConfig(level=logging.DEBUG)
logger: Logger = getLogger(__name__)


load_dotenv()


def get_local_ip() -> str:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# Doesn't have to be reachable — just used to determine the default interface
		s.connect(("8.8.8.8", 80))
		ip = s.getsockname()[0]
	finally:
		s.close()

	return str(ip)


IP: str = get_local_ip()
R_CH_DRAW: str = f"epdpi_draw_{IP}"
R_CH_CLEAR: str = f"epdpi_clear_{IP}"


def is_machine_valid() -> bool:
	return "IS_RASPBERRYPI" in os.environ


def can_draw() -> bool:
	if not is_machine_valid():
		logging.error("Invalid machine")
		return False
	return True


def epd_clear() -> None:
	logging.info(f"epd_clear")

	if not can_draw():
		return

	display.clear()


def epd_draw(buffer: list[int]) -> None:
	logging.info(f"epd_draw")

	if not can_draw():
		return

	display.draw(buffer)


def redis_event_handler(msg: dict[str, str]) -> None:
	logger.info(f"[redis_event_handler] ", msg)
	
	if msg["type"] != "message" or msg["channel"] != f"{R_CH_DRAW}":
		return

	if msg["channel"] == R_CH_DRAW:
		data: str = msg["data"]
		decoded_bytes: bytes = base64.b64decode(data)
		buffer: list[int] = list(decoded_bytes)
		epd_draw(buffer)

	elif msg["channel"] == R_CH_CLEAR:
		data: str = msg["data"]
		if data == "clear":
			epd_clear()


def redis_exception_handler(ex, pubsub, thread) -> None:
	logging.error(f"{ex=}")
	thread.stop()
	thread.join(timeout=1.0)
	pubsub.close()


if __name__ == "__main__":
	# Initialize Redis
	redis_client = redis.Redis(
		host="localhost",
		port=6379,
		password=os.getenv("REDIS_PASSWORD"),
		decode_responses=True,
	)
	redis_pubsub = redis_client.pubsub()
	redis_pubsub.subscribe(**{f"{R_CH_DRAW}": redis_event_handler})
	redis_pubsub.subscribe(**{f"{R_CH_CLEAR}": redis_event_handler})
	redis_thread = redis_pubsub.run_in_thread(
		sleep_time=1, exception_handler=redis_exception_handler
	)
	redis_thread.name = "redis pubsub thread"
