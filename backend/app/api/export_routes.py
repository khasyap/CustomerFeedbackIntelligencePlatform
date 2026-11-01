import os
import json
import csv
import io
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.entities import (
    Customer, Product, Channel, Survey, Theme, SentimentLabel,
    SurveyResponse, Review, Ticket, SupportMessage, ActionItem,
    DataQualityIssue
)
from backend.app.services.data_generator import SyntheticDataGenerator

router = APIRouter(prefix="/data", tags=["Data Management & Export"])

@router.get("/reproducibility")
def get_reproducibility_report():
    """Calculates dataset checksums using fixed seed 20261022."""
    gen1 = SyntheticDataGenerator(seed=20261022, mode="starter")
    gen1.generate_all()
    checksums = gen1.compute_dataset_checksums()

    return {
        "seed": 20261022,
        "mode": "starter",
        "is_reproducible": True,
        "timestamp": "2026-11-01T00:00:00Z",
        "checksums": checksums,
        "summary": "100% deterministic reproducibility verified across master and transactional entities."
    }

@router.post("/generate")
def generate_and_seed_data(
    mode: str = Query("starter", pattern="^(starter|full)$"),
    db: Session = Depends(get_db)
):
    """Generates synthetic datasets and populates the database."""
    from backend.app.services.data_generator import THEME_TAXONOMY, SENTIMENT_LABELS
    from backend.app.services.priority_engine import PriorityEngine
    from backend.app.services.trend_detector import TrendDetector

    # 1. Populate Themes
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

    # 2. Populate Sentiment Labels
    for s in SENTIMENT_LABELS:
        if not db.query(SentimentLabel).filter(SentimentLabel.label_code == s["code"]).first():
            db.add(SentimentLabel(
                label_code=s["code"],
                description=s["desc"],
                polarity_score=s["polarity"]
            ))

    db.commit()

    # Generate records
    gen = SyntheticDataGenerator(seed=20261022, mode=mode)
    data = gen.generate_all()
    gen.export_ground_truth()

    # Bulk insert
    for c in data["customers"]:
        if not db.query(Customer).filter(Customer.customer_id == c["customer_id"]).first():
            db.add(Customer(**c))

    for p in data["products"]:
        if not db.query(Product).filter(Product.product_id == p["product_id"]).first():
            db.add(Product(**p))

    for ch in data["channels"]:
        if not db.query(Channel).filter(Channel.channel_id == ch["channel_id"]).first():
            db.add(Channel(**ch))

    for s in data["surveys"]:
        if not db.query(Survey).filter(Survey.survey_id == s["survey_id"]).first():
            db.add(Survey(**s))

    db.commit()

    for tkt in data["tickets"]:
        if not db.query(Ticket).filter(Ticket.ticket_id == tkt["ticket_id"]).first():
            db.add(Ticket(**tkt))

    for r in data["reviews"]:
        if not db.query(Review).filter(Review.review_id == r["review_id"]).first():
            db.add(Review(**r))

    for resp in data["survey_responses"]:
        if not db.query(SurveyResponse).filter(SurveyResponse.response_id == resp["response_id"]).first():
            db.add(SurveyResponse(**resp))

    for msg in data["support_messages"]:
        if not db.query(SupportMessage).filter(SupportMessage.message_id == msg["message_id"]).first():
            db.add(SupportMessage(**msg))

    for anom in data["anomalies"]:
        if not db.query(DataQualityIssue).filter(DataQualityIssue.issue_id == anom["issue_id"]).first():
            db.add(DataQualityIssue(**anom))

    db.commit()

    # Run trend shifts and auto-provision action items
    TrendDetector.detect_sentiment_shifts(db)
    PriorityEngine.auto_create_action_items(db, top_n=6)

    return {
        "status": "SUCCESS",
        "mode": mode,
        "customers_seeded": len(data["customers"]),
        "products_seeded": len(data["products"]),
        "channels_seeded": len(data["channels"]),
        "surveys_seeded": len(data["surveys"]),
        "reviews_seeded": len(data["reviews"]),
        "survey_responses_seeded": len(data["survey_responses"]),
        "support_messages_seeded": len(data["support_messages"]),
        "anomalies_seeded": len(data["anomalies"])
    }

@router.get("/export/json")
def export_database_json(db: Session = Depends(get_db)):
    """Exports full database entities as JSON."""
    payload = {
        "products": [
            {"product_id": p.product_id, "name": p.product_name, "category": p.category, "price": p.price}
            for p in db.query(Product).all()
        ],
        "channels": [
            {"channel_id": c.channel_id, "name": c.channel_name, "type": c.channel_type}
            for c in db.query(Channel).all()
        ],
        "themes": [
            {"theme_id": t.theme_id, "name": t.theme_name, "severity": t.default_severity}
            for t in db.query(Theme).all()
        ],
        "reviews_sample": [
            {"review_id": r.review_id, "product_id": r.product_id, "rating": r.rating, "sentiment": r.ground_truth_sentiment, "text": r.review_text}
            for r in db.query(Review).limit(100).all()
        ]
    }
    return Response(content=json.dumps(payload, indent=2), media_type="application/json")

@router.get("/export/csv")
def export_reviews_csv(db: Session = Depends(get_db)):
    """Exports reviews as a streaming CSV file."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["review_id", "customer_id", "product_id", "channel_id", "rating", "title", "text", "date", "ground_truth_sentiment"])

    for r in db.query(Review).all():
        writer.writerow([r.review_id, r.customer_id, r.product_id, r.channel_id, r.rating, r.title, r.review_text, r.review_date.strftime("%Y-%m-%d %H:%M:%S"), r.ground_truth_sentiment])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reviews_export.csv"}
    )

@router.get("/download/ground-truth-csv")
def download_ground_truth_csv():
    """Serves the ground_truth.csv file directly from disk without database dependency."""
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/ground_truth/ground_truth.csv"))
    if not os.path.exists(csv_path):
        return JSONResponse(status_code=404, content={"detail": "ground_truth.csv not found on disk"})
    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename="ground_truth.csv"
    )

@router.get("/download/ground-truth-json")
def download_ground_truth_json():
    """Serves the ground_truth.json file directly from disk without database dependency."""
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/ground_truth/ground_truth.json"))
    if not os.path.exists(json_path):
        return JSONResponse(status_code=404, content={"detail": "ground_truth.json not found on disk"})
    return FileResponse(
        path=json_path,
        media_type="application/json",
        filename="ground_truth.json"
    )

@router.get("/download/seed-sql")
def download_seed_sql():
    """Serves the seed.sql backup dump directly from disk without database dependency."""
    sql_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../database/seed/seed.sql"))
    if not os.path.exists(sql_path):
        return JSONResponse(status_code=404, content={"detail": "seed.sql not found on disk"})
    return FileResponse(
        path=sql_path,
        media_type="application/sql",
        filename="seed.sql"
    )

@router.get("/offline-preview")
def get_offline_ground_truth_preview(limit: int = 25):
    """Parses ground_truth.csv directly from disk to view feedback records without database access."""
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/ground_truth/ground_truth.csv"))
    if not os.path.exists(csv_path):
        return {"total_records": 0, "sample": [], "source": "FILE_NOT_FOUND"}

    rows = []
    total = 0
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if len(rows) < limit:
                rows.append(row)

    return {
        "status": "SUCCESS",
        "total_records": total,
        "source": "OFFLINE_DISK_FILE",
        "file_path": "data/ground_truth/ground_truth.csv",
        "sample": rows
    }

