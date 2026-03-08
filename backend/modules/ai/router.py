from fastapi import APIRouter, Depends

from core.auth import get_current_user
from models import User
from modules.ai import service
from modules.ai.schemas import AIChatRequest, AIChatResponse

router = APIRouter()


@router.post("/chat", response_model=AIChatResponse, operation_id="aiChat")
async def chat(
    body: AIChatRequest,
    current_user: User = Depends(get_current_user),
):
    return await service.chat(body)
