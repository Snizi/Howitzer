# Howitzer Development Guide

This guide provides instructions for setting up the development environment, running tests, and contributing to the Howitzer project.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd Howitzer
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Project Structure

-   `main.py`: Application entry point and CLI parsing.
-   `utils/`: Core utilities and business logic.
    -   `orchestrator.py`: Main workflow coordination.
    -   `profile_processor.py`: Profile loading and application.
    -   `match_detector.py`: Authorization bypass detection logic.
    -   `services/replay_service.py`: Request replay orchestration.
    -   `burp_parser.py`: Burp Suite XML parsing.
    -   `http_client.py`: HTTP client wrapper.
    -   `models.py`: Domain models (dataclasses).
    -   `output/`: Output formatters (HTML, JSON, CSV, ASCII).
-   `tests/`: Unit and integration tests.

## Testing

Howitzer uses `unittest` for testing.

### Running all tests
```bash
python -m unittest discover tests
```

### Running specific tests
```bash
python -m unittest tests.test_orchestrator
```

## Contribution Guidelines

1.  **Code Style:** Follow PEP 8 guidelines.
2.  **Testing:** Ensure all new features include unit tests. Run existing tests to prevent regressions.
3.  **Documentation:** Update docstrings and documentation files for any changes.
4.  **Pull Requests:** Submit PRs with clear descriptions of changes.

## Architecture

See [Architecture Documentation](architecture.md) for detailed design diagrams.
