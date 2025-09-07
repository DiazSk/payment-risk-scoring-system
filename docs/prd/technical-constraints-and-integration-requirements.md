# Technical Constraints and Integration Requirements

### Existing Technology Stack

**Languages**: Python 3.9+  
**Frameworks**: FastAPI (backend), Streamlit (dashboard), scikit-learn, XGBoost  
**Database**: File-based storage (pickle models, CSV data, JSON metadata)  
**Infrastructure**: Railway Cloud deployment, Docker containerization  
**External Dependencies**: pandas, numpy, matplotlib, seaborn, requests

### Integration Approach

**Database Integration Strategy**: Extend existing pickle/JSON storage pattern with new AML and velocity model artifacts while maintaining current model metadata structure

**API Integration Strategy**: Add new endpoints (`/aml_check`, `/velocity_analysis`) to existing FastAPI router while preserving current `/predict` and `/batch_predict` functionality

**Frontend Integration Strategy**: Enhance Streamlit dashboard with new AML monitoring and velocity analysis tabs using existing component architecture and styling patterns

**Testing Integration Strategy**: Extend current test suite (15/15 passing) with AML and velocity-specific test cases while maintaining 100% coverage target

### Code Organization and Standards

**File Structure Approach**: Follow existing pattern with new modules in `src/` (aml_engine.py, velocity_checker.py) and enhanced `app/models.py` for new request/response schemas

**Naming Conventions**: Maintain current snake_case for functions/variables, PascalCase for classes, following established patterns in existing codebase

**Coding Standards**: Continue current practices with comprehensive docstrings, type hints, error handling patterns, and logging consistency

**Documentation Standards**: Extend existing README/docs pattern with new sections for AML and velocity features while maintaining current badge/metrics format

### Deployment and Operations

**Build Process Integration**: Enhance existing Dockerfile and requirements.txt with new dependencies while maintaining Railway-compatible build times under 10 minutes

**Deployment Strategy**: Maintain current Railway auto-deployment from main branch with zero-downtime rolling updates, extend health checks for new features

**Monitoring and Logging**: Extend existing logging infrastructure with AML/velocity-specific log categories while maintaining current performance monitoring endpoints

**Configuration Management**: Enhance existing environment variable pattern with new AML thresholds and velocity parameters while maintaining Railway configuration compatibility

### Risk Assessment and Mitigation

**Technical Risks**: 
- Model retraining may not achieve realistic 87% target immediately
- New features could impact existing sub-100ms response times
- Memory usage may exceed free tier limits with additional model loading

**Integration Risks**:
- Current artificial metrics are deeply embedded in training pipeline
- Existing perfect model artifacts may need complete regeneration
- Dashboard metrics displays assume current unrealistic performance levels

**Deployment Risks**:
- Railway free tier has compute/memory constraints for enhanced features
- Zero-downtime deployment challenging with model artifact changes
- Current health checks may not validate new AML/velocity functionality

**Mitigation Strategies**:
- Implement feature flags for gradual rollout of realistic metrics
- Add performance monitoring specifically for new feature impact
- Create model artifact migration strategy for seamless transition
- Implement comprehensive integration testing before deployment
- Design graceful degradation if AML/velocity services become unavailable
