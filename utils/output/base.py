from abc import ABC, abstractmethod


class OutputFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def generate(self, results, output_dir='.', total_requests=0):
        """
        Generate output in specific format.

        Args:
            results: List of match dicts with enriched data
            output_dir: Directory to write output files (default: current)
            total_requests: Total number of requests processed

        Returns:
            str: Path to generated file (or None for stdout formatters)
        """
        pass
