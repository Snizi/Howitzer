import yaml
from utils.exceptions import ConfigurationError


def load_config(config_path):
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        raise ConfigurationError(f"Template file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML syntax: {e}")

def validate_profile(profile_config, profile_name):
    original_headers = profile_config.get('original_headers', 'keep')
    if original_headers not in ['keep', 'remove']:
        raise ConfigurationError(f"Profile '{profile_name}': original_headers must be 'keep' or 'remove'")

    replace = profile_config.get('replace', [])
    if not isinstance(replace, list):
        raise ConfigurationError(f"Profile '{profile_name}': 'replace' must be a list")

    for item in replace:
        if not isinstance(item, dict) or 'header' not in item:
            raise ConfigurationError(f"Profile '{profile_name}': Each replace item must have 'header' key")

    add = profile_config.get('add', [])
    if not isinstance(add, list):
        raise ConfigurationError(f"Profile '{profile_name}': 'add' must be a list")

    for item in add:
        if not isinstance(item, dict) or 'header' not in item:
            raise ConfigurationError(f"Profile '{profile_name}': Each add item must have 'header' key")

    return profile_config
