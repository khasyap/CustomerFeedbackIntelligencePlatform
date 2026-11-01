from fastapi import APIRouter
from backend.app.api.master_routes import router as master_router
from backend.app.api.feedback_routes import router as feedback_router
from backend.app.api.analytics_routes import router as analytics_router
from backend.app.api.ml_routes import router as ml_router
from backend.app.api.action_routes import router as action_router
from backend.app.api.quality_routes import router as quality_router
from backend.app.api.evaluation_routes import router as evaluation_router
from backend.app.api.export_routes import router as export_router

api_router = APIRouter(prefix="/api")

api_router.include_router(master_router)
api_router.include_router(feedback_router)
api_router.include_router(analytics_router)
api_router.include_router(ml_router)
api_router.include_router(action_router)
api_router.include_router(quality_router)
api_router.include_router(evaluation_router)
api_router.include_router(export_router)

@api_router.get("/health")
def health_status():
    return {
        "status": "HEALTHY",
        "service": "Customer Feedback Intelligence API",
        "version": "2.0.0",
        "docs_url": "/docs"
    }

__all__ = ["api_router"]
