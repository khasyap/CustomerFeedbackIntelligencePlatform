import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.api import api_router
from backend.app.models.entities import Theme, SentimentLabel, Customer
from backend.app.services.data_generator import THEME_TAXONOMY, SENTIMENT_LABELS, SyntheticDataGenerator
from backend.app.services.trend_detector import TrendDetector
from backend.app.services.priority_engine import PriorityEngine

# Ensure tables are created immediately
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-seed baseline master and starter data if empty
    db = SessionLocal()
    try:
        if db.query(Customer).count() == 0:
            print("[INFO] Empty database detected. Seeding initial master and starter data...")
            # 1. Themes
            for t in THEME_TAXONOMY:
                if not db.query(Theme).filter(Theme.theme_id == t["id"]).first():
                    db.add(Theme(
                        theme_id=t["id"],
                        theme_name=t["name"],
                        parent_theme_id=t["parent"],
                        description=t["desc"],
                        keywords=t["keywords"],
                        default_severity=t["severity"],
                        is_active=True
                    ))
            # 2. Sentiment labels
            for s in SENTIMENT_LABELS:
                if not db.query(SentimentLabel).filter(SentimentLabel.label_code == s["code"]).first():
                    db.add(SentimentLabel(
                        label_code=s["code"],
                        description=s["desc"],
                        polarity_score=s["polarity"]
                    ))
            db.commit()

            # 3. Generate starter data
            gen = SyntheticDataGenerator(seed=settings.RANDOM_SEED, mode="starter")
            data = gen.generate_all()
            gen.export_ground_truth()

            for c in data["customers"]:
                db.add(Customer(**c))
            from backend.app.models.entities import Product, Channel, Survey, Ticket, Review, SurveyResponse, SupportMessage, DataQualityIssue
            for p in data["products"]:
                db.add(Product(**p))
            for ch in data["channels"]:
                db.add(Channel(**ch))
            for s in data["surveys"]:
                db.add(Survey(**s))
            db.commit()

            for tkt in data["tickets"]:
                db.add(Ticket(**tkt))
            for r in data["reviews"]:
                db.add(Review(**r))
            for resp in data["survey_responses"]:
                db.add(SurveyResponse(**resp))
            for msg in data["support_messages"]:
                db.add(SupportMessage(**msg))
            for anom in data["anomalies"]:
                db.add(DataQualityIssue(**anom))
            db.commit()

            # Provision initial sentiment alerts and priority action items
            TrendDetector.detect_sentiment_shifts(db)
            PriorityEngine.auto_create_action_items(db, top_n=5)
            print("[INFO] Initial seeding completed successfully!")
    finally:
        db.close()

    yield

app = FastAPI(
    title="Customer Feedback Intelligence & Sentiment Analytics API",
    description="Enterprise AI-powered Customer Feedback Intelligence and Sentiment Analytics Platform API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local pair programming dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Mount frontend static distribution if built
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/")
    def health_check():
        return {
            "status": "HEALTHY",
            "service": "Customer Feedback Intelligence API",
            "version": "2.0.0",
            "docs_url": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
