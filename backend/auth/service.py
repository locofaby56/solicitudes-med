import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.models import Usuario

ALGORITMO_TOKEN = "HS256"
HORAS_TOKEN = 8


def encriptar_contrasena(contrasena: str) -> str:
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()


def verificar_contrasena(contrasena: str, contrasena_guardada: str) -> bool:
    return bcrypt.checkpw(contrasena.encode(), contrasena_guardada.encode())


def _correo_limpio(correo: str) -> str:
    return correo.strip().lower()


def registrar_usuario(sesion: Session, correo: str, contrasena: str) -> Usuario:
    correo = _correo_limpio(correo)
    ya_existe = sesion.scalars(select(Usuario).where(Usuario.correo == correo)).first()
    if ya_existe is not None:
        raise ValueError("Ese correo ya está registrado")

    usuario = Usuario(correo=correo, contrasena=encriptar_contrasena(contrasena))
    sesion.add(usuario)
    try:
        sesion.commit()
    except IntegrityError:
        sesion.rollback()
        raise ValueError("Ese correo ya está registrado")
    sesion.refresh(usuario)
    return usuario


def crear_token(usuario: Usuario) -> str:
    secreto = os.environ.get("JWT_SECRET", "").strip()
    if not secreto:
        raise RuntimeError("Falta la variable de entorno JWT_SECRET")
    ahora = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(usuario.id),
            "correo": usuario.correo,
            "iat": ahora,
            "exp": ahora + timedelta(hours=HORAS_TOKEN),
        },
        secreto,
        algorithm=ALGORITMO_TOKEN,
    )


def iniciar_sesion(sesion: Session, correo: str, contrasena: str) -> str:
    correo = _correo_limpio(correo)
    usuario = sesion.scalars(select(Usuario).where(Usuario.correo == correo)).first()
    if usuario is None or not verificar_contrasena(contrasena, usuario.contrasena):
        raise PermissionError("Correo o contraseña incorrectos")
    return crear_token(usuario)
