import os

from logging import Logger, getLogger
import sys


log: Logger = getLogger(__name__)


DIR_LIB: str = os.path.join(
	os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(DIR_LIB):
	sys.path.append(DIR_LIB)


def draw(buffer: list[int]) -> bool:
	log.info(f"draw {buffer=}")

	try:
		from waveshare_epd.epd7in3e import EPD

		epd = EPD()
		epd.init()

		# Send to display
		epd.display(buffer)

		# Sleep
		epd.sleep()

		log.info(f"draw finish")

		return True

	except Exception as error:
		log.error(msg=f"Unable to draw buffer. {error=}")
		return False


def clear() -> bool:
	log.info(f"clear")

	try:
		from waveshare_epd.epd7in3e import EPD

		# Init
		epd = EPD()
		epd.init()

		# Clear display
		epd.clear()

		# Sleep
		epd.sleep()

		log.info(f"clear finish")

		return True

	except IOError as error:
		log.error(msg=f"Unable to clear display. {error=}")
		return False
