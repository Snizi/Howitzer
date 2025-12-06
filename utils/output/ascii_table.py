from .base import OutputFormatter


class ASCIITableOutput(OutputFormatter):
    """ASCII table formatter for stdout display."""

    def generate(self, results, output_dir='.', total_requests=0):
        """Display results in ASCII table to stdout."""
        if not results:
            print("\n" + "="*100)
            print(f"No matching endpoints found across any profile. (Total requests: {total_requests})")
            print("="*100)
            return None

        print("\n" + "="*130)
        print(f"{'MATCHING ENDPOINTS SUMMARY':^130}")
        print("="*130)

        # Calculate column widths
        max_host = max((len(r.get('host', '')) for r in results), default=20)
        max_path = max((len(r.get('path', '')) for r in results), default=20)
        max_method = max((len(r.get('method', '')) for r in results), default=6)
        max_profile = max((len(r.get('profile', '')) for r in results), default=10)

        # Ensure minimum widths
        host_width = max(max_host, 25)
        path_width = max(max_path, 20)
        method_width = max(max_method, 6)
        profile_width = max(max_profile, 10)
        status_width = 6
        lengths_width = 20

        # Header
        header = (f"| {'HOST':<{host_width}} | {'ENDPOINT':<{path_width}} | "
                 f"{'METHOD':<{method_width}} | {'PROFILE':<{profile_width}} | "
                 f"{'STATUS':<{status_width}} | {'LENGTHS':<{lengths_width}} |")

        separator = ("+" + "-"*(host_width+2) + "+" + "-"*(path_width+2) + "+" +
                    "-"*(method_width+2) + "+" + "-"*(profile_width+2) + "+" +
                    "-"*(status_width+2) + "+" + "-"*(lengths_width+2) + "+")

        print(separator)
        print(header)
        print(separator)

        # Rows
        for result in results:
            host = result.get('host', '')
            path = result.get('path', '')
            method = result.get('method', '')
            profile = result.get('profile', '')
            status = str(result.get('status_code', ''))

            orig_len = result.get('original_length', 0)
            replay_len = result.get('replayed_length', 0)
            lengths = f"orig={orig_len}, re={replay_len}"

            # Truncate long values
            if len(host) > host_width:
                host = host[:host_width-3] + "..."
            if len(path) > path_width:
                path = path[:path_width-3] + "..."
            if len(lengths) > lengths_width:
                lengths = lengths[:lengths_width-3] + "..."

            row = (f"| {host:<{host_width}} | {path:<{path_width}} | "
                  f"{method:<{method_width}} | {profile:<{profile_width}} | "
                  f"{status:<{status_width}} | {lengths:<{lengths_width}} |")
            print(row)

        print(separator)
        print(f"\nTotal matches: {len(results)} / {total_requests} requests")
        print("="*130 + "\n")

        return None
