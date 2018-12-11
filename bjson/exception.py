class BJsonBaseError(Exception):
    pass


class BJsonEncodeError(BJsonBaseError):
    pass


class BJsonDecodeError(BJsonBaseError):
    pass


class BJsonVersionError(BJsonBaseError):
    pass


__all__ = [
    "BJsonBaseError",
    "BJsonEncodeError",
    "BJsonDecodeError",
    "BJsonVersionError",
]
