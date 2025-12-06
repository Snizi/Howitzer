import unittest
from unittest.mock import patch, MagicMock
from utils.profile_processor import ProfileProcessor
from utils.models import Profile, HTTPRequest
from utils.exceptions import ProfileValidationError, ConfigurationError


class TestProfileProcessor(unittest.TestCase):

    def setUp(self):
        self.config = {
            'profiles': {
                'test_profile': {
                    'description': 'Test Description',
                    'original_headers': 'keep',
                    'replace': [{'header': 'Authorization'}],
                    'add': [{'header': 'X-Test'}]
                }
            }
        }
        self.processor = ProfileProcessor(self.config)

    def test_load_profiles(self):
        self.assertIn('test_profile', self.processor.profiles)
        profile = self.processor.profiles['test_profile']
        self.assertEqual(profile.name, 'test_profile')
        self.assertEqual(profile.description, 'Test Description')
        self.assertEqual(profile.original_headers, 'keep')
        self.assertEqual(profile.replace_headers, ['Authorization'])
        self.assertEqual(profile.add_headers, ['X-Test'])

    def test_get_profile_success(self):
        profile = self.processor.get_profile('test_profile')
        self.assertEqual(profile.name, 'test_profile')

    def test_get_profile_not_found(self):
        with self.assertRaises(ProfileValidationError):
            self.processor.get_profile('non_existent')

    def test_apply_profile_success(self):
        request = HTTPRequest(
            method='GET',
            url='http://example.com',
            headers={'Authorization': 'Bearer old', 'Content-Type': 'application/json'}
        )
        profile = self.processor.get_profile('test_profile')
        replace_headers_cli = [('Authorization', 'Bearer new')]
        add_headers_cli = [('X-Test', 'value')]

        modified_request = self.processor.apply_profile(
            request, profile, replace_headers_cli, add_headers_cli
        )

        self.assertEqual(modified_request.headers['Authorization'], 'Bearer new')
        self.assertEqual(modified_request.headers['X-Test'], 'value')
        self.assertEqual(modified_request.headers['Content-Type'], 'application/json')

    def test_apply_profile_failure(self):
        request = HTTPRequest(
            method='GET',
            url='http://example.com',
            headers={}
        )
        profile = self.processor.get_profile('test_profile')
        with self.assertRaises(ProfileValidationError):
            self.processor.apply_profile(request, profile, [], [])

if __name__ == '__main__':
    unittest.main()
