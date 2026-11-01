import os
import pytest
import pandas as pd
from backend.app.config import settings
from backend.app.database import SessionLocal
from backend.app.models.entities import Customer, Product, Channel, Survey, Review, SurveyResponse
from backend.app.services.data_generator import SyntheticDataGenerator

def test_primary_key_uniqueness():
    db = SessionLocal()
    try:
        cust_ids = [c.customer_id for c in db.query(Customer.customer_id).all()]
        assert len(cust_ids) == len(set(cust_ids)), "Duplicate Customer IDs found!"

        prod_ids = [p.product_id for p in db.query(Product.product_id).all()]
        assert len(prod_ids) == len(set(prod_ids)), "Duplicate Product IDs found!"

        surv_ids = [s.survey_id for s in db.query(Survey.survey_id).all()]
        assert len(surv_ids) == len(set(surv_ids)), "Duplicate Survey IDs found!"
    finally:
        db.close()

def test_ground_truth_isolation():
    csv_path = os.path.join(settings.DATA_DIR, "ground_truth", "ground_truth.csv")
    assert os.path.exists(csv_path), "ground_truth.csv file must exist separately"
    df = pd.read_csv(csv_path)
    # Ensure splits are present
    categories = set(df["evaluation_category"].unique())
    assert "TRAIN" in categories
    assert "TEST" in categories
    assert "VAL" in categories
    assert "ANOMALY" in categories

def test_generator_deterministic_reproducibility():
    gen1 = SyntheticDataGenerator(seed=20261022, mode="starter")
    gen1.generate_all()
    chk1 = gen1.compute_dataset_checksums()

    gen2 = SyntheticDataGenerator(seed=20261022, mode="starter")
    gen2.generate_all()
    chk2 = gen2.compute_dataset_checksums()

    for entity in chk1:
        assert chk1[entity] == chk2[entity], f"Checksum divergence in entity: {entity}"
