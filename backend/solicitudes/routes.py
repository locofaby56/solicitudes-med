import os

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from auth.models import Usuario
from auth.service import ALGORITMO_TOKEN
from db.connection import obtener_sesion
from solicitudes.models import Solicitud
from solicitudes.service import (
    crear_solicitud as guardar_solicitud,
    listar_medicamentos,
    listar_solicitudes,
)

router = APIRouter()
seguridad = HTTPBearer(auto_error=False)


class NuevaSolicitud(BaseModel):
    medicamento_id: int
    numero_orden: str | None = Field(default=None, max_length=100)
    direccion: str | None = Field(default=None, max_length=500)
    telefono: str | None = Field(default=None, max_length=30)
    correo: EmailStr | None = None


def _solicitud_json(solicitud: Solicitud) -> dict:
    return {
        "id": solicitud.id,
        "usuario_id": solicitud.usuario_id,
        "medicamento_id": solicitud.medicamento_id,
        "numero_orden": solicitud.numero_orden,
        "direccion": solicitud.direccion,
        "telefono": solicitud.telefono,
        "correo": solicitud.correo,
        "creado_en": solicitud.creado_en.isoformat(sep=" ") if solicitud.creado_en else None,
    }


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(seguridad),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario:
    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Falta el token")
    secreto = os.environ.get("JWT_SECRET", "").strip()
    if not secreto:
        raise HTTPException(status_code=500, detail="Falta la variable de entorno JWT_SECRET")
    try:
        datos = jwt.decode(credenciales.credentials, secreto, algorithms=[ALGORITMO_TOKEN])
        usuario_id = int(datos["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Token inválido") from error
    usuario = sesion.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return usuario


@router.get("/medicamentos")
def catalogo(
    sesion: Session = Depends(obtener_sesion),
    _usuario: Usuario = Depends(usuario_actual),
):
    return [
        {"id": medicamento.id, "nombre": medicamento.nombre, "es_no_pos": bool(medicamento.es_no_pos)}
        for medicamento in listar_medicamentos(sesion)
    ]


@router.post("/solicitudes", status_code=201)
def crear(
    datos: NuevaSolicitud,
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(usuario_actual),
):
    try:
        solicitud = guardar_solicitud(
            sesion,
            usuario.id,
            datos.medicamento_id,
            datos.numero_orden,
            datos.direccion,
            datos.telefono,
            datos.correo,
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _solicitud_json(solicitud)


@router.get("/solicitudes")
def listar(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(10, ge=1, le=50),
    sesion: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(usuario_actual),
):
    solicitudes, total = listar_solicitudes(sesion, usuario.id, pagina, por_pagina)
    return {
        "solicitudes": [_solicitud_json(solicitud) for solicitud in solicitudes],
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": total,
    }
