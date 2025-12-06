from typing import Optional, List, Tuple
from utils.models import HTTPRequest, HTTPResponse, Profile, Match
from utils.http_client import HTTPClient
from utils.profile_processor import ProfileProcessor
from utils.match_detector import MatchDetector
from utils.logging import HowitzerLogger
from utils.exceptions import HTTPClientError


class RequestReplayService:

    def __init__(
        self,
        http_client: HTTPClient,
        profile_processor: ProfileProcessor,
        match_detector: MatchDetector,
        logger: HowitzerLogger = None
    ):
        self.http_client = http_client
        self.profile_processor = profile_processor
        self.match_detector = match_detector
        self.logger = logger or HowitzerLogger()

    def replay_request(
        self,
        original_request: HTTPRequest,
        original_response: HTTPResponse,
        profile: Profile,
        replace_headers_cli: List[Tuple[str, str]],
        add_headers_cli: List[Tuple[str, str]],
        original_profile_name: str = "original",
        verbose: bool = False
    ) -> Optional[Match]:
        self.logger.info(f"Processing {original_request.method} {original_request.url}...")

        modified_request = self.profile_processor.apply_profile(
            request=original_request,
            profile=profile,
            replace_headers_cli=replace_headers_cli,
            add_headers_cli=add_headers_cli
        )

        if verbose:
            self.logger.verbose_log(f"  Original headers: {list(original_request.headers.keys())}")
            self.logger.verbose_log(f"  Modified headers: {list(modified_request.headers.keys())}")
            for name, value in modified_request.headers.items():
                display_value = value[:50] + "..." if len(value) > 50 else value
                self.logger.verbose_log(f"    {name}: {display_value}")

        try:
            modified_response = self.http_client.send_request(modified_request)
        except HTTPClientError as e:
            self.logger.error(f"  Failed to send request: {e}")
            raise

        self.logger.info(
            f"  Original Body Len: {original_response.body_length}, "
            f"New Body Len: {modified_response.body_length}"
        )

        match = self.match_detector.detect_match(
            original_request=original_request,
            original_response=original_response,
            modified_request=modified_request,
            modified_response=modified_response,
            original_profile=original_profile_name,
            modified_profile=profile.name
        )

        if match:
            self.logger.success("  MATCH FOUND!")

        return match
