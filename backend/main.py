from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.routes import router as router_auth
from solicitudes.routes import router as router_solicitudes

ORIGENES_FRONTEND = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

aplicacion = FastAPI()
aplicacion.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_FRONTEND,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
aplicacion.include_router(router_auth)
aplicacion.include_router(router_solicitudes)
app = aplicacion
