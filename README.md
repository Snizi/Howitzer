# Howitzer

Howitzer is a Python-based security tool designed to detect authorization bypass vulnerabilities. It works by replaying HTTP requests captured from Burp Suite with different user profiles (credentials) and comparing the response lengths to identify potential access control issues.

## Features

- **Burp Suite Integration**: Parses XML exports directly from Burp Suite.
- **Profile Management**: Define multiple user profiles with specific header manipulation strategies (e.g., swapping Authorization tokens, Cookies).
- **Automated Replay**: Automatically replays requests with different profiles.
- **Match Detection**: Identifies potential vulnerabilities by comparing response body lengths.
- **Flexible Configuration**: Uses YAML templates to define profiles and rules.

## Prerequisites

- Python 3.8 or higher
- Burp Suite (to capture and export requests)

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/howitzer.git
   cd howitzer
   ```

2. Install the package:
   ```bash
   pip install .
   ```

   This will install `howitzer` and its dependencies (`requests`, `PyYAML`).

### Development Setup

If you want to modify the code:

```bash
pip install -e .
```

## Usage

After installation, you can run the tool using the `howitzer` command.

### Basic Syntax

```bash
howitzer -t <template.yaml> --burp-requests <requests.xml> -p <profile_name> -rH "Header: Value"
```

### Arguments

- `-t, --template`: Path to the YAML template file defining profiles.
- `--burp-requests`: Path to the XML file exported from Burp Suite.
- `-p, --profile`: Name of the profile to use (must match a profile in `template.yaml`).
- `-rH, --replace-header`: Value for a header specified in the profile's `replace` list.
- `-aH, --add-header`: Value for a header specified in the profile's `add` list.
- `-v, --verbose`: Enable verbose output.
- `-o, --output`: Output format (html, json, csv). Can be used multiple times.
- `--proxy`: Proxy server to use (e.g., `127.0.0.1:8080`).
- `--no-verify-ssl`: Disable SSL certificate verification.

### Example

1. **Capture Requests in Burp Suite**:
   - Configure your browser to use Burp Suite as a proxy (typically `127.0.0.1:8080`).
   - Log in to the application using the **highest privilege account** (e.g., admin, superuser).
   - Navigate through all features and pages of the application while Burp Suite logs all requests in the Proxy tab.
   - Once you've explored the application thoroughly, go to the **Target** tab in Burp Suite.
   - Find and expand the target host in the site map.
   - Select all requests for that host by pressing **Ctrl+A** (or Cmd+A on Mac).
   - Right-click on the selected requests and choose **"Save items"**.
   - In the save dialog, ensure **"Base64-encode request and response"** is checked.
   - Save the file as XML (e.g., `requests.xml`).

2. **Create Template (`template.yaml`)**:
   ```yaml
   profiles:
     moderator:
       description: "Moderator of the application, checking against admin requests."
       original_headers: keep
       replace:
         - header: Authorization
     user:
       description: "Regular user of the application, checking against admin requests."
       original_headers: keep
       replace:
         - header: Authorization
   ```

3. **Run Howitzer**:
   ```bash
   # Test as user1
   howitzer -t template.yaml --burp-requests requests.xml \
     -p user1 -rH "Authorization: Bearer <token_for_user1>"

   # Test as multiple users
   howitzer -t template.yaml --burp-requests requests.xml \
     -p user1 -rH "Authorization: Bearer <token1>" \
     -p admin -rH "Cookie: session=admin_session"
   ```

## Configuration

### Template Structure

The `template.yaml` file defines how Howitzer should manipulate headers for each profile.

```yaml
profiles:
  <profile_name>:
    description: "<description>"
    original_headers: <keep|remove>
    replace:
      - header: <Header-Name>
    add:
      - header: <Header-Name>
```

- `original_headers`:
    - `keep`: Retains original headers from the Burp request, except those in `replace`.
    - `remove`: Discards all original headers.
- `replace`: List of headers to replace. Values are provided via CLI `-rH`.
- `add`: List of headers to add. Values are provided via CLI `-aH`.

## Development

To run tests:

```bash
python -m unittest discover tests
```

## License

See [LICENSE](LICENSE) file.
