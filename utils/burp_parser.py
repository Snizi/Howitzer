
import xml.etree.ElementTree as ET
from typing import Iterator, Tuple
from utils.models import HTTPRequest, HTTPResponse
from utils.exceptions import BurpXMLError, ParseError
from utils.parsers import decode_base64, parse_raw_request, extract_body_from_raw_response


class BurpXMLParser:

    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.tree = None
        self.root = None
        self._load_xml()

    def _load_xml(self) -> None:
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
        if self.root is None:
            raise BurpXMLError("XML not loaded")

        items = self.root.findall('item')
        if not items:
            raise BurpXMLError("No <item> elements found in XML")

        first_item = items[0]
        required_elements = ['url', 'request', 'response', 'method']
        for elem_name in required_elements:
            if first_item.find(elem_name) is None:
                raise BurpXMLError(
                    f"Missing required element <{elem_name}> in XML structure"
                )

        return True

    def parse(self, skip_options: bool = True) -> Iterator[Tuple[HTTPRequest, HTTPResponse]]:
        if self.root is None:
            raise BurpXMLError("XML not loaded")

        for item in self.root.findall('item'):
            try:
                url_elem = item.find('url')
                request_elem = item.find('request')
                response_elem = item.find('response')
                method_elem = item.find('method')

                if url_elem is None or request_elem is None or response_elem is None:
                    continue

                url = url_elem.text
                method = method_elem.text if method_elem is not None else 'GET'

                if skip_options and method.upper() == 'OPTIONS':
                    continue

                is_base64 = request_elem.get('base64') == 'true'
                raw_request = (
                    decode_base64(request_elem.text) if is_base64
                    else request_elem.text.encode('utf-8')
                )

                try:
                    parsed_method, path, protocol, headers, body = parse_raw_request(raw_request)
                except Exception as e:
                    raise ParseError(f"Failed to parse HTTP request for {url}: {e}")

                http_request = HTTPRequest(
                    method=parsed_method,
                    url=url,
                    headers=headers,
                    body=body,
                    raw=raw_request.decode('utf-8', errors='replace')
                )

                is_base64 = response_elem.get('base64') == 'true'
                raw_response = (
                    decode_base64(response_elem.text) if is_base64
                    else response_elem.text.encode('utf-8')
                )

                try:
                    response_body = extract_body_from_raw_response(raw_response)
                except Exception as e:
                    raise ParseError(f"Failed to parse HTTP response for {url}: {e}")

                http_response = HTTPResponse(
                    status_code=0,
                    body=response_body.decode('utf-8', errors='replace'),
                    body_length=len(response_body),
                    headers={}
                )

                yield (http_request, http_response)

            except ParseError:
                raise
            except BurpXMLError:
                raise
            except Exception as e:
                raise BurpXMLError(f"Unexpected error parsing XML item: {e}")

    def count_items(self) -> int:
        if self.root is None:
            return 0
        return len(self.root.findall('item'))
