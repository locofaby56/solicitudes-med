import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.routes import router as router_auth
from db.connection import cargar_entorno
from solicitudes.routes import router as router_solicitudes

cargar_entorno()

ORIGENES_FRONTEND = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
origenes_extra = [
    origen.strip()
    for origen in os.environ.get("CORS_ORIGINS", "").split(",")
    if origen.strip()
]

aplicacion = FastAPI()
aplicacion.add_middleware(
    CORSMiddleware,
    allow_origins=[*ORIGENES_FRONTEND, *origenes_extra],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
aplicacion.include_router(router_auth)
aplicacion.include_router(router_solicitudes)
app = aplicacion
