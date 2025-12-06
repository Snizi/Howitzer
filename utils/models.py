
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone


@dataclass
class Profile:
    name: str
    description: str
    original_headers: str
    replace_headers: List[str] = field(default_factory=list)
    add_headers: List[str] = field(default_factory=list)
    replace_values: Dict[str, str] = field(default_factory=dict)
    add_values: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.original_headers not in ('keep', 'remove'):
            raise ValueError(f"original_headers must be 'keep' or 'remove', got: {self.original_headers}")


@dataclass
class HTTPRequest:
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str] = None
    raw: str = ""

    def __post_init__(self):
        if not self.method:
            raise ValueError("HTTP method cannot be empty")
        if not self.url:
            raise ValueError("URL cannot be empty")


@dataclass
class HTTPResponse:
    status_code: int
    body: str
    body_length: int
    headers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.body_length != len(self.body):
            self.body_length = len(self.body)


@dataclass
class Match:
    url: str
    method: str
    original_profile: str
    matched_profile: str
    response_length: int
    original_length: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    status_code: Optional[int] = None
    path: Optional[str] = None

    def to_dict(self) -> Dict:
        from urllib.parse import urlparse
        parsed_url = urlparse(self.url)
        host = parsed_url.netloc

        return {
            'url': self.url,
            'method': self.method,
            'original_profile': self.original_profile,
            'matched_profile': self.matched_profile,
            'response_length': self.response_length,
            'original_length': self.original_length,
            'replayed_length': self.response_length,
            'timestamp': self.timestamp.isoformat(),
            'status_code': self.status_code,
            'path': self.path,
            'host': host,
            'profile': self.matched_profile
        }


@dataclass
class HTTPClientConfig:
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    timeout: int = 10
    verify_ssl: bool = False
    user_agent: str = "Howitzer/1.0"

    @property
    def proxy_url(self) -> Optional[str]:
        if self.proxy_host and self.proxy_port:
            return f"http://{self.proxy_host}:{self.proxy_port}"
        return None

    @property
    def proxies(self) -> Optional[Dict[str, str]]:
        proxy_url = self.proxy_url
        if proxy_url:
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        return None

    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError(f"timeout must be positive, got: {self.timeout}")
        if self.proxy_port is not None and (self.proxy_port <= 0 or self.proxy_port > 65535):
            raise ValueError(f"proxy_port must be between 1-65535, got: {self.proxy_port}")
        if (self.proxy_host is None) != (self.proxy_port is None):
            raise ValueError("Both proxy_host and proxy_port must be set together, or neither")
