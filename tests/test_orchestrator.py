import unittest
from unittest.mock import Mock, patch, MagicMock
from utils.orchestrator import HowitzerOrchestrator
from utils.models import HTTPRequest, HTTPResponse, Profile, Match
from utils.exceptions import BurpXMLError, HTTPClientError


class TestHowitzerOrchestrator(unittest.TestCase):

    def setUp(self):
        self.burp_xml_path = "test.xml"
        self.http_client = Mock()
        self.profile_processor = Mock()
        self.replay_service = Mock()
        self.logger = Mock()

        self.orchestrator = HowitzerOrchestrator(
            self.burp_xml_path,
            self.http_client,
            self.profile_processor,
            self.replay_service,
            self.logger
        )

    @patch('utils.orchestrator.BurpXMLParser')
    def test_run_success(self, MockParser):
        mock_parser_instance = MockParser.return_value
        mock_parser_instance.count_items.return_value = 1
        
        request = HTTPRequest(method='GET', url='http://example.com', headers={})
        response = HTTPResponse(status_code=200, body='test', body_length=4)
        mock_parser_instance.parse.return_value = [(request, response)]

        profile = Profile(name='test', description='desc', original_headers='keep')
        self.profile_processor.get_profile.return_value = profile

        mock_match = Match(
            url='http://example.com', method='GET',
            original_profile='original', matched_profile='test',
            response_length=100, original_length=100
        )
        self.replay_service.replay_request.return_value = mock_match

        profile_configs = [{
            'profile': 'test',
            'replace': [],
            'add': []
        }]

        results, total_requests = self.orchestrator.run(profile_configs)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], mock_match)
        self.profile_processor.get_profile.assert_called_with('test')
        self.replay_service.replay_request.assert_called_once()
        self.logger.info.assert_called()

    @patch('utils.orchestrator.BurpXMLParser')
    def test_run_http_error_continues(self, MockParser):
        mock_parser_instance = MockParser.return_value
        mock_parser_instance.count_items.return_value = 1
        mock_parser_instance.parse.return_value = [
            (HTTPRequest(method='GET', url='http://1.com', headers={}), HTTPResponse(status_code=200, body='', body_length=0)),
            (HTTPRequest(method='GET', url='http://2.com', headers={}), HTTPResponse(status_code=200, body='', body_length=0))
        ]

        self.profile_processor.get_profile.return_value = Profile(name='test', description='', original_headers='keep')

        self.replay_service.replay_request.side_effect = [
            HTTPClientError("Connection failed"),
            Match(url='http://2.com', method='GET', original_profile='original', matched_profile='test', response_length=0, original_length=0)
        ]

        profile_configs = [{'profile': 'test', 'replace': [], 'add': []}]

        results, total_requests = self.orchestrator.run(profile_configs)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, 'http://2.com')
        self.logger.error.assert_called()

if __name__ == '__main__':
    unittest.main()
