import os

from logging import Logger, getLogger
import sys


logger: Logger = getLogger(__name__)


DIR_LIB: str = os.path.join(
	os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(DIR_LIB):
	sys.path.append(DIR_LIB)
	logger.info(f"{sys.path=}")	
	


def draw(buffer: list[int]) -> bool:
	logger.info(f"drawing display")

	try:
		from waveshare_epd.epd7in3e import EPD

		epd = EPD()
		epd.init()

		# Send to display
		epd.display(buffer)

		# Sleep
		epd.sleep()

		logger.info(f"draw finish")

		return True

	except Exception as error:
		logger.error(msg=f"Unable to draw buffer. {error=}")
		return False


def clear() -> bool:
	logger.info(f"clearing display")

	try:
		from waveshare_epd.epd7in3e import EPD

		# Init
		epd = EPD()
		epd.init()

		# Clear display
		epd.clear()

		# Sleep
		epd.sleep()

		logger.info(f"clear finish")

		return True

	except IOError as error:
		logger.error(msg=f"Unable to clear display. {error=}")
		return False
