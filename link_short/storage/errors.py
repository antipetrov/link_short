
class ShortCodeStorageError(Exception):
    pass

class ShortCodeStorageCreateError(ShortCodeStorageError):
    pass


class ShortCodeStorageConfigError(ShortCodeStorageError):
    pass


class ShortCodeStorageDeleteError(ShortCodeStorageError):
    pass


class ShortCodeNotFound(ShortCodeStorageError):
    pass


class ShortCodeDecodeError(Exception):
    pass

class ShortCodeStatSaveError(Exception):
    pass

