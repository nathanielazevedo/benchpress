import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from core.logging import setup_logging, get_logger
from core.database import AsyncSessionLocal, settings
from core.auth import hash_password
from models import User, UserRole
from modules.auth.router import router as auth_router
from modules.companies.router import router as companies_router
from modules.labs.router import router as labs_router
from modules.users.router import router as users_router
from modules.designs.router import router as designs_router
from modules.ai.router import router as ai_router
from modules.instruments.router import router as instruments_router
from modules.companies.schemas import CompanyWithLabsOut
from modules.labs.schemas import LabOut

# Resolve forward ref: CompanyWithLabsOut.labs -> LabOut (must run after both modules load)
CompanyWithLabsOut.model_rebuild(_types_namespace={"LabOut": LabOut})

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.role == UserRole.super_admin))
        if not result.scalar_one_or_none():
            admin = User(
                username=settings.super_admin_username,
                password_hash=hash_password(settings.super_admin_password),
                role=UserRole.super_admin,
                lab_id=None,
            )
            db.add(admin)
            await db.commit()
            logger.info("Super admin '%s' created", settings.super_admin_username)
    yield


app = FastAPI(title="Benchpress API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s %s %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(companies_router, prefix="/api/companies", tags=["companies"])
app.include_router(labs_router, prefix="/api/labs", tags=["labs"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(designs_router, prefix="/api/designs", tags=["designs"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
app.include_router(instruments_router, prefix="/api/instruments", tags=["instruments"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
