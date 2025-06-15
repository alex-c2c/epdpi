import os
    
"""
REDIS
"""
R_CH_PUB: str = f"epdpi{os.getenv("ID")}_clockpi"
R_CH_SUB: str = f"clockpi_epdpi{os.getenv("ID")}"

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
