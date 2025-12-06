"""
Burp Suite XML parser for the Howitzer security testing tool.

Parses Burp Suite XML exports into domain models, handling base64 decoding
and extracting HTTP requests and responses.
"""

import xml.etree.ElementTree as ET
from typing import Iterator, Tuple
from utils.models import HTTPRequest, HTTPResponse
from utils.exceptions import BurpXMLError, ParseError
from utils.parsers import decode_base64, parse_raw_request, extract_body_from_raw_response


class BurpXMLParser:
    """
    Parser for Burp Suite XML export files.

    Reads XML files exported from Burp Suite and yields domain model objects
    for HTTP requests and responses, handling base64 decoding and parsing.
    """

    def __init__(self, xml_path: str):
        """
        Initialize parser with XML file path.

        Args:
            xml_path: Path to Burp Suite XML export file

        Raises:
            BurpXMLError: If XML file cannot be loaded or parsed
        """
        self.xml_path = xml_path
        self.tree = None
        self.root = None
        self._load_xml()

    def _load_xml(self) -> None:
        """
        Load and parse XML file.

        Raises:
            BurpXMLError: If file not found or XML parsing fails
        """
        try:
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()
        except FileNotFoundError:
            raise BurpXMLError(f"Burp XML file not found: {self.xml_path}")
        except ET.ParseError as e:
            raise BurpXMLError(f"Invalid XML format in {self.xml_path}: {e}")
        except Exception as e:
            raise BurpXMLError(f"Failed to load XML file {self.xml_path}: {e}")

    def validate_format(self) -> bool:
        """
        Validate that XML has expected Burp Suite structure.

        Returns:
            True if XML appears to be valid Burp Suite export

        Raises:
            BurpXMLError: If XML structure is invalid
        """
        if self.root is None:
            raise BurpXMLError("XML not loaded")

        # Check for at least one <item> element
        items = self.root.findall('item')
        if not items:
            raise BurpXMLError("No <item> elements found in XML")

        # Validate first item has expected structure
        first_item = items[0]
        required_elements = ['url', 'request', 'response', 'method']
        for elem_name in required_elements:
            if first_item.find(elem_name) is None:
                raise BurpXMLError(
                    f"Missing required element <{elem_name}> in XML structure"
                )

        return True

    def parse(self, skip_options: bool = True) -> Iterator[Tuple[HTTPRequest, HTTPResponse]]:
        """
        Parse XML and yield (HTTPRequest, HTTPResponse) tuples.

        Args:
            skip_options: If True, skip OPTIONS requests (default: True)

        Yields:
            Tuple of (HTTPRequest, HTTPResponse) domain models

        Raises:
            BurpXMLError: If XML parsing fails
            ParseError: If HTTP request/response parsing fails
        """
        if self.root is None:
            raise BurpXMLError("XML not loaded")

        for item in self.root.findall('item'):
            try:
                # Extract XML elements
                url_elem = item.find('url')
                request_elem = item.find('request')
                response_elem = item.find('response')
                method_elem = item.find('method')

                # Skip items with missing required elements
                if url_elem is None or request_elem is None or response_elem is None:
                    continue

                url = url_elem.text
                method = method_elem.text if method_elem is not None else 'GET'

                # Skip OPTIONS requests if requested
                if skip_options and method.upper() == 'OPTIONS':
                    continue

                # Decode request (handle base64 encoding)
                is_base64 = request_elem.get('base64') == 'true'
                raw_request = (
                    decode_base64(request_elem.text) if is_base64
                    else request_elem.text.encode('utf-8')
                )

                # Parse HTTP request
                try:
                    parsed_method, path, protocol, headers, body = parse_raw_request(raw_request)
                except Exception as e:
                    raise ParseError(f"Failed to parse HTTP request for {url}: {e}")

                # Create HTTPRequest domain model
                http_request = HTTPRequest(
                    method=parsed_method,
                    url=url,
                    headers=headers,
                    body=body,
                    raw=raw_request.decode('utf-8', errors='replace')
                )

                # Decode response (handle base64 encoding)
                is_base64 = response_elem.get('base64') == 'true'
                raw_response = (
                    decode_base64(response_elem.text) if is_base64
                    else response_elem.text.encode('utf-8')
                )

                # Extract response body
                try:
                    response_body = extract_body_from_raw_response(raw_response)
                except Exception as e:
                    raise ParseError(f"Failed to parse HTTP response for {url}: {e}")

                # Create HTTPResponse domain model
                # Note: We don't have status code in the raw response extraction,
                # so we'll use a placeholder. The original code doesn't extract it either.
                http_response = HTTPResponse(
                    status_code=0,  # Placeholder - original response status unknown
                    body=response_body.decode('utf-8', errors='replace'),
                    body_length=len(response_body),
                    headers={}  # Could parse response headers if needed
                )

                yield (http_request, http_response)

            except ParseError:
                # Re-raise ParseError as-is
                raise
            except BurpXMLError:
                # Re-raise BurpXMLError as-is
                raise
            except Exception as e:
                # Wrap unexpected exceptions
                raise BurpXMLError(f"Unexpected error parsing XML item: {e}")

    def count_items(self) -> int:
        """
        Count total number of items in XML.

        Returns:
            Number of <item> elements in XML
        """
        if self.root is None:
            return 0
        return len(self.root.findall('item'))
