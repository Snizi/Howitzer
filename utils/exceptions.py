

class HowitzerException(Exception):
    pass


class ConfigurationError(HowitzerException):
    pass


class BurpXMLError(HowitzerException):
    pass


class HTTPClientError(HowitzerException):
    pass


class ProfileValidationError(HowitzerException):
    pass


class ParseError(HowitzerException):
    pass


class MatchDetectionError(HowitzerException):
    pass
