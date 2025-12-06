
import requests
from typing import Optional, Dict
from utils.models import HTTPRequest, HTTPResponse, HTTPClientConfig
from utils.exceptions import HTTPClientError


class HTTPClient:

    def __init__(self, config: HTTPClientConfig):
        self.config = config
        self.session = requests.Session()
        self._configure_session()

    def _configure_session(self) -> None:
        self.session.headers.update({
            'User-Agent': self.config.user_agent
        })

        self.session.verify = self.config.verify_ssl

    def send_request(self, request: HTTPRequest) -> HTTPResponse:
        try:
            response = self.session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                data=request.body,
                timeout=self.config.timeout,
                proxies=self.config.proxies
            )

            return HTTPResponse(
                status_code=response.status_code,
                body=response.content.decode('utf-8', errors='replace'),
                body_length=len(response.content),
                headers=dict(response.headers)
            )

        except requests.exceptions.Timeout as e:
            raise HTTPClientError(f"Request timeout after {self.config.timeout}s: {e}")

        except requests.exceptions.ConnectionError as e:
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
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
