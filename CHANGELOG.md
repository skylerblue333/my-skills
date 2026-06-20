# Changelog

All notable changes to the Stock Buddy Skills Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-20

### Added
- Initial release of Stock Buddy Skills Suite
- 14 specialized analysis skills for DSE stocks
- MCP server with stdio and HTTP transports
- Data adapter layer with pluggable providers
- Multi-agent system for coordinated analysis
- Interactive HTML checklists for momentum and investment criteria
- Price prediction engine with technical and fundamental targets
- DSE market localization with sector benchmarks
- CI/CD pipeline with GitHub Actions
- Docker packaging and deployment
- Comprehensive test infrastructure
- Full documentation suite

### Features
- **Core Skills**: All 14 analysis skills operational
- **Data Layer**: FileProvider, DSEProvider (stub), MockProvider
- **Caching**: In-memory cache with TTL support
- **Rate Limiting**: Token bucket algorithm
- **Agents**: MomentumAgent, InvestmentAgent, BusinessAgent
- **UI**: Interactive checklists with explanations
- **Predictions**: Buy zones, sell targets, stop loss calculations
- **Localization**: DSE circuit breakers, sector P/E benchmarks

### Security
- Educational disclaimers on all outputs
- No hardcoded credentials
- Rate limiting on data access
- Container runs as non-root user
- Dependency scanning enabled

## [0.9.0] - 2024-06-19 (Pre-release)

### Added
- Core skill implementations
- Basic MCP server
- Initial test framework

## [0.1.0] - 2024-06-15 (Alpha)

### Added
- Project structure
- RCF documentation
- Initial skill templates