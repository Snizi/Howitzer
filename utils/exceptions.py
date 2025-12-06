"""
Custom exception hierarchy for the Howitzer security testing tool.

Provides structured error handling with specific exception types for different
failure scenarios, replacing scattered sys.exit() calls.
"""


class HowitzerException(Exception):
    """
    Base exception for all Howitzer-specific errors.

    All custom exceptions in the Howitzer tool should inherit from this class.
    """
    pass


class ConfigurationError(HowitzerException):
    """
    Configuration loading or validation failed.

    Raised when:
    - Template YAML file cannot be loaded
    - Template structure is invalid
    - Profile configuration is malformed
    - Required configuration fields are missing
    """
    pass


class BurpXMLError(HowitzerException):
    """
    Burp Suite XML parsing failed.

    Raised when:
    - XML file cannot be found or opened
    - XML structure is invalid
    - Base64 decoding fails
    - Required XML elements are missing
    """
    pass


class HTTPClientError(HowitzerException):
    """
    HTTP request execution failed.

    Raised when:
    - HTTP request times out
    - Connection to target or proxy fails
    - Invalid URL format
    - Network errors occur
    """
    pass


class ProfileValidationError(HowitzerException):
    """
    Profile validation failed.

    Raised when:
    - Profile name doesn't exist in template
    - Required CLI header values are missing
    - Profile structure is invalid
    - Header manipulation fails
    """
    pass


class ParseError(HowitzerException):
    """
    Parsing operation failed.

    Raised when:
    - HTTP request parsing fails
    - Header parsing fails
    - URL parsing fails
    - Invalid format encountered
    """
    pass


class MatchDetectionError(HowitzerException):
    """
    Match detection operation failed.

    Raised when:
    - Response comparison fails
    - Invalid match strategy
    - Missing required response data
    """
    pass
