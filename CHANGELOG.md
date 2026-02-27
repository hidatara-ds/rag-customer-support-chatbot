# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2024-02-27

### Added
- `.env.example` file for environment configuration template
- `docker-compose.yml` for multi-service Docker deployment
- Test suite with pytest (`tests/test_api.py`, `tests/test_utils.py`)
- `Makefile` with common development commands
- `CONTRIBUTING.md` with contribution guidelines
- `pytest.ini` for test configuration
- `CHANGELOG.md` to track project changes
- Enhanced health check endpoint with database connectivity status
- Comprehensive logging throughout the application
- `HealthResponse` schema for health check endpoint

### Changed
- Translated README.md from Indonesian to English
- Enhanced error handling in all endpoints
- Improved input validation with Pydantic field validators
- Updated `app/config.py` to use python-dotenv and load from .env file
- Enhanced `app/main.py` with better error handling and logging
- Improved `app/db.py` with error handling and logging
- Enhanced `app/llm.py` with better error handling for Ollama API calls
- Updated `app/schemas.py` with field validation constraints
- Improved `.gitignore` with project-specific entries
- Updated `requirements.txt` with testing dependencies

### Improved
- Code documentation with docstrings
- Error messages are more user-friendly
- Database operations now include proper error handling
- LLM API calls handle timeouts and connection errors gracefully
- Better separation of concerns in code structure

### Fixed
- Database URL configuration (changed from coffee_support to shoe_support)
- Product search now uses partial matching (ILIKE with wildcards)
- API title and version now configurable via environment variables

## [1.0.0] - Initial Release

### Added
- Initial FastAPI application structure
- SQLAlchemy database models
- Ollama LLM integration
- Basic chat endpoint
- Product and order endpoints
- Simple web UI
- Docker support
