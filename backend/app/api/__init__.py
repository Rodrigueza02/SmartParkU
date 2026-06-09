
from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.parking import router as parking_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(parking_router)
