"""
HTTP client abstraction for the Howitzer security testing tool.

Provides a wrapper around the requests library with configurable proxy,
timeout, and SSL verification settings, replacing hardcoded HTTP client
configuration in the main application loop.
"""

import requests
from typing import Optional, Dict
from utils.models import HTTPRequest, HTTPResponse, HTTPClientConfig
from utils.exceptions import HTTPClientError


class HTTPClient:
    """
    HTTP client wrapper with configurable settings.

    Encapsulates proxy configuration, timeout settings, and SSL verification,
    providing a clean interface for sending HTTP requests and receiving
    standardized responses.
    """

    def __init__(self, config: HTTPClientConfig):
        """
        Initialize HTTP client with configuration.

        Args:
            config: HTTPClientConfig with proxy, timeout, and SSL settings
        """
        self.config = config
        self.session = requests.Session()
        self._configure_session()

    def _configure_session(self) -> None:
        """Configure the requests session with client settings."""
        # Set user agent
        self.session.headers.update({
            'User-Agent': self.config.user_agent
        })

        # Configure SSL verification
        self.session.verify = self.config.verify_ssl

    def send_request(self, request: HTTPRequest) -> HTTPResponse:
        """
        Send HTTP request and return standardized response.

        Args:
            request: HTTPRequest domain model with method, URL, headers, and body

        Returns:
            HTTPResponse domain model with status code, body, and metadata

        Raises:
            HTTPClientError: If request fails due to timeout, connection error, etc.
        """
        try:
            # Send request with configured settings
            response = self.session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                data=request.body,
                timeout=self.config.timeout,
                proxies=self.config.proxies  # Will be None if no proxy configured
            )

            # Convert to domain model
            return HTTPResponse(
                status_code=response.status_code,
                body=response.content.decode('utf-8', errors='replace'),
                body_length=len(response.content),
                headers=dict(response.headers)
            )

        except requests.exceptions.Timeout as e:
            raise HTTPClientError(f"Request timeout after {self.config.timeout}s: {e}")

        except requests.exceptions.ConnectionError as e:
            # Provide helpful message if proxy is configured
            if self.config.proxy_url:
                raise HTTPClientError(
                    f"Connection failed (proxy: {self.config.proxy_url}): {e}"
                )
            raise HTTPClientError(f"Connection failed: {e}")

        except requests.exceptions.RequestException as e:
            raise HTTPClientError(f"HTTP request failed: {e}")

        except Exception as e:
            raise HTTPClientError(f"Unexpected error sending request: {e}")

    def close(self) -> None:
        """Close the HTTP session and clean up resources."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
