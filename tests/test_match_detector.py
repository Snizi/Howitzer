import unittest
from utils.match_detector import (
    MatchDetector, BodyLengthMatcher, StatusCodeMatcher, 
    ExactBodyMatcher, CombinedMatcher
)
from utils.models import HTTPRequest, HTTPResponse, Match


class TestMatchDetector(unittest.TestCase):

    def setUp(self):
        self.request = HTTPRequest(
            method='GET',
            url='http://example.com',
            headers={}
        )
        self.response1 = HTTPResponse(
            status_code=200,
            body='test body',
            body_length=9
        )
        self.response2 = HTTPResponse(
            status_code=200,
            body='test body',
            body_length=9
        )
        self.response3 = HTTPResponse(
            status_code=403,
            body='access denied',
            body_length=13
        )

    def test_body_length_matcher(self):
        matcher = BodyLengthMatcher()
        self.assertTrue(matcher.is_match(self.response1, self.response2))
        self.assertFalse(matcher.is_match(self.response1, self.response3))

    def test_status_code_matcher(self):
        matcher = StatusCodeMatcher()
        self.assertTrue(matcher.is_match(self.response1, self.response2))
        self.assertFalse(matcher.is_match(self.response1, self.response3))

    def test_exact_body_matcher(self):
        matcher = ExactBodyMatcher()
        self.assertTrue(matcher.is_match(self.response1, self.response2))
        self.assertFalse(matcher.is_match(self.response1, self.response3))

    def test_combined_matcher(self):
        matcher = CombinedMatcher(BodyLengthMatcher(), StatusCodeMatcher())
        self.assertTrue(matcher.is_match(self.response1, self.response2))
        self.assertFalse(matcher.is_match(self.response1, self.response3))

    def test_detect_match_found(self):
        detector = MatchDetector(BodyLengthMatcher())
        match = detector.detect_match(
            self.request, self.response1, self.request, self.response2,
            "original", "test_profile"
        )
        self.assertIsNotNone(match)
        self.assertIsInstance(match, Match)
        self.assertEqual(match.url, 'http://example.com')
        self.assertEqual(match.matched_profile, 'test_profile')

    def test_detect_match_not_found(self):
        detector = MatchDetector(BodyLengthMatcher())
        match = detector.detect_match(
            self.request, self.response1, self.request, self.response3,
            "original", "test_profile"
        )
        self.assertIsNone(match)

if __name__ == '__main__':
    unittest.main()
