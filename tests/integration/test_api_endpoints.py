import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    res_root = client.get("/")
    assert res_root.status_code == 200

def test_api_master_data():
    res_cust = client.get("/api/customers?limit=10")
    assert res_cust.status_code == 200
    assert len(res_cust.json()) > 0

    res_prod = client.get("/api/products")
    assert res_prod.status_code == 200
    assert len(res_prod.json()) >= 10

    res_themes = client.get("/api/themes")
    assert res_themes.status_code == 200
    assert len(res_themes.json()) == 18

def test_api_analytics_overview():
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_feedback"] > 0
    assert "sentiment_distribution" in data
    assert "sentiment_percentages" in data
    assert data["total_themes_identified"] == 18

def test_api_sentiment_breakdown():
    res_prod = client.get("/api/analytics/sentiment?group_by=product")
    assert res_prod.status_code == 200
    assert len(res_prod.json()["items"]) > 0

    res_chan = client.get("/api/analytics/sentiment?group_by=channel")
    assert res_chan.status_code == 200
    assert len(res_chan.json()["items"]) > 0

def test_api_service_priorities():
    res = client.get("/api/analytics/priorities?limit=5")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    assert items[0]["priority_score"] >= items[-1]["priority_score"]
    assert "suggested_action" in items[0]

def test_api_feedback_explorer():
    res = client.get("/api/feedback?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) == 10
    assert data["total"] > 0

    # Test single item detail
    fb_id = data["items"][0]["feedback_id"]
    res_detail = client.get(f"/api/feedback/{fb_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["feedback_id"] == fb_id

def test_api_data_quality():
    res_val = client.post("/api/data-quality/validate")
    assert res_val.status_code == 200
    assert res_val.json()["pass_rate"] > 95.0

    res_issues = client.get("/api/data-quality/issues")
    assert res_issues.status_code == 200
    assert len(res_issues.json()) > 0
