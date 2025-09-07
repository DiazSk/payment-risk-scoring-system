# Story 1.2 — Implement Real AML Compliance Checking Features

**Background & Context:**
The current system lacks AML compliance features, which are essential for any professional-grade fintech platform. AML checks help detect suspicious activities and ensure regulatory compliance, reducing risk for users and stakeholders.

**Acceptance Criteria:**
1. Integrate AML compliance logic into the risk scoring pipeline.
2. Implement detection of common AML red flags (e.g., structuring, rapid movement of funds, unusual transaction patterns).
3. Update API and dashboard to display AML-related risk scores and flags.
4. Document AML compliance features and their rationale in system documentation.
5. Ensure AML checks are configurable and can be updated as regulations evolve.

**Implementation Notes:**
- Research and define AML rules relevant to payment risk scoring.
- Add AML feature engineering to data pipeline and model inputs.
- Update model training and evaluation to include AML risk scoring.
- Refactor dashboard and API outputs to show AML compliance status.
- Document AML logic and configuration options.

**Dependencies:**
- PRD: docs/prd/intro-project-analysis-and-context.md
- Data pipeline: src/data_pipeline.py, src/feature_engineering.py
- Model training: src/model_training.py
- Dashboard: dashboard/app.py, dashboard/components.py
- API: app/main.py, app/predictor.py

**Risks:**
- AML rules may require frequent updates to stay compliant with regulations.
- False positives could impact user experience if not tuned properly.

**Definition of Done:**
- AML compliance checks integrated into risk scoring pipeline.
- AML risk scores and flags displayed in API and dashboard.
- Documentation updated to explain AML features.
- Code reviewed and validated for completeness.
