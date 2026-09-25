import os
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

RAIZ = Path(__file__).resolve().parents[2]


def cargar_entorno() -> None:
    ruta = RAIZ / ".env"
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        limpia = linea.strip()
        if not limpia or limpia.startswith("#") or "=" not in limpia:
            continue
        clave, valor = limpia.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def _variable(nombre: str) -> str:
    cargar_entorno()
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        raise RuntimeError(f"Falta la variable de entorno {nombre}")
    return valor


def _url_base() -> str:
    usuario = quote_plus(_variable("DB_USERNAME"))
    clave = quote_plus(os.environ.get("DB_PASSWORD", ""))
    host = _variable("DB_HOST")
    puerto = os.environ.get("DB_PORT", "3306").strip() or "3306"
    base = quote_plus(_variable("DB_DATABASE"))
    return f"mysql+pymysql://{usuario}:{clave}@{host}:{puerto}/{base}?charset=utf8mb4"


class Base(DeclarativeBase):
    pass


motor = create_engine(_url_base(), pool_pre_ping=True)
SesionLocal = sessionmaker(bind=motor, autoflush=False, autocommit=False)


def obtener_sesion():
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
