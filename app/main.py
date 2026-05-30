import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine, Base, test_connection
from .config import settings
from .routes import auth, rooms, packages, bookings, messages, gallery, locations, admin, content, contact, testimonials

# Seed data
from . import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    _log = logging.getLogger("kinkyworld")
    ok = test_connection()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    # Mount uploads now that the directory is guaranteed to exist
    from fastapi.staticfiles import StaticFiles as _SF
    try:
        app.mount("/uploads", _SF(directory=settings.UPLOAD_DIR), name="uploads")
    except Exception:
        pass  # already mounted (e.g. hot-reload)
    if ok:
        # Create tables one-by-one so a pre-existing table (from Supabase schema.sql)
        # doesn't abort the whole create_all and skip the seed.
        for table in Base.metadata.sorted_tables:
            try:
                table.create(bind=engine, checkfirst=True)
            except Exception as e:
                _log.warning(f"Skipping table '{table.name}': {e}")
        try:
            seed.run()
        except Exception as e:
            _log.error(f"Seed failed: {e}", exc_info=True)
    else:
        _log.error("DB unreachable — seed skipped")
    yield


_is_dev = os.environ.get("RENDER") is None  # Render sets RENDER=true

app = FastAPI(
    title="Kinky World API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if _is_dev else None,
    redoc_url="/redoc" if _is_dev else None,
    openapi_url="/openapi.json" if _is_dev else None,
)

# Support comma-separated origins: FRONTEND_URL=https://a.com,https://b.com
_raw_origins = settings.FRONTEND_URL or ""
_origins = list(
    {o.strip() for o in _raw_origins.split(",") if o.strip()}
    | {"http://localhost:5173"}
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(packages.router)
app.include_router(bookings.router)
app.include_router(messages.router)
app.include_router(gallery.router)
app.include_router(locations.router)
app.include_router(admin.router)
app.include_router(content.router)
app.include_router(contact.router)
app.include_router(testimonials.router)



@app.get("/")
def root():
    return {"service": "Kinky World API", "status": "running", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "kinkyworld-api"}


