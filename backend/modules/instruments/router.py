from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.permissions import require_lab_admin
from core.pagination import PageParams, Page
from models import User
from modules.instruments import service
from modules.instruments.schemas import HeartbeatIn, InstrumentOut, InstrumentCommand

router = APIRouter()


@router.post("/heartbeat", response_model=InstrumentOut, operation_id="instrumentHeartbeat")
async def heartbeat(
    body: HeartbeatIn,
    db: AsyncSession = Depends(get_db),
):
    """Called by the instrument agent on each poll cycle. No user auth required."""
    return await service.upsert_heartbeat(db, body)


@router.get("/{instrument_id}/commands", response_model=list[InstrumentCommand], operation_id="getInstrumentCommands")
async def get_commands(instrument_id: str):
    """Polled by the instrument agent to receive pending commands."""
    return await service.get_pending_commands(instrument_id)


@router.get("", response_model=Page[InstrumentOut], operation_id="listInstruments")
async def list_instruments(
    page: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_lab_admin),
):
    """List all instruments. Requires lab_admin or above."""
    items, total = await service.list_instruments(db, page.skip, page.limit)
    return Page(items=items, total=total, skip=page.skip, limit=page.limit)
