from enum import Enum

# CadQuery centering constants for common options - (width, depth, height)
center_w = (True, False, False)
center_wd = (True, True, False)
center_wh = (True, False, True)


class LogLevel(Enum):
    TRACE = 0
    DEBUG = 10
    INFO = 20
    ERROR = 30
