from typing import List, Dict
from utils.models import Profile, Match
from utils.http_client import HTTPClient
from utils.services.replay_service import RequestReplayService
from utils.burp_parser import BurpXMLParser
from utils.profile_processor import ProfileProcessor
from utils.logging import HowitzerLogger
from utils.exceptions import BurpXMLError, ProfileValidationError, HTTPClientError


class HowitzerOrchestrator:

    def __init__(
        self,
        burp_xml_path: str,
        http_client: HTTPClient,
        profile_processor: ProfileProcessor,
        replay_service: RequestReplayService,
        logger: HowitzerLogger
    ):
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
        self.results = []
        self.logger.info(f"Loading Burp Suite XML export: {self.burp_xml_path}")
        parser = BurpXMLParser(self.burp_xml_path)

        parser.validate_format()
        item_count = parser.count_items()
        self.logger.info(f"Found {item_count} items in XML export")

        for profile_spec in profile_configs:
            profile_name = profile_spec['profile']
            replace_headers_cli = profile_spec['replace']
            add_headers_cli = profile_spec['add']

            profile = self.profile_processor.get_profile(profile_name)

            self._print_profile_banner(profile)

            profile_matches = 0

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
                    self.logger.error(f"HTTP error: {e}")
                    continue

            self.logger.info(f"\nProfile '{profile_name}' complete: {profile_matches} matches found")

        self.logger.separator()
        total_requests = item_count * len(profile_configs)
        self.logger.info(f"Total matches found: {len(self.results)} / {total_requests} requests")
        self.logger.separator()

        return self.results, total_requests

    def _print_profile_banner(self, profile: Profile) -> None:
        self.logger.separator('=')
        self.logger.info(f"Running profile: {profile.name}")
        if profile.description:
            self.logger.info(f"Description: {profile.description}")
        self.logger.separator('=')
        print()
