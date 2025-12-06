import json
import os
from datetime import datetime, timezone
from .base import OutputFormatter


class JSONOutput(OutputFormatter):

    def generate(self, results, output_dir='.', total_requests=0):
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"Howitzer-results-{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        output_data = {
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'total_matches': len(results),
            'total_requests': total_requests,
            'matches': results
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(output_data, f, indent=2)
            return filepath
        except (IOError, PermissionError) as e:
            from utils.logging import get_logger
            get_logger().error(f"Error writing JSON file: {e}")
            return None
