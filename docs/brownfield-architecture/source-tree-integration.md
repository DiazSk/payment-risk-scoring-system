# Source Tree Integration

### Existing Project Structure
```
payment-risk-scoring-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI router - will add new endpoints
│   ├── models.py               # Pydantic models - will extend with AML/velocity schemas
│   ├── predictor.py            # ML predictions - will integrate new model loading
│   └── monitoring.py           # System monitoring - will track new metrics
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py        # Data processing - preserved
│   ├── evaluation.py           # Model evaluation - will enhance with realistic metrics
│   ├── feature_engineering.py  # 82-feature pipeline - will extend with AML/velocity features
│   ├── model_training.py       # Training pipeline - will add realistic model training
│   └── utils.py               # Utilities - preserved
├── dashboard/
│   ├── app.py                 # Streamlit main - will add new pages
│   └── components.py          # UI components - will extend with AML/velocity widgets
├── models/
│   └── model_metadata.json    # Model config - will extend with new model references
└── tests/
    ├── test_api.py            # API tests - will add new endpoint tests
    └── test_complete_pipeline.py # Integration tests - will enhance coverage
```

### New File Organization
```
payment-risk-scoring-system/
├── app/
│   ├── main.py                 # Enhanced with /aml_check, /velocity_analysis endpoints
│   ├── models.py               # Extended with AMLResult, VelocityMetrics, EnhancedResponse
│   ├── predictor.py            # Enhanced with realistic metrics integration
│   └── monitoring.py           # Enhanced with AML/velocity monitoring
├── src/
│   ├── aml_engine.py           # NEW - AML compliance analysis engine
│   ├── velocity_checker.py     # NEW - Transaction velocity monitoring
│   ├── metrics_engine.py       # NEW - Realistic metrics generation
│   ├── feature_engineering.py  # Enhanced with AML/velocity feature extraction
│   ├── model_training.py       # Enhanced with realistic model training
│   └── evaluation.py           # Enhanced with honest performance evaluation
├── dashboard/
│   ├── app.py                 # Enhanced with AML monitoring and velocity analysis pages
│   ├── components.py          # Extended with AML charts, velocity graphs, realistic metric displays
│   └── pages/                 # NEW folder for organized page components
│       ├── aml_monitoring.py   # NEW - AML compliance dashboard
│       └── velocity_analysis.py # NEW - Velocity monitoring dashboard
├── models/
│   ├── aml_classifier.pkl      # NEW - AML pattern detection model
│   ├── velocity_analyzer.pkl   # NEW - Velocity risk assessment model
│   ├── aml_metadata.json      # NEW - AML model configuration
│   ├── velocity_metadata.json # NEW - Velocity analysis parameters
│   └── model_metadata.json    # Enhanced with references to new models
├── tests/
│   ├── test_aml_engine.py     # NEW - AML functionality tests
│   ├── test_velocity_checker.py # NEW - Velocity analysis tests
│   ├── test_realistic_metrics.py # NEW - Metrics validation tests
│   ├── test_api.py            # Enhanced with new endpoint tests
│   └── test_complete_pipeline.py # Enhanced with comprehensive integration tests
└── docs/
    ├── AWS_DEPLOYMENT.md       # NEW - AWS infrastructure documentation
    └── MIGRATION_GUIDE.md      # NEW - Railway to AWS migration guide
```

### Integration Guidelines

**File Naming:** Maintains existing snake_case convention (`aml_engine.py`, `velocity_checker.py`) consistent with current `feature_engineering.py` pattern

**Folder Organization:** Follows established pattern with business logic in `src/`, API layer in `app/`, UI components in `dashboard/`, preserving existing separation of concerns

**Import/Export Patterns:** New modules will follow existing import structure:
- `from src.aml_engine import AMLEngine` (matches current `from src.feature_engineering import FeatureEngineer`)
- Maintain relative imports within packages
- Use absolute imports for cross-package dependencies
