from typing import Dict, List, Tuple
from utils.models import Profile, HTTPRequest
from utils.exceptions import ProfileValidationError, ConfigurationError
from utils.parsers import manipulate_headers


class ProfileProcessor:
    """
    Applies authentication profiles to HTTP requests.

    Wraps existing manipulate_headers() logic without modifying it.
    """

    def __init__(self, config: Dict):
        """
        Initialize processor with template configuration.

        Args:
            config: Template configuration dict from YAML
        """
        self.config = config
        self.profiles: Dict[str, Profile] = {}
        self._load_profiles()

    def _load_profiles(self) -> None:
        """
        Load profiles from config into Profile domain models.

        Converts YAML config structure to Profile dataclasses.
        """
        if 'profiles' not in self.config:
            raise ConfigurationError("No 'profiles' section in template")

        for name, profile_config in self.config['profiles'].items():
            # Create Profile domain model
            # Note: We don't validate structure here as it's handled by manipulate_headers
            # when actually applied, or by basic YAML parsing.
            # But we should ensure basic fields exist.
            
            profile = Profile(
                name=name,
                description=profile_config.get('description', ''),
                original_headers=profile_config.get('original_headers', 'keep'),
                replace_headers=[h['header'] for h in profile_config.get('replace', [])],
                add_headers=[h['header'] for h in profile_config.get('add', [])],
                replace_values={},  # Populated from CLI
                add_values={}       # Populated from CLI
            )

            self.profiles[name] = profile

    def get_profile(self, name: str) -> Profile:
        """
        Get profile by name.

        Args:
            name: Profile name

        Returns:
            Profile domain model

        Raises:
            ProfileValidationError: If profile doesn't exist
        """
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
        """
        Apply profile transformations to request.

        IMPORTANT: Uses existing manipulate_headers() logic internally.
        No changes to header manipulation strategy.

        Args:
            request: Original HTTP request
            profile: Profile to apply
            replace_headers_cli: CLI header replacements (from -rH)
            add_headers_cli: CLI header additions (from -aH)

        Returns:
            New HTTPRequest with modified headers

        Raises:
            ProfileValidationError: If profile application fails
        """
        # Get profile config from original YAML structure
        profile_config = self.config['profiles'][profile.name]

        # Use existing manipulate_headers() function (UNCHANGED)
        try:
            modified_headers = manipulate_headers(
                original_headers=request.headers,
                profile_config=profile_config,
                replace_headers_cli=replace_headers_cli,
                add_headers_cli=add_headers_cli
            )
        except ValueError as e:
            raise ProfileValidationError(f"Failed to apply profile '{profile.name}': {e}")

        # Create new HTTPRequest with modified headers
        return HTTPRequest(
            method=request.method,
            url=request.url,
            headers=modified_headers,
            body=request.body,
            raw=request.raw
        )

    def list_profiles(self) -> List[str]:
        """Get list of available profile names."""
        return list(self.profiles.keys())
