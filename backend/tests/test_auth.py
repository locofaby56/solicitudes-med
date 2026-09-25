import os
import sys
import uuid
from pathlib import Path

RAIZ_BACKEND = Path(__file__).resolve().parents[1]
if str(RAIZ_BACKEND) not in sys.path:
    sys.path.insert(0, str(RAIZ_BACKEND))

import bcrypt
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from auth.models import Usuario
from db.connection import SesionLocal
from main import aplicacion

CONTRASENA = "clave-segura"


def _borrar_usuario(correo: str) -> None:
    with SesionLocal() as sesion:
        usuario = sesion.scalars(select(Usuario).where(Usuario.correo == correo)).first()
        if usuario is not None:
            sesion.delete(usuario)
            sesion.commit()


@pytest.fixture
def correo():
    valor = f"usuario-{uuid.uuid4().hex}@ejemplo.com"
    yield valor
    _borrar_usuario(valor)


@pytest.fixture
def cliente():
    with TestClient(aplicacion) as cliente_http:
        yield cliente_http


def test_registro_crea_el_usuario(cliente, correo):
    respuesta = cliente.post(
        "/registro",
        json={"correo": correo, "contrasena": CONTRASENA},
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["correo"] == correo
    assert "contrasena" not in cuerpo

    with SesionLocal() as sesion:
        usuario = sesion.scalars(select(Usuario).where(Usuario.correo == correo)).one()
        assert usuario.id == cuerpo["id"]


def test_login_devuelve_un_token_valido(cliente, correo):
    cliente.post("/registro", json={"correo": correo, "contrasena": CONTRASENA})
    respuesta = cliente.post(
        "/iniciar-sesion",
        json={"correo": correo, "contrasena": CONTRASENA},
    )
    assert respuesta.status_code == 200
    token = respuesta.json()["token"]
    datos = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])

    with SesionLocal() as sesion:
        usuario = sesion.scalars(select(Usuario).where(Usuario.correo == correo)).one()
    assert datos["sub"] == str(usuario.id)
    assert datos["correo"] == correo


def test_la_contrasena_queda_hasheada(cliente, correo):
    cliente.post("/registro", json={"correo": correo, "contrasena": CONTRASENA})
    with SesionLocal() as sesion:
        usuario = sesion.scalars(select(Usuario).where(Usuario.correo == correo)).one()
        guardada = usuario.contrasena

    assert guardada != CONTRASENA
    assert bcrypt.checkpw(CONTRASENA.encode(), guardada.encode())


def test_rechaza_credenciales_invalidas(cliente, correo):
    desconocido = cliente.post(
        "/iniciar-sesion",
        json={"correo": correo, "contrasena": CONTRASENA},
    )
    assert desconocido.status_code == 401
    assert desconocido.json()["detail"]

    cliente.post("/registro", json={"correo": correo, "contrasena": CONTRASENA})
    incorrecta = cliente.post(
        "/iniciar-sesion",
        json={"correo": correo, "contrasena": "otra-clave-mal"},
    )
    assert incorrecta.status_code == 401
    assert incorrecta.json()["detail"]
