# Introduction

This document outlines the architectural approach for enhancing the Payment Risk Scoring System with realistic metrics, AML compliance, and velocity checking capabilities. Its primary goal is to serve as the guiding architectural blueprint for AI-driven development of new features while ensuring seamless integration with the existing FastAPI/Streamlit system.

**Relationship to Existing Architecture:**
This document supplements the existing project architecture documented in ARCHITECTURE.md by defining how new AML and velocity components will integrate with current fraud detection systems. Where conflicts arise between new realistic metrics and existing perfect-score patterns, this document provides guidance on maintaining system integrity while implementing honest performance reporting.

### Current Project State
- **Primary Purpose:** Credit card fraud detection system deployed on Railway Cloud
- **Current Tech Stack:** Python 3.9+, FastAPI (backend), Streamlit (dashboard), scikit-learn, XGBoost
- **Architecture Style:** Microservices with REST API and file-based storage
- **Deployment Method:** Railway Cloud with Docker containerization

### Available Documentation
- ✅ Tech Stack Documentation - Found in ARCHITECTURE.md and code structure
- ✅ Source Tree/Architecture - Comprehensive ARCHITECTURE.md with microservices flow
- ✅ API Documentation - FastAPI auto-generated docs at /docs endpoint
- ✅ External API Documentation - Railway deployment docs
- ❌ Coding Standards - Not explicitly documented
- ❌ UX/UI Guidelines - No formal design system documented
- ❌ Technical Debt Documentation - Critical gap: no documentation of the fake metrics issue

### Identified Constraints
- Railway free tier compute/memory limitations (500MB limit)
- Sub-150ms response time requirements
- Existing API contract compatibility
- File-based storage pattern (pickle models, CSV data, JSON metadata)

### Change Log
| Change | Date | Version | Description | Author |
|--------|------|---------|-------------|--------|
| Initial Architecture | 2025-09-07 | v1.0 | Brownfield enhancement architecture for realistic metrics and AML features | Winston (Architect) |
