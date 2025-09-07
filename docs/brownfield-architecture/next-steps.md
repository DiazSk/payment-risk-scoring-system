# Next Steps

### Story Manager Handoff

**Prompt for Story Manager:**
"Please implement the Payment Risk Scoring System Brownfield Enhancement using the comprehensive architecture documented in `docs/brownfield-architecture.md`. 

**Key Integration Requirements Validated:**
- Maintain existing FastAPI router patterns in `app/main.py` when adding new endpoints
- Extend current 82-feature engineering pipeline in `src/feature_engineering.py` for AML/velocity features
- Preserve backward compatibility for all existing `/predict` and `/batch_predict` API contracts
- Follow existing Pydantic model patterns in `app/models.py` for new AML and velocity schemas

**Existing System Constraints Based on Project Analysis:**
- Railway free tier memory limit (500MB) - monitor model artifact loading
- Sub-150ms response time requirement - validate with new AML/velocity processing
- File-based storage pattern (pickle/JSON) - extend existing metadata structure
- Zero-downtime deployment requirement - use Railway's existing rollback capabilities

**First Story to Implement:** Story 1.1 (Remove Artificial Metrics) with integration checkpoints:
1. Verify existing model training pipeline in `src/model_training.py` before modifications
2. Ensure new realistic models maintain existing pickle storage patterns
3. Validate API response compatibility through existing test suite
4. Confirm memory usage stays within Railway limits

**Critical:** Maintain existing system integrity throughout implementation. Each story must preserve current functionality while adding enhancements."

### Developer Handoff

**Prompt for Developer Implementation:**
"Begin implementing the brownfield enhancement following the architecture in `docs/brownfield-architecture.md` and existing coding standards analyzed from the project.

**Architecture Reference and Coding Standards:**
- Follow existing Python PEP 8 patterns evident in `src/` modules
- Maintain current pytest testing organization in `tests/` directory  
- Use existing Pydantic validation patterns from `app/models.py`
- Preserve current logging integration with `app/monitoring.py`

**Integration Requirements with Existing Codebase:**
- Extend `app/main.py` FastAPI router with new endpoints following existing route patterns
- Add new modules in `src/` directory: `aml_engine.py`, `velocity_checker.py`, `metrics_engine.py`
- Enhance `src/feature_engineering.py` with AML/velocity features while preserving 82-feature pipeline
- Extend `dashboard/components.py` with new visualization components following existing styling

**Technical Decisions Based on Project Constraints:**
- Use existing pandas/NumPy stack for AML transaction analysis (no new dependencies)
- Maintain current pickle model storage pattern with enhanced metadata
- Follow existing error handling through FastAPI middleware
- Preserve Railway deployment compatibility with current Docker patterns

**Compatibility Requirements with Verification Steps:**
1. **API Compatibility:** Run existing `tests/test_api.py` after each endpoint addition
2. **Model Integration:** Verify pickle loading performance within memory constraints  
3. **Response Time:** Benchmark new features against 150ms requirement
4. **Backward Compatibility:** Ensure existing consumers receive identical responses

**Implementation Sequencing:** Start with realistic metrics (Story 1.1), then AML features (Story 1.2), velocity checking (Story 1.3), maintaining system stability throughout."

---

**Architecture Document Complete!** 

This comprehensive brownfield enhancement architecture provides the technical foundation for transforming your payment risk scoring system from artificial metrics to a professional, defensible platform with real AML and velocity checking capabilities. The architecture preserves your sophisticated FastAPI/Streamlit foundation while enabling the critical enhancements needed for professional credibility and regulatory compliance.
