from fastapi import APIRouter

from .endpoints import proteins

api_router = APIRouter()
api_router.include_router(proteins.router, prefix="/proteins", tags=["proteins"])
