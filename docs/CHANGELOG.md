# Changelog

All notable changes to the LLM Red Teaming Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- [ ] PostgreSQL database support
- [ ] Advanced analytics dashboard
- [ ] Batch scan scheduling
- [ ] Custom vulnerability definitions
- [ ] API rate limit handling improvements
- [ ] Export results to CSV/JSON
- [ ] Multi-user support with RBAC
- [ ] Integration with CI/CD pipelines

## [1.0.0] - 2026-02-26

### Added
- Initial release of LLM Red Teaming Platform
- Streamlit-based web interface
- FastAPI RESTful API backend
- Integration with DeepTeam framework
- Support for multiple LLM providers:
  - OpenAI (GPT-4, GPT-3.5, GPT-4o)
  - Azure OpenAI
  - Groq (Llama 3.x, Mixtral)
  - Anthropic Claude
  - Google Gemini
  - Local models via Ollama
- Vulnerability testing capabilities:
  - Robustness testing
  - Indirect prompt injection
  - Jailbreak attempts
  - Shell injection detection
  - Goal hijacking
  - Inter-agent communication security
  - Recursive hijacking
- Attack methods:
  - Jailbreak strategies
  - Prompt leaking
  - ROT13 encoding
  - Base64 encoding
  - Gray box attacks
  - Prompt probing
- Attack library with pre-defined prompts:
  - Ignore previous instructions
  - DAN (Do Anything Now)
  - Evil confidant
  - Translated attacks
  - Opposite day scenarios
- Custom attack builder interface
- Static attack testing mode
- PDF report generation
- SQLite database for result persistence
- Comprehensive logging system
- Session-based authentication
- Configuration management via environment variables
- Real-time scan monitoring
- Results visualization with charts
- Scan history tracking

### Enhanced
- LangChain adapter with JSON mode support for OpenAI/Azure models
- Temperature controls for evaluation vs. simulation models
- Error filtering for rate-limited and failed tests
- Enhanced response extraction using Pydantic models
- Windows async event loop compatibility fixes
- Detailed debug logging throughout the application

### Fixed
- JSON generation errors with attacker models
- Rate limit detection and handling
- Target response extraction from test cases
- Event loop cleanup errors on Windows
- Model configuration for DeepTeam integration
- Database schema initialization

### Security
- Environment-based API key management
- Session token validation
- Input sanitization for prompts
- Secure database connections
- Authentication middleware

### Documentation
- Architecture documentation
- Contributing guidelines
- Security considerations guide
- Demo creation guide
- Requirements for different environments
- Comprehensive README with setup instructions

## [0.9.0] - 2026-02-20 (Beta)

### Added
- Beta release for internal testing
- Core red teaming engine
- Basic UI with Streamlit
- OpenAI and Groq provider support
- Vulnerability scanning capabilities
- Database persistence layer
- PDF report generation

### Known Issues
- Rate limit errors not properly categorized
- Target responses showing as "N/A" in some cases
- Windows async cleanup warnings
- Limited error messages for API failures

## [0.8.0] - 2026-02-15 (Alpha)

### Added
- Initial alpha release
- Proof of concept implementation
- Basic DeepTeam integration
- Simple vulnerability testing
- Command-line interface

### Known Issues
- No persistent storage
- Limited error handling
- Single provider support only
- No authentication

## Version History Summary

| Version | Release Date | Status | Key Features |
|---------|-------------|--------|--------------|
| 1.0.0   | 2026-02-26  | Stable | Full feature release |
| 0.9.0   | 2026-02-20  | Beta   | Internal testing |
| 0.8.0   | 2026-02-15  | Alpha  | Proof of concept |

## Upgrade Guide

### From 0.9.0 to 1.0.0

1. **Database Migration**
   ```bash
   python migrate_db.py
   ```

2. **Environment Variables**
   - Add new required variables to `.env`:
     ```
     SECRET_KEY=your_secret_key_here
     LOG_LEVEL=INFO
     ```

3. **Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **Configuration**
   - Review `config/settings.py` for new settings
   - Update provider configurations if needed

### Breaking Changes

#### Version 1.0.0
- **Database Schema**: Added `error` field to results table
- **API Response Format**: Standardized JSON responses
- **Configuration**: Renamed some environment variables

## Deprecation Notices

### Version 1.0.0
- `DEEPEVAL_RESULTS_FOLDER` environment variable (use database instead)
- Legacy `/scan` endpoint (use `/api/scan` instead)

### Future Deprecations (Version 2.0.0)
- SQLite will be deprecated in favor of PostgreSQL
- Session-based auth to be replaced with JWT tokens
- Streamlit UI may be deprecated in favor of full FastAPI + React

## Contributors

### Version 1.0.0
- Core development and architecture
- DeepTeam integration
- UI/UX design
- Documentation
- Testing and bug fixes

## Support

- **Documentation**: See `docs/` folder
- **Issues**: GitHub Issues
- **Security**: See `docs/SECURITY.md` for vulnerability reporting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Semantic Versioning

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (1.X.0): New features, backwards-compatible
- **PATCH** version (1.0.X): Bug fixes, backwards-compatible

## Release Notes Format

Each release includes:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features to be removed in future
- **Removed**: Features removed in this release
- **Fixed**: Bug fixes
- **Security**: Security updates

---

**Last Updated**: February 26, 2026  
**Current Version**: 1.0.0
