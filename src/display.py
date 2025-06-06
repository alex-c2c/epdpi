import os

from logging import Logger, getLogger
import sys
from consts import *


log: Logger = getLogger(__name__)


DIR_LIB: str = os.path.join(
	os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(DIR_LIB):
	sys.path.append(DIR_LIB)


def draw(buffer:list[int]) -> tuple[int, str]:
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

		return RETURN_CODE_SUCCESS, None

	except Exception as error:
		log.error(msg=f"Unable to draw buffer. {error=}")
		return RETURN_CODE_EXCEPTION, error


def clear() -> tuple[int, str]:
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
  
		return RETURN_CODE_SUCCESS, None

	except IOError as error:
		log.error(msg=f"Unable to clear display. {error=}")
		return RETURN_CODE_EXCEPTION, error
