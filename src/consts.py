"""
REDIS
"""
R_CHANNEL_CLOCKPI: str = "clockpi"
R_CHANNEL_EPDPI: str = "epdpi"

R_MSG_CLEAR: str = "clear"
R_MSG_DRAW: str = "draw"
R_MSG_BUSY: str = "busy"
R_MSG_UPDATED: str = "updated"
R_MSG_RESULT: str = "result"

R_SETTINGS_EPD_BUSY: str = "epd_busy"


"""
RETURN CODE
"""
RETURN_CODE_SUCCESS = 0
RETURN_CODE_INVALID_MACHINE = -1
RETURN_CODE_EPD_BUSY = -2
RETURN_CODE_EXCEPTION = -3
