# ## File: main.py

# import logging
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.config import settings
# from app.database import init_db
# from app.routes.devices import router as devices_router
# from app.routes.locations import router as locations_router
# from app.routes.dashboard import router as dashboard_router
# from app.routes.alerts import router as alerts_router
# from app.routes.assets import router as assets_router
# from app.routes.auth import router as auth_router# from app.routes import auth_router, devices_router, locations_router, alerts_router, dashboard_router
# from app.utils import setup_logging
# from app.services import email_service
# from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError
# from starlette.exceptions import HTTPException as StarletteHTTPException
# from Mqtt_client import start_mqtt
# from device_status_checker import device_offline_checker
# import asyncio


# setup_logging()
# logger = logging.getLogger(__name__)



# app = FastAPI(title="GPS Asset Tracking API",  swagger_ui_init_oauth=None)
# app.add_middleware(
# CORSMiddleware,
# allow_origins=["*"],
# allow_credentials=True,
# allow_methods=["*"],
# allow_headers=["*"],
# )


# # include routers
# app.include_router(auth_router, prefix="/auth", tags=["auth"])
# app.include_router(devices_router, prefix="/devices", tags=["devices"])
# app.include_router(assets_router, prefix="/assets", tags=["assets"])
# app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
# app.include_router(locations_router, prefix="/locations", tags=["locations"])
# app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])


# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(request, exc):
#     logger.warning("HTTP exception: %s %s", exc.status_code, exc.detail)
#     return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     logger.warning("Validation error: %s", exc.errors())
#     return JSONResponse({"error": "Validation error", "details": exc.errors()}, status_code=422)


# @app.exception_handler(Exception)
# async def unhandled_exception_handler(request, exc):
#     logger.exception("Unhandled exception: %s", exc)
#     return JSONResponse({"error": "Internal server error"}, status_code=500)


# @app.on_event("startup")
# async def startup_event():
#     logger.info("Starting app, initializing DB...")
#     await init_db()

#     # ✅ Correct way
#     asyncio.create_task(start_mqtt())

# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(device_offline_checker())


# File: main.py

import logging
import asyncio
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.database import init_db
from app.utils import setup_logging

from app.routes.auth import router as auth_router
from app.routes.devices import router as devices_router
from app.routes.assets import router as assets_router
from app.routes.asset_status import router as asset_status_router  # ✅ NEW
from app.routes.alerts import router as alerts_router
from app.routes.locations import router as locations_router
from app.routes.dashboard import router as dashboard_router

from Mqtt_client import start_mqtt
from device_status_checker import device_offline_checker

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
setup_logging()
logger = logging.getLogger(__name__)

# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------
app = FastAPI(
    title="GPS Asset Tracking API",
    swagger_ui_init_oauth=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ROUTERS
# --------------------------------------------------
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(devices_router, prefix="/devices", tags=["devices"])
app.include_router(assets_router, prefix="/assets", tags=["assets"])
app.include_router(asset_status_router, prefix="/assets", tags=["asset-status"])  # ✅
app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
app.include_router(locations_router, prefix="/locations", tags=["locations"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

# --------------------------------------------------
# EXCEPTION HANDLERS
# --------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.warning("HTTP exception: %s %s", exc.status_code, exc.detail)
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.warning("Validation error: %s", exc.errors())
    return JSONResponse(
        {"error": "Validation error", "details": exc.errors()},
        status_code=422
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        {"error": "Internal server error"},
        status_code=500
    )

# --------------------------------------------------
# STARTUP EVENT (SINGLE & CLEAN)
# --------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("Starting app, initializing DB...")
    await init_db()

    # 🔌 MQTT Listener
    asyncio.create_task(start_mqtt())

    # ⏱ Device offline checker
    asyncio.create_task(device_offline_checker())



