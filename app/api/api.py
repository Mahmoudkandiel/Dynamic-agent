from fastapi import APIRouter
from api.agent_api import router as agent_routes
from api.chat_api import router as chat_routes
from api.utils_api import router as utils_routes

api_router = APIRouter()


api_router.include_router(agent_routes)
api_router.include_router(chat_routes)
api_router.include_router(utils_routes)