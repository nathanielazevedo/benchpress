from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Instrument, InstrumentStatus
from modules.instruments.schemas import HeartbeatIn


async def upsert_heartbeat(db: AsyncSession, body: HeartbeatIn) -> Instrument:
    result = await db.execute(
        select(Instrument).where(Instrument.instrument_id == body.instrument_id)
    )
    instrument = result.scalar_one_or_none()

    now = datetime.utcnow()

    if instrument is None:
        instrument = Instrument(
            instrument_id=body.instrument_id,
            name=body.name,
            status=InstrumentStatus(body.status),
            last_seen_at=now,
            created_at=now,
        )
        db.add(instrument)
    else:
        instrument.name = body.name
        instrument.status = InstrumentStatus(body.status)
        instrument.last_seen_at = now

    await db.commit()
    await db.refresh(instrument)
    return instrument


async def list_instruments(db: AsyncSession, skip: int, limit: int) -> tuple[list[Instrument], int]:
    total_result = await db.execute(select(func.count()).select_from(Instrument))
    total = total_result.scalar_one()
    result = await db.execute(
        select(Instrument).order_by(Instrument.last_seen_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all(), total


async def get_pending_commands(instrument_id: str) -> list:
    # Command queue not yet implemented — always empty.
    return []
