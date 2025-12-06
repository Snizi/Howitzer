from typing import Dict, List, Tuple
from utils.models import Profile, HTTPRequest
from utils.exceptions import ProfileValidationError, ConfigurationError
from utils.parsers import manipulate_headers


class ProfileProcessor:

    def __init__(self, config: Dict):
        self.config = config
        self.profiles: Dict[str, Profile] = {}
        self._load_profiles()

    def _load_profiles(self) -> None:
        if 'profiles' not in self.config:
            raise ConfigurationError("No 'profiles' section in template")

        for name, profile_config in self.config['profiles'].items():
            
            profile = Profile(
                name=name,
                description=profile_config.get('description', ''),
                original_headers=profile_config.get('original_headers', 'keep'),
                replace_headers=[h['header'] for h in profile_config.get('replace', [])],
                add_headers=[h['header'] for h in profile_config.get('add', [])],
                replace_values={},
                add_values={}
            )

            self.profiles[name] = profile

    def get_profile(self, name: str) -> Profile:
        if name not in self.profiles:
            available = ', '.join(self.profiles.keys())
            raise ProfileValidationError(
                f"Profile '{name}' not found. Available profiles: {available}"
            )
        return self.profiles[name]

    def apply_profile(
        self,
        request: HTTPRequest,
        profile: Profile,
        replace_headers_cli: List[Tuple[str, str]],
        add_headers_cli: List[Tuple[str, str]]
    ) -> HTTPRequest:
        profile_config = self.config['profiles'][profile.name]

        try:
            modified_headers = manipulate_headers(
                original_headers=request.headers,
                profile_config=profile_config,
                replace_headers_cli=replace_headers_cli,
                add_headers_cli=add_headers_cli
            )
        except ValueError as e:
            raise ProfileValidationError(f"Failed to apply profile '{profile.name}': {e}")

        return HTTPRequest(
            method=request.method,
            url=request.url,
            headers=modified_headers,
            body=request.body,
            raw=request.raw
        )

    def list_profiles(self) -> List[str]:
        return list(self.profiles.keys())
