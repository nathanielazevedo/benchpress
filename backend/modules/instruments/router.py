import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.minio import list_instrument_files, get_object_stream
from core.permissions import require_lab_admin
from core.pagination import PageParams, Page
from models import User
from modules.instruments import service
from modules.instruments.schemas import HeartbeatIn, InstrumentOut, InstrumentCommand, InstrumentFileOut

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


@router.get("/{instrument_id}/files", response_model=list[InstrumentFileOut], operation_id="listInstrumentFiles")
async def list_files(
    instrument_id: str,
    current_user: User = Depends(require_lab_admin),
):
    """List files uploaded by a specific instrument from object storage."""
    return await list_instrument_files(instrument_id)


@router.get("/{instrument_id}/files/download", operation_id="downloadInstrumentFile")
async def download_file(
    instrument_id: str,
    key: str = Query(...),
    current_user: User = Depends(require_lab_admin),
):
    """Stream a single instrument file from object storage."""
    # Prevent path traversal — key must belong to this instrument
    if not key.startswith(f"{instrument_id}/"):
        raise HTTPException(status_code=403, detail="Access denied")

    response, content_type = get_object_stream(key)
    filename = key.split("/")[-1]
    encoded = urllib.parse.quote(filename)

    return StreamingResponse(
        response,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
    )


@router.get("", response_model=Page[InstrumentOut], operation_id="listInstruments")
async def list_instruments(
    page: PageParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_lab_admin),
):
    """List all instruments. Requires lab_admin or above."""
    items, total = await service.list_instruments(db, page.skip, page.limit)
    return Page(items=items, total=total, skip=page.skip, limit=page.limit)
