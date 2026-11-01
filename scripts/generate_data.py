import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.config import settings
from backend.app.database import SessionLocal, Base, engine
from backend.app.models.entities import (
    Customer, Product, Channel, Survey, Theme, SentimentLabel,
    Ticket, Review, SurveyResponse, SupportMessage, DataQualityIssue
)
from backend.app.services.data_generator import (
    SyntheticDataGenerator, THEME_TAXONOMY, SENTIMENT_LABELS
)
from backend.app.services.trend_detector import TrendDetector
from backend.app.services.priority_engine import PriorityEngine

def main():
    parser = argparse.ArgumentParser(description="Synthetic Data Generator for Customer Feedback Intelligence")
    parser.add_argument("--mode", choices=["starter", "full"], default="starter", help="Generation volume mode")
    parser.add_argument("--seed", type=int, default=settings.RANDOM_SEED, help="Deterministic random seed")
    parser.add_argument("--reset-db", action="store_true", help="Drops and recreates database tables before seeding")
    args = parser.parse_args()

    print(f"==================================================")
    print(f"Customer Feedback Intelligence Data Generator")
    print(f"Mode: {args.mode} | Seed: {args.seed}")
    print(f"==================================================")

    if args.reset_db:
        print("[INFO] Resetting database tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Master Themes
        print("[INFO] Seeding Master Theme Taxonomy...")
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

        # 2. Master Sentiment Labels
        print("[INFO] Seeding Master Sentiment Labels...")
        for s in SENTIMENT_LABELS:
            if not db.query(SentimentLabel).filter(SentimentLabel.label_code == s["code"]).first():
                db.add(SentimentLabel(
                    label_code=s["code"],
                    description=s["desc"],
                    polarity_score=s["polarity"]
                ))
        db.commit()

        # 3. Generate Datasets
        print(f"[INFO] Generating synthetic datasets in {args.mode} mode...")
        gen = SyntheticDataGenerator(seed=args.seed, mode=args.mode)
        data = gen.generate_all()

        csv_p, json_p = gen.export_ground_truth()
        print(f"[SUCCESS] Exported ground truth to:\n - {csv_p}\n - {json_p}")

        # Seeding
        print(f"[INFO] Inserting {len(data['customers'])} customers...")
        for c in data["customers"]:
            db.add(Customer(**c))
        db.commit()

        print(f"[INFO] Inserting {len(data['products'])} products...")
        for p in data["products"]:
            db.add(Product(**p))

        print(f"[INFO] Inserting {len(data['channels'])} channels...")
        for ch in data["channels"]:
            db.add(Channel(**ch))

        print(f"[INFO] Inserting {len(data['surveys'])} surveys...")
        for s in data["surveys"]:
            db.add(Survey(**s))
        db.commit()

        print(f"[INFO] Inserting {len(data['tickets'])} tickets...")
        for tkt in data["tickets"]:
            db.add(Ticket(**tkt))
        db.commit()

        print(f"[INFO] Inserting {len(data['reviews'])} reviews...")
        for r in data["reviews"]:
            db.add(Review(**r))
        db.commit()

        print(f"[INFO] Inserting {len(data['survey_responses'])} survey responses...")
        for resp in data["survey_responses"]:
            db.add(SurveyResponse(**resp))
        db.commit()

        print(f"[INFO] Inserting {len(data['support_messages'])} support messages...")
        for msg in data["support_messages"]:
            db.add(SupportMessage(**msg))
        db.commit()

        print(f"[INFO] Inserting {len(data['anomalies'])} data quality exceptions...")
        for anom in data["anomalies"]:
            db.add(DataQualityIssue(**anom))
        db.commit()

        print("[INFO] Running trend anomaly detection & provisioning priority actions...")
        TrendDetector.detect_sentiment_shifts(db)
        actions = PriorityEngine.auto_create_action_items(db, top_n=6)
        print(f"[SUCCESS] Provisioned {len(actions)} high-priority action items.")

        # Checksums
        checksums = gen.compute_dataset_checksums()
        print(f"\n[DETERMINISTIC CHECKSUMS (SHA-256)]")
        for entity, chk in checksums.items():
            print(f" - {entity:20s}: {chk[:16]}...")

        print(f"\n[DONE] Generation complete!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
