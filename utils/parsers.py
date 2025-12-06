import base64
import re

def decode_base64(data):
    if not data:
        return b""
    try:
        return base64.b64decode(data)
    except Exception:
        return b""


def parse_raw_request(raw_request_bytes):
    parts = raw_request_bytes.split(b'\r\n\r\n', 1)
    header_part = parts[0]
    body = parts[1] if len(parts) > 1 else b""

    headers_lines = header_part.split(b'\r\n')
    request_line = headers_lines[0]

    req_line_parts = request_line.split(b' ')
    method = req_line_parts[0].decode('utf-8')
    path = req_line_parts[1].decode('utf-8') if len(req_line_parts) > 1 else '/'
    protocol = req_line_parts[2].decode('utf-8') if len(req_line_parts) > 2 else 'HTTP/1.1'

    headers = {}
    for line in headers_lines[1:]:
        if b':' in line:
            key, value = line.split(b':', 1)
            headers[key.decode('utf-8').strip()] = value.decode('utf-8').strip()

    return method, path, protocol, headers, body

def extract_body_from_raw_response(raw_response_bytes):
    parts = raw_response_bytes.split(b'\r\n\r\n', 1)
    return parts[1] if len(parts) > 1 else b""

def parse_header_arg(header_string):
    if ':' not in header_string:
        raise ValueError(f"Invalid header format: {header_string}")

    parts = header_string.split(':', 1)
    header_name = parts[0].strip()
    header_value = parts[1].strip()

    if not header_name:
        raise ValueError("Header name cannot be empty")

    return (header_name, header_value)

def manipulate_headers(original_headers, profile_config, replace_headers_cli, add_headers_cli):
    if profile_config.get('original_headers', 'keep') == 'remove':
        result_headers = {}
    else:
        result_headers = original_headers.copy()

    replace_map = {name.lower(): (name, value) for name, value in replace_headers_cli}
    add_map = {name.lower(): (name, value) for name, value in add_headers_cli}

    profile_replace = [item['header'].lower() for item in profile_config.get('replace', [])]
    profile_add = [item['header'].lower() for item in profile_config.get('add', [])]

    for header_name in profile_replace:
        keys_to_remove = [k for k in result_headers.keys() if k.lower() == header_name]
        for key in keys_to_remove:
            del result_headers[key]

        if header_name in replace_map:
            original_case_name, value = replace_map[header_name]
            result_headers[original_case_name] = value

    for header_name in profile_add:
        if header_name in add_map:
            original_case_name, value = add_map[header_name]
            keys_to_remove = [k for k in result_headers.keys() if k.lower() == header_name]
            for key in keys_to_remove:
                del result_headers[key]
            result_headers[original_case_name] = value

    missing_replace = [h for h in profile_replace if h not in replace_map]
    missing_add = [h for h in profile_add if h not in add_map]

    if missing_replace:
        raise ValueError(f"Profile requires replacement for headers {missing_replace} but no CLI values provided")
    if missing_add:
        raise ValueError(f"Profile requires adding headers {missing_add} but no CLI values provided")

    return result_headers
