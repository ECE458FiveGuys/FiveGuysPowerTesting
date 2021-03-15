from enum import auto
from database.enums import AutoName


class PermissionGroupEnum(AutoName):
    UNPRIVILEGED = auto()
    INSTRUMENT_MANAGEMENT = auto()
    MODEL_MANAGEMENT = auto()
    CALIBRATION = auto()
    ADMINISTRATOR = auto()


class UserEnum(AutoName):
    PK = auto()
    USERNAME = auto()
    PASSWORD = auto()
    NAME = auto()
    EMAIL = auto()
    IS_ACTIVE = auto()
    IS_STAFF = auto()
    IS_SUPERUSER = auto()
    GROUPS = auto()
