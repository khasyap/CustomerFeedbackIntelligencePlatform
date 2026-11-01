# SOURCE CODE & ASSET MANIFEST

```
customer-feedback-intelligence/ (d:\yotta\)
│
├── frontend/                                   # React 19 + TypeScript + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CreateActionModal.tsx           # Provision action item dialog
│   │   │   ├── FeedbackDetailModal.tsx         # Full drill-down and manual correction modal
│   │   │   ├── Sidebar.tsx                     # 11-view enterprise navigation sidebar
│   │   │   └── StatCard.tsx                    # Reusable KPI stat card with trends
│   │   ├── pages/
│   │   │   ├── ActionManagementPage.tsx        # Action items & lifecycle state tracker
│   │   │   ├── DataManagementPage.tsx          # Data generator, batch runner, exports
│   │   │   ├── DataQualityPage.tsx             # Exception management dashboard
│   │   │   ├── FeedbackExplorerPage.tsx        # Searchable, filterable feedback repository
│   │   │   ├── ModelEvaluationPage.tsx         # Confusion matrix & benchmark metrics
│   │   │   ├── OverviewPage.tsx                # Executive KPIs, donuts, themes & trends
│   │   │   ├── SentimentAnalyticsPage.tsx      # Net Sentiment Score (NSS) rankings
│   │   │   ├── ServicePrioritiesPage.tsx       # 5-factor weighted priority recommendation
│   │   │   ├── SettingsPage.tsx                # Runtime settings & compliance parameters
│   │   │   ├── ThemeIntelligencePage.tsx       # 18-theme taxonomy & heatmap
│   │   │   └── TrendDetectionPage.tsx          # Time-series & sentiment shift alerts
│   │   ├── services/
│   │   │   └── api.ts                          # REST API client connecting to FastAPI
│   │   ├── types/
│   │   │   └── index.ts                        # Complete TypeScript interfaces
│   │   ├── App.tsx                             # Root dashboard shell
│   │   ├── main.tsx                            # React DOM entrypoint
│   │   └── index.css                           # Tailwind CSS v4 styling & dark theme
│   ├── package.json                            # Frontend npm dependencies
│   ├── tsconfig.json                           # TypeScript root configuration
│   ├── tsconfig.app.json                       # Bundler TypeScript compiler options
│   └── vite.config.ts                          # Vite 8 config with Tailwind v4 & proxy
│
├── backend/                                    # Python FastAPI Backend Architecture
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py                     # Unified API router
│   │   │   ├── action_routes.py                # Action CRUD & lifecycle validation
│   │   │   ├── analytics_routes.py             # Overview KPIs, trends, priorities
│   │   │   ├── evaluation_routes.py            # Benchmark & evaluation runs
│   │   │   ├── export_routes.py                # CSV, JSON, reproducibility checks
│   │   │   ├── feedback_routes.py              # Feedback explorer & manual correction
│   │   │   ├── master_routes.py                # Customers, products, channels, themes
│   │   │   ├── ml_routes.py                    # Inference, batch processing, telemetry
│   │   │   └── quality_routes.py               # Data quality exception triage
│   │   ├── ml/
│   │   │   ├── __init__.py                     # ML package exports
│   │   │   ├── evaluation.py                   # Scientific metrics calculation
│   │   │   ├── preprocessor.py                 # Multilingual text cleaning & PII masking
│   │   │   ├── sentiment_classifier.py         # TF-IDF Logistic Regression & explanations
│   │   │   ├── sentiment_model.joblib          # Trained ML model artifact
│   │   │   └── theme_classifier.py             # Hybrid multi-label extraction engine
│   │   ├── models/
│   │   │   ├── __init__.py                     # Database models export
│   │   │   └── entities.py                     # 18 relational entities + shift alerts
│   │   ├── schemas/
│   │   │   ├── __init__.py                     # Pydantic schemas export
│   │   │   ├── actions.py                      # ActionItem schemas
│   │   │   ├── analytics.py                    # KPI & breakdown schemas
│   │   │   ├── feedback.py                     # Feedback item & correction schemas
│   │   │   └── quality.py                      # Exception & evaluation schemas
│   │   ├── services/
│   │   │   ├── __init__.py                     # Services package export
│   │   │   ├── audit_service.py                # Validated lifecycle & audit logger
│   │   │   ├── data_generator.py               # Seed 20261022 deterministic generator
│   │   │   ├── priority_engine.py              # 5-factor priority calculation engine
│   │   │   ├── trend_detector.py               # Time-series shift detection engine
│   │   │   └── validation_service.py           # 10 automated data quality rules
│   │   ├── config.py                           # App settings & hyperparameters
│   │   ├── database.py                         # SQLAlchemy engine & session maker
│   │   └── main.py                             # FastAPI application entrypoint
│   └── requirements.txt                        # Backend Python dependencies
│
├── data/                                       # Data Storage & Artifacts
│   ├── ground_truth/
│   │   ├── ground_truth.csv                    # Isolated ground truth labels (CSV)
│   │   └── ground_truth.json                   # Isolated ground truth labels (JSON)
│   ├── evaluation/
│   │   └── evaluation_benchmark.json           # Holdout test split evaluation metrics
│   └── exports/                                # Analytical data dumps
│
├── database/                                   # Database Seeds & Migrations
│   ├── seed/
│   │   └── seed.sql                            # Full database SQL seed export
│   └── migrations/                             # Schema evolution scripts
│
├── scripts/                                    # Automation CLI Utility Scripts
│   ├── evaluate_models.py                      # Empirical model evaluation CLI
│   ├── generate_data.py                        # Deterministic synthetic data CLI
│   ├── process_feedback.py                     # Batch NLP processing CLI
│   ├── train_models.py                         # Sentiment model training CLI
│   ├── validate_data.py                        # Data quality audit CLI
│   └── verify_reproducibility.py               # Deterministic seed verification CLI
│
├── tests/                                      # Automated Pytest Test Suite
│   ├── data_quality/
│   │   └── test_data_integrity.py              # Primary key, foreign key & split tests
│   ├── integration/
│   │   └── test_api_endpoints.py               # End-to-end FastAPI endpoint tests
│   └── unit/
│       ├── test_lifecycle_and_audit.py         # Lifecycle state machine tests
│       └── test_ml_models.py                   # NLP model, PII & theme tests
│
├── docs/                                       # System Documentation
│   ├── API_DOCUMENTATION.md                    # REST API endpoint reference
│   ├── DATABASE_SCHEMA.md                      # Mermaid ER diagram & relational schema
│   ├── DATA_DICTIONARY.md                      # Comprehensive 18-entity data dictionary
│   ├── DATA_GENERATION.md                      # Synthetic generation & taxonomy guide
│   ├── MODEL_DOCUMENTATION.md                  # Machine learning architecture & benchmarks
│   ├── REPRODUCIBILITY_REPORT.md               # Bitwise hash reproducibility report
│   ├── SOURCE_MANIFEST.md                      # Complete codebase layout
│   └── VALIDATION_REPORT.md                    # Data quality scan audit findings
│
├── .env.example                                # Environment variables template
├── .env                                        # Local runtime environment file
├── Dockerfile                                  # Multi-stage container build
├── docker-compose.yml                          # Container orchestration configuration
├── pytest.ini                                  # Pytest configuration
└── README.md                                   # Master project guide
```

