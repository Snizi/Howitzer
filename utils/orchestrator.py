from typing import List, Dict
from utils.models import Profile, Match
from utils.http_client import HTTPClient
from utils.services.replay_service import RequestReplayService
from utils.burp_parser import BurpXMLParser
from utils.profile_processor import ProfileProcessor
from utils.logging import HowitzerLogger
from utils.exceptions import BurpXMLError, ProfileValidationError, HTTPClientError


class HowitzerOrchestrator:
    """
    Main application workflow orchestrator.

    Coordinates parsing of Burp XML, profile processing, and request replay
    to detect authorization bypass vulnerabilities.
    """

    def __init__(
        self,
        burp_xml_path: str,
        http_client: HTTPClient,
        profile_processor: ProfileProcessor,
        replay_service: RequestReplayService,
        logger: HowitzerLogger
    ):
        """
        Initialize orchestrator with dependencies.

        Args:
            burp_xml_path: Path to Burp Suite XML export
            http_client: Configured HTTP client
            profile_processor: Profile processor for loading profiles
            replay_service: Request replay service
            logger: Logger for output
        """
        self.burp_xml_path = burp_xml_path
        self.http_client = http_client
        self.profile_processor = profile_processor
        self.replay_service = replay_service
        self.logger = logger
        self.results: List[Match] = []

    def run(
        self,
        profile_configs: List[Dict],
        verbose: bool = False
    ) -> tuple[List[Match], int]:
        """
        Execute main workflow.

        Workflow:
        1. Parse Burp XML export
        2. For each profile specification:
           a. Load profile from processor
           b. Display profile banner
           c. Replay all requests with profile applied
           d. Collect matches
        3. Return all detected matches

        Args:
            profile_configs: List of profile specifications from CLI
                Example: [
                    {'profile': 'lorenzo', 'replace': [('Auth', 'token')], 'add': []},
                    {'profile': 'user2', 'replace': [], 'add': [('X-Key', 'secret')]}
                ]
            verbose: Enable verbose logging

        Returns:
            List of Match objects for detected authorization bypasses

        Raises:
            BurpXMLError: If XML parsing fails
            ProfileValidationError: If profile doesn't exist or is invalid
        """
        # Parse Burp XML
        self.logger.info(f"Loading Burp Suite XML export: {self.burp_xml_path}")
        parser = BurpXMLParser(self.burp_xml_path)

        # Validate XML format
        parser.validate_format()
        item_count = parser.count_items()
        self.logger.info(f"Found {item_count} items in XML export")

        # Process each profile
        for profile_spec in profile_configs:
            profile_name = profile_spec['profile']
            replace_headers_cli = profile_spec['replace']
            add_headers_cli = profile_spec['add']

            # Get profile from processor (validates it exists)
            profile = self.profile_processor.get_profile(profile_name)

            # Display profile banner
            self._print_profile_banner(profile)

            # Track matches for this profile
            profile_matches = 0

            # Process all requests with this profile
            for original_request, original_response in parser.parse():
                try:
                    match = self.replay_service.replay_request(
                        original_request=original_request,
                        original_response=original_response,
                        profile=profile,
                        replace_headers_cli=replace_headers_cli,
                        add_headers_cli=add_headers_cli,
                        original_profile_name="original",
                        verbose=verbose
                    )

                    if match:
                        self.results.append(match)
                        profile_matches += 1

                except HTTPClientError as e:
                    # Log but continue processing other requests
                    self.logger.error(f"HTTP error: {e}")
                    continue

            # Summary for this profile
            self.logger.info(f"\nProfile '{profile_name}' complete: {profile_matches} matches found")

        # Final summary
        self.logger.separator()
        total_requests = item_count * len(profile_configs)
        self.logger.info(f"Total matches found: {len(self.results)} / {total_requests} requests")
        self.logger.separator()

        return self.results, total_requests

    def _print_profile_banner(self, profile: Profile) -> None:
        """
        Display profile banner.

        Args:
            profile: Profile to display
        """
        self.logger.separator('=')
        self.logger.info(f"Running profile: {profile.name}")
        if profile.description:
            self.logger.info(f"Description: {profile.description}")
        self.logger.separator('=')
        print()  # Blank line for readability
