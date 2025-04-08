from enum import Enum
import os
import tempfile

# Redis
CHANNEL_CLOCKPI: str = "clockpi"
CHANNEL_EPDPI: str = "epdpi"
MSG_CLEAR: str = "clear"
MSG_DRAW: str = "draw"

# Allowed extensions for drawing
ALLOWED_EXTENSIONS: set[str] = "bmp"

# Tmp directory
TMP_FILE_PATH: str = os.path.join(tempfile.gettempdir(), "clockpi_temp")

# Return code
RETURN_CODE_SUCCESS = 0
RETURN_CODE_INVALID_MACHINE = -1
RETURN_CODE_EPD_BUSY = -2
RETURN_CODE_EXCEPTION = -3

# Offsets
SHADOW_OFFSET_X: int = -5
SHADOW_OFFSET_Y: int = 5

SECT_9_OFFSET_X: int = 33
SECT_9_OFFSET_Y: int = 25

SECT_6_OFFSET_X: int = 30
SECT_6_OFFSET_Y: int = -10

SECT_4_OFFSET_X: int = 30
SECT_4_OFFSET_Y: int = 30

# Colors
COLOR_NONE: int = 0
COLOR_BLACK: int = 1
COLOR_WHITE: int = 2
COLOR_YELLOW: int = 3
COLOR_RED: int = 4
COLOR_BLUE: int = 5
COLOR_GREEN: int = 6


# Time Mode
class TimeMode(Enum):
    OFF = 0
    SECT_9_TOP_LEFT = 1
    SECT_9_TOP_CENTER = 2
    SECT_9_TOP_RIGHT = 3
    SECT_9_MIDDLE_LEFT = 4
    SECT_9_MIDDLE_CENTER = 5
    SECT_9_MIDDLE_RIGHT = 6
    SECT_9_BOTTOM_LEFT = 7
    SECT_9_BOTTOM_CENTER = 8
    SECT_9_BOTTOM_RIGHT = 9
    SECT_6_TOP_LEFT = 10
    SECT_6_TOP_RIGHT = 11
    SECT_6_MIDDLE_LEFT = 12
    SECT_6_MIDDLE_RIGHT = 13
    SECT_6_BOTTOM_LEFT = 14
    SECT_6_BOTTOM_RIGHT = 15
    SECT_4_TOP_LEFT = 16
    SECT_4_TOP_RIGHT = 17
    SECT_4_BOTTOM_LEFT = 18
    SECT_4_BOTTOM_RIGHT = 19
    FULL_1 = 20  # Small
    FULL_2 = 21  # Medium
    FULL_3 = 22  # Large
    MAX = FULL_3 + 1
