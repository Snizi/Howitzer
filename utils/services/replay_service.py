from typing import Optional, List, Tuple
from utils.models import HTTPRequest, HTTPResponse, Profile, Match
from utils.http_client import HTTPClient
from utils.profile_processor import ProfileProcessor
from utils.match_detector import MatchDetector
from utils.logging import HowitzerLogger
from utils.exceptions import HTTPClientError


class RequestReplayService:
    """
    Coordinates request replay workflow.

    Orchestrates profile application, HTTP request sending, and
    match detection for authorization bypass testing.
    """

    def __init__(
        self,
        http_client: HTTPClient,
        profile_processor: ProfileProcessor,
        match_detector: MatchDetector,
        logger: HowitzerLogger = None
    ):
        """
        Initialize replay service with dependencies.

        Args:
            http_client: HTTPClient for sending requests
            profile_processor: ProfileProcessor for applying profiles
            match_detector: MatchDetector for detecting bypasses
            logger: Optional logger for output
        """
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
        """
        Replay request with profile applied and detect matches.

        Workflow:
        1. Apply profile to request headers
        2. Send modified request via HTTP client
        3. Compare responses using match detector
        4. Return Match if authorization bypass detected

        Args:
            original_request: Original HTTP request from Burp Suite
            original_response: Original HTTP response from Burp Suite
            profile: Profile to apply
            replace_headers_cli: CLI header replacements (from -rH)
            add_headers_cli: CLI header additions (from -aH)
            original_profile_name: Name for original profile (default: "original")
            verbose: Enable verbose logging

        Returns:
            Match object if bypass detected, None otherwise

        Raises:
            HTTPClientError: If HTTP request fails
            ProfileValidationError: If profile application fails
        """
        # Log request processing
        self.logger.info(f"Processing {original_request.method} {original_request.url}...")

        # 1. Apply profile to request
        modified_request = self.profile_processor.apply_profile(
            request=original_request,
            profile=profile,
            replace_headers_cli=replace_headers_cli,
            add_headers_cli=add_headers_cli
        )

        # Verbose output
        if verbose:
            self.logger.verbose_log(f"  Original headers: {list(original_request.headers.keys())}")
            self.logger.verbose_log(f"  Modified headers: {list(modified_request.headers.keys())}")
            for name, value in modified_request.headers.items():
                display_value = value[:50] + "..." if len(value) > 50 else value
                self.logger.verbose_log(f"    {name}: {display_value}")

        # 2. Send modified request
        try:
            modified_response = self.http_client.send_request(modified_request)
        except HTTPClientError as e:
            self.logger.error(f"  Failed to send request: {e}")
            raise

        # Log response lengths
        self.logger.info(
            f"  Original Body Len: {original_response.body_length}, "
            f"New Body Len: {modified_response.body_length}"
        )

        # 3. Detect match
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
