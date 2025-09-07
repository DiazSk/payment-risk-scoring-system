# Story 1.1 — Remove Artificial/Fake Metrics and Replace with Honest, Defensible Performance Numbers

**Background & Context:**
The current system displays artificially inflated metrics (e.g., 92.3% fraud detection rate, 1.000 scores for all metrics) in training reports and dashboards. This creates professional reputation risk and undermines the credibility of the platform. The goal is to transform the system into a legitimate, professional-grade payment risk scoring platform with honest, realistic, and defensible performance metrics.

**Acceptance Criteria:**
1. All code and documentation referencing fake or artificially perfect metrics must be identified and removed.
2. Training reports, dashboards, and API endpoints must display actual model performance metrics (accuracy, precision, recall, F1) based on real test data.
3. Update documentation to reflect the change from artificial to honest metrics.
4. Ensure that all displayed metrics can be defended in technical interviews.
5. No references to fake metrics remain in code, documentation, or user-facing outputs.

**Implementation Notes:**
- Review all model training, evaluation, and reporting code for hardcoded or artificially inflated metrics.
- Update model evaluation logic to compute and display real metrics from test/validation datasets.
- Refactor dashboard and API outputs to show honest metrics.
- Update training report files and documentation to remove references to fake metrics.
- Add comments and documentation explaining the change and rationale.

**Dependencies:**
- PRD: docs/prd/intro-project-analysis-and-context.md
- Training reports: models/training_report_*.txt, reports/model_performance_report.txt, etc.
- Dashboard: dashboard/app.py, dashboard/components.py
- API: app/main.py, app/predictor.py

**Risks:**
- Revealing lower, but realistic, performance metrics may impact perceived system quality.
- Requires careful communication in documentation to explain the improvement in integrity.

**Definition of Done:**
- All fake metrics removed from code, reports, and documentation.
- Honest metrics are displayed everywhere performance is shown.
- Documentation updated to reflect the change.
- Code reviewed and validated for completeness.
