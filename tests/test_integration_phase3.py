import unittest
from unittest.mock import Mock, patch
from utils.models import HTTPRequest, HTTPResponse, Profile, Match
from utils.services.replay_service import RequestReplayService
from utils.profile_processor import ProfileProcessor
from utils.match_detector import MatchDetector
from utils.http_client import HTTPClient
from utils.logging import HowitzerLogger

class TestIntegrationPhase3(unittest.TestCase):

    def setUp(self):
        self.config = {
            'profiles': {
                'integration_test': {
                    'description': 'Integration Test Profile',
                    'original_headers': 'keep',
                    'replace': [{'header': 'Authorization'}],
                    'add': [{'header': 'X-Integration'}]
                }
            }
        }
        self.profile_processor = ProfileProcessor(self.config)
        self.match_detector = MatchDetector()
        self.logger = HowitzerLogger(verbose=True)
        
        self.http_client = Mock(spec=HTTPClient)
        
        self.replay_service = RequestReplayService(
            http_client=self.http_client,
            profile_processor=self.profile_processor,
            match_detector=self.match_detector,
            logger=self.logger
        )

    def test_full_replay_workflow(self):
        original_request = HTTPRequest(
            method='GET',
            url='http://example.com/api/resource',
            headers={'Authorization': 'Bearer original', 'Content-Type': 'application/json'}
        )
        
        original_response = HTTPResponse(
            status_code=200,
            body='{"data": "secret"}',
            body_length=18
        )
        
        replayed_response = HTTPResponse(
            status_code=200,
            body='{"data": "secret"}',
            body_length=18
        )
        self.http_client.send_request.return_value = replayed_response

        profile = self.profile_processor.get_profile('integration_test')
        replace_headers_cli = [('Authorization', 'Bearer new_token')]
        add_headers_cli = [('X-Integration', 'true')]

        match = self.replay_service.replay_request(
            original_request=original_request,
            original_response=original_response,
            profile=profile,
            replace_headers_cli=replace_headers_cli,
            add_headers_cli=add_headers_cli,
            verbose=True
        )

        
        self.http_client.send_request.assert_called_once()
        call_args = self.http_client.send_request.call_args
        sent_request = call_args[0][0]
        
        self.assertEqual(sent_request.headers['Authorization'], 'Bearer new_token')
        self.assertEqual(sent_request.headers['X-Integration'], 'true')
        
        self.assertIsNotNone(match)
        self.assertEqual(match.url, 'http://example.com/api/resource')
        self.assertEqual(match.matched_profile, 'integration_test')

if __name__ == '__main__':
    unittest.main()
