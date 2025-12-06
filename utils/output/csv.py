import csv
import os
from datetime import datetime
from .base import OutputFormatter


class CSVOutput(OutputFormatter):
    """CSV formatter for tabular output."""

    def generate(self, results, output_dir='.', total_requests=0):
        """Generate CSV output file."""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"Howitzer-results-{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        fieldnames = [
            'host', 'path', 'query', 'method', 'profile',
            'original_length', 'replayed_length', 'status_code', 'timestamp'
        ]

        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                if results:
                    writer.writerows(results)

            return filepath
        except (IOError, PermissionError) as e:
            from utils.logging import get_logger
            get_logger().error(f"Error writing CSV file: {e}")
            return None
