import unittest
from unittest.mock import Mock, MagicMock
from utils.services.replay_service import RequestReplayService
from utils.models import HTTPRequest, HTTPResponse, Profile, Match
from utils.exceptions import HTTPClientError


class TestRequestReplayService(unittest.TestCase):

    def setUp(self):
        self.http_client = Mock()
        self.profile_processor = Mock()
        self.match_detector = Mock()
        self.logger = Mock()
        self.service = RequestReplayService(
            self.http_client, self.profile_processor, 
            self.match_detector, self.logger
        )

        self.original_request = HTTPRequest(
            method='GET', url='http://example.com', headers={}
        )
        self.original_response = HTTPResponse(
            status_code=200, body='original', body_length=8
        )
        self.profile = Profile(
            name='test', description='', original_headers='keep'
        )
        self.modified_request = HTTPRequest(
            method='GET', url='http://example.com', headers={'New': 'Header'}
        )
        self.modified_response = HTTPResponse(
            status_code=200, body='modified', body_length=8
        )

    def test_replay_request_success(self):
        # Setup mocks
        self.profile_processor.apply_profile.return_value = self.modified_request
        self.http_client.send_request.return_value = self.modified_response
        self.match_detector.detect_match.return_value = Match(
            url='http://example.com', method='GET', 
            original_profile='original', matched_profile='test',
            response_length=8, original_length=8
        )

        # Execute
        match = self.service.replay_request(
            self.original_request, self.original_response, self.profile,
            [], []
        )

        # Verify
        self.profile_processor.apply_profile.assert_called_once()
        self.http_client.send_request.assert_called_once_with(self.modified_request)
        self.match_detector.detect_match.assert_called_once()
        self.assertIsNotNone(match)
        self.logger.success.assert_called_once()

    def test_replay_request_http_error(self):
        # Setup mocks
        self.profile_processor.apply_profile.return_value = self.modified_request
        self.http_client.send_request.side_effect = HTTPClientError("Error")

        # Execute & Verify
        with self.assertRaises(HTTPClientError):
            self.service.replay_request(
                self.original_request, self.original_response, self.profile,
                [], []
            )
        self.logger.error.assert_called()

if __name__ == '__main__':
    unittest.main()
