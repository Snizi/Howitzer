import os
from datetime import datetime, timezone
from .base import OutputFormatter


class HTMLOutput(OutputFormatter):

    def generate(self, results, output_dir='.', total_requests=0):
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"Howitzer-results-{timestamp}.html"
        filepath = os.path.join(output_dir, filename)

        hosts = {}
        for result in results:
            host = result.get('host', 'Unknown Host')
            if host not in hosts:
                hosts[host] = []
            hosts[host].append(result)

        profiles = sorted(set(r.get('profile', '') for r in results))

        html = self._generate_html(hosts, results, profiles, total_requests)

        try:
            with open(filepath, 'w') as f:
                f.write(html)
            return filepath
        except (IOError, PermissionError) as e:
            from utils.logging import get_logger
            get_logger().error(f"Error writing HTML file: {e}")
            return None

    def _generate_html(self, hosts, all_results, profiles, total_requests=0):
        generated_time = datetime.now(timezone.utc).isoformat() + 'Z'
        total_matches = len(all_results)
        unique_hosts = len(hosts)
        profile_list = ', '.join(profiles) if profiles else 'None'

        host_sections = []
        for host, matches in sorted(hosts.items()):
            rows = []
            for match in matches:
                path = match.get('path', '')
                query = match.get('query', '')
                endpoint = f"{path}?{query}" if query else path

                method = match.get('method', '')
                profile = match.get('profile', '')
                status = match.get('status_code', '')
                orig_len = match.get('original_length', 0)
                replay_len = match.get('replayed_length', 0)
                timestamp = match.get('timestamp', '')

                status_class = self._get_status_class(status)

                rows.append(f"""
                    <tr>
                        <td>{self._escape_html(endpoint)}</td>
                        <td class="method">{self._escape_html(method)}</td>
                        <td>{self._escape_html(profile)}</td>
                        <td class="{status_class}">{status}</td>
                        <td>orig={orig_len}, replay={replay_len}</td>
                        <td class="timestamp">{timestamp}</td>
                    </tr>
                """)

            host_sections.append(f"""
                <section class="host-section">
                    <h2>{self._escape_html(host)}</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Endpoint</th>
                                <th>Method</th>
                                <th>Profile</th>
                                <th>Status Code</th>
                                <th>Response Lengths</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(rows)}
                        </tbody>
                    </table>
                </section>
            """)

        if not all_results:
            host_sections = ['<p class="no-results">No matching endpoints found.</p>']

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Howitzer Security Test Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color:
            background:
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}

        h1 {{
            color:
            border-bottom: 3px solid
            padding-bottom: 15px;
            margin-bottom: 25px;
            font-size: 2em;
        }}

        h2 {{
            color:
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-left: 4px solid
            padding-left: 12px;
        }}

        .summary {{
            background:
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
            border-left: 4px solid
        }}

        .summary p {{
            margin: 8px 0;
            font-size: 1.05em;
        }}

        .summary strong {{
            color:
            font-weight: 600;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background: white;
        }}

        thead {{
            background:
            color: white;
        }}

        th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 10px 12px;
            border-bottom: 1px solid
        }}

        tbody tr:hover {{
            background:
        }}

        tbody tr:nth-child(even) {{
            background:
        }}

        tbody tr:nth-child(even):hover {{
            background:
        }}

        .method {{
            font-weight: 600;
            color:
        }}

        .timestamp {{
            font-size: 0.9em;
            color:
        }}

        .status-success {{
            color:
            font-weight: 600;
        }}

        .status-redirect {{
            color:
            font-weight: 600;
        }}

        .status-client-error {{
            color:
            font-weight: 600;
        }}

        .status-server-error {{
            color:
            font-weight: 600;
        }}

        .host-section {{
            margin-bottom: 40px;
        }}

        .no-results {{
            text-align: center;
            padding: 40px;
            color:
            font-size: 1.2em;
        }}

        .warning {{
            background:
            border: 1px solid
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
            color:
        }}

        .warning strong {{
            display: block;
            margin-bottom: 5px;
        }}

        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid
            text-align: center;
            color:
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Howitzer - Authorization Bypass Detection Results</h1>

        <div class="warning">
            <strong>Security Notice:</strong>
            This report contains sensitive security testing results. Handle with care and restrict access to authorized personnel only.
        </div>

        <div class="summary">
            <p><strong>Generated:</strong> {generated_time}</p>
            <p><strong>Total Matches:</strong> {total_matches} / {total_requests} requests</p>
            <p><strong>Unique Hosts:</strong> {unique_hosts}</p>
            <p><strong>Profiles Used:</strong> {profile_list}</p>
        </div>

        {''.join(host_sections)}

        <footer>
            <p>Generated by Howitzer - Authorization Bypass Detection Tool</p>
            <p>Report generated at {generated_time}</p>
        </footer>
    </div>
</body>
</html>"""

        return html_template

    def _get_status_class(self, status):
        try:
            status_int = int(status)
            if 200 <= status_int < 300:
                return 'status-success'
            elif 300 <= status_int < 400:
                return 'status-redirect'
            elif 400 <= status_int < 500:
                return 'status-client-error'
            elif 500 <= status_int < 600:
                return 'status-server-error'
        except (ValueError, TypeError):
            pass
        return ''

    def _escape_html(self, text):
        if not text:
            return ''
        text = str(text)
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
