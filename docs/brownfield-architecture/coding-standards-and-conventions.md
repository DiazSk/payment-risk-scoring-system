# Coding Standards and Conventions

### Existing Standards Compliance

**Code Style:** Python PEP 8 compliance with snake_case for functions/variables, PascalCase for classes (evident in `app/models.py` Pydantic models, `src/feature_engineering.py` function naming)

**Linting Rules:** Implicit Python standards based on existing code patterns - consistent indentation (4 spaces), docstring usage for functions, type hints for function parameters and returns

**Testing Patterns:** pytest framework with organized test structure in `tests/` directory, descriptive test names (e.g., `test_complete_pipeline.py`), comprehensive coverage approach (15/15 passing tests mentioned in PRD)

**Documentation Style:** Comprehensive docstrings for classes and functions, inline comments for complex logic, README.md with deployment instructions and performance metrics

### Enhancement-Specific Standards

- **AML Module Standards:** All AML functions must include compliance rationale in docstrings, suspicious pattern detection must be clearly documented with business logic explanations
- **Velocity Analysis Standards:** Time window calculations must include timezone handling, baseline deviation algorithms must be mathematically documented
- **Realistic Metrics Standards:** All metric calculations must include formula documentation, performance claims must be verifiable through automated tests
- **Error Handling Standards:** New features must include graceful degradation patterns, external API failures must not impact core fraud detection functionality

### Critical Integration Rules

**Existing API Compatibility:** All new endpoints must follow existing FastAPI route patterns with Pydantic validation, maintain existing error response formats, preserve current authentication approach

**Database Integration:** New model artifacts must follow existing pickle serialization patterns, metadata must extend current JSON structure without breaking existing parsing, file naming must follow existing convention (`{feature}_{model_type}.pkl`)

**Error Handling:** New components must integrate with existing `app/monitoring.py` logging patterns, error messages must follow current JSON error response format, exception handling must preserve existing API stability

**Logging Consistency:** 
- Use existing logging configuration and format
- New features must log to same destinations as current system
- Performance metrics must integrate with existing monitoring endpoints
- AML compliance events require audit-level logging for regulatory purposes
