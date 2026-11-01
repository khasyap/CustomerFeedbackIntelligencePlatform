from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.entities import Customer, Product, Channel, Survey, Theme, SentimentLabel
from backend.app.schemas.feedback import CustomerBase, ProductBase, ChannelBase, SurveyBase, ThemeBase

router = APIRouter(tags=["Master Data"])

@router.get("/customers", response_model=List[CustomerBase])
def get_customers(
    segment: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(Customer)
    if segment:
        query = query.filter(Customer.segment == segment)
    return query.limit(limit).all()

@router.get("/products", response_model=List[ProductBase])
def get_products(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    return query.all()

@router.get("/channels", response_model=List[ChannelBase])
def get_channels(
    channel_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Channel)
    if channel_type:
        query = query.filter(Channel.channel_type == channel_type)
    return query.all()

@router.get("/surveys", response_model=List[SurveyBase])
def get_surveys(db: Session = Depends(get_db)):
    return db.query(Survey).all()

@router.get("/themes", response_model=List[ThemeBase])
def get_themes(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Theme)
    if is_active is not None:
        query = query.filter(Theme.is_active == is_active)
    return query.all()
