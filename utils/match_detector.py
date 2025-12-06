from abc import ABC, abstractmethod
from typing import Optional
from utils.models import HTTPRequest, HTTPResponse, Match
from datetime import datetime, timezone


class MatchStrategy(ABC):

    @abstractmethod
    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        pass


class BodyLengthMatcher(MatchStrategy):

    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        return original.body_length == modified.body_length


class StatusCodeMatcher(MatchStrategy):

    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        return original.status_code == modified.status_code


class ExactBodyMatcher(MatchStrategy):

    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        return original.body == modified.body


class CombinedMatcher(MatchStrategy):

    def __init__(self, *strategies: MatchStrategy):
        self.strategies = strategies

    def is_match(self, original: HTTPResponse, modified: HTTPResponse) -> bool:
        return all(
            strategy.is_match(original, modified)
            for strategy in self.strategies
        )


class MatchDetector:

    def __init__(self, strategy: MatchStrategy = None):
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
        if self.strategy.is_match(original_response, modified_response):
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
