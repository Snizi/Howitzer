from abc import ABC, abstractmethod


class OutputFormatter(ABC):

    @abstractmethod
    def generate(self, results, output_dir='.', total_requests=0):
        pass
