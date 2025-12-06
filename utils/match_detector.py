from abc import ABC, abstractmethod
from typing import Optional
from utils.models import HTTPRequest, HTTPResponse, Match
from datetime import datetime, timezone


class MatchStrategy(ABC):
    """Abstract match detection strategy."""

    @abstractmethod
    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        """
        Determine if responses match (indicating potential bypass).

        Args:
            original: Original response from Burp Suite
            modified: Response from replayed request with different credentials

        Returns:
            True if responses match, False otherwise
        """
        pass


class BodyLengthMatcher(MatchStrategy):
    """
    Match based on response body length equality.

    This is the current detection strategy used in main.py.
    """

    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        """Check if body lengths are equal."""
        return original.body_length == modified.body_length


class StatusCodeMatcher(MatchStrategy):
    """Match based on HTTP status code equality."""

    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        """Check if status codes are equal."""
        return original.status_code == modified.status_code


class ExactBodyMatcher(MatchStrategy):
    """Match based on exact body content equality."""

    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        """Check if response bodies are exactly equal."""
        return original.body == modified.body


class CombinedMatcher(MatchStrategy):
    """
    Combine multiple matchers (all must match).

    Example: Both body length AND status code must match.
    """

    def __init__(self, *strategies: MatchStrategy):
        """
        Initialize with multiple strategies.

        Args:
            strategies: Variable number of MatchStrategy instances
        """
        self.strategies = strategies

    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        """Check if all strategies match."""
        return all(
            strategy.is_match(original, modified)
            for strategy in self.strategies
        )


class MatchDetector:
    """
    Detects potential authorization bypass vulnerabilities.

    Compares original and modified responses to identify endpoints
    that behave identically across different user contexts.
    """

    def __init__(self, strategy: MatchStrategy = None):
        """
        Initialize detector with match strategy.

        Args:
            strategy: MatchStrategy to use (defaults to BodyLengthMatcher)
        """
        self.strategy = strategy or BodyLengthMatcher()

    def detect_match(
        self,
        original_request: HTTPRequest,
        original_response: HTTPResponse,
        modified_request: HTTPRequest,
        modified_response: HTTPResponse,
        original_profile: str,
        modified_profile: str
    ) -> Optional[Match]:
        """
        Detect if responses indicate authorization bypass.

        Args:
            original_request: Original HTTP request from Burp Suite
            original_response: Original HTTP response from Burp Suite
            modified_request: Replayed request with modified credentials
            modified_response: Response from replayed request
            original_profile: Name of original profile (usually "original")
            modified_profile: Name of profile used for replay

        Returns:
            Match object if bypass detected, None otherwise
        """
        # Check if responses match using configured strategy
        if self.strategy.is_match(original_response, modified_response):
            # Create Match domain model
            from urllib.parse import urlparse

            parsed_url = urlparse(original_request.url)

            return Match(
                url=original_request.url,
                method=original_request.method,
                original_profile=original_profile,
                matched_profile=modified_profile,
                response_length=modified_response.body_length,
                original_length=original_response.body_length,
                timestamp=datetime.now(timezone.utc),
                status_code=modified_response.status_code,
                path=parsed_url.path or '/'
            )

        return None
