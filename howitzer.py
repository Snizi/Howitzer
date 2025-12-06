from utils.parsers import parse_header_arg
from utils.config import load_config
from utils.output import ASCIITableOutput, HTMLOutput, JSONOutput, CSVOutput
from utils.models import HTTPClientConfig
from utils.http_client import HTTPClient
from utils.exceptions import HowitzerException, ConfigurationError, BurpXMLError
from utils.logging import HowitzerLogger
from utils.profile_processor import ProfileProcessor
from utils.match_detector import MatchDetector
from utils.services.replay_service import RequestReplayService
from utils.orchestrator import HowitzerOrchestrator
import argparse
import sys
import os


def parse_profile_args(args_list):
    profiles = []
    current_profile = None
    i = 0

    while i < len(args_list):
        arg = args_list[i]

        if arg in ['-p', '--profile']:
            if current_profile:
                profiles.append(current_profile)

            i += 1
            if i >= len(args_list):
                raise ValueError("Missing profile name after -p")
            profile_name = args_list[i]
            current_profile = {
                'profile': profile_name,
                'replace': [],
                'add': []
            }

        elif arg in ['-rH', '--replace-header']:
            if not current_profile:
                raise ValueError("Found -rH before any -p profile declaration")
            i += 1
            if i >= len(args_list):
                raise ValueError("Missing header value after -rH")
            header_str = args_list[i]
            name, value = parse_header_arg(header_str)
            current_profile['replace'].append((name, value))

        elif arg in ['-aH', '--add-header']:
            if not current_profile:
                raise ValueError("Found -aH before any -p profile declaration")
            i += 1
            if i >= len(args_list):
                raise ValueError("Missing header value after -aH")
            header_str = args_list[i]
            name, value = parse_header_arg(header_str)
            current_profile['add'].append((name, value))

        else:
            raise ValueError(f"Unknown argument: {arg}")

        i += 1

    if current_profile:
        profiles.append(current_profile)

    return profiles


def parse_proxy_arg(proxy_str):
    if proxy_str is None:
        return None, None

    if ':' not in proxy_str:
        raise ValueError(f"Invalid proxy format '{proxy_str}'. Expected format: host:port")

    parts = proxy_str.split(':')
    if len(parts) != 2:
        raise ValueError(f"Invalid proxy format '{proxy_str}'. Expected format: host:port")

    host = parts[0].strip()
    try:
        port = int(parts[1].strip())
    except ValueError:
        raise ValueError(f"Invalid proxy port '{parts[1]}'. Port must be a number")

    if not host:
        raise ValueError("Proxy host cannot be empty")

    if port <= 0 or port > 65535:
        raise ValueError(f"Invalid proxy port {port}. Port must be between 1-65535")

    return host, port


def parse_args():
    parser = argparse.ArgumentParser(description='Process Burp Suite XML export.')
    parser.add_argument('-t', '--template', required=True,
                       help='Template file to load')
    parser.add_argument('--burp-requests', required=True,
                       help='Path to Burp XML exported requests')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('-o', '--output', action='append',
                       choices=['html', 'json', 'csv'],
                       help='Output format(s) - can be specified multiple times')

    parser.add_argument('--proxy', default=None,
                       help='Proxy server (format: host:port, e.g., 127.0.0.1:8080)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    parser.add_argument('--no-verify-ssl', action='store_true',
                       help='Disable SSL certificate verification (default: verify enabled)')

    args, remaining = parser.parse_known_args()

    try:
        profile_configs = parse_profile_args(remaining)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    args.profile_configs = profile_configs
    return args


def main():

    try:
        args = parse_args()

        logger = HowitzerLogger(verbose=args.verbose)
        from utils.logging import set_logger
        set_logger(logger)

        logger.info(f"Loading template: {args.template}")
        try:
            config = load_config(args.template)
        except FileNotFoundError:
            raise ConfigurationError(f"Template file not found: {args.template}")
        except Exception as e:
            raise ConfigurationError(f"Invalid YAML syntax: {e}")

        if not os.path.exists(args.burp_requests):
            raise BurpXMLError(f"Burp XML file not found: {args.burp_requests}")

        proxy_host, proxy_port = parse_proxy_arg(args.proxy)
        http_config = HTTPClientConfig(
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            timeout=args.timeout,
            verify_ssl=not args.no_verify_ssl
        )

        if args.verbose:
            logger.banner("HTTP Client Configuration")
            logger.info(f"  Proxy: {http_config.proxy_url or 'None (direct connection)'}")
            logger.info(f"  Timeout: {http_config.timeout}s")
            logger.info(f"  SSL Verification: {'Enabled' if http_config.verify_ssl else 'Disabled'}")
            print()

        http_client = HTTPClient(http_config)
        profile_processor = ProfileProcessor(config)
        match_detector = MatchDetector()
        replay_service = RequestReplayService(
            http_client=http_client,
            profile_processor=profile_processor,
            match_detector=match_detector,
            logger=logger
        )

        orchestrator = HowitzerOrchestrator(
            burp_xml_path=args.burp_requests,
            http_client=http_client,
            profile_processor=profile_processor,
            replay_service=replay_service,
            logger=logger
        )

        matches, total_requests = orchestrator.run(
            profile_configs=args.profile_configs,
            verbose=args.verbose
        )

        results_dicts = [match.to_dict() for match in matches]

        ascii_output = ASCIITableOutput()
        ascii_output.generate(results_dicts, total_requests=total_requests)

        if args.output:
            output_formatters = {
                'html': HTMLOutput(),
                'json': JSONOutput(),
                'csv': CSVOutput()
            }

            for format_name in args.output:
                formatter = output_formatters[format_name]
                filepath = formatter.generate(results_dicts, total_requests=total_requests)
                if filepath:
                    logger.info(f"{format_name.upper()} output saved to: {filepath}")

        http_client.close()
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)

    except HowitzerException as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        if 'args' in locals() and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
