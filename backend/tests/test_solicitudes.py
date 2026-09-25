import sys
import uuid
from pathlib import Path

RAIZ_BACKEND = Path(__file__).resolve().parents[1]
if str(RAIZ_BACKEND) not in sys.path:
    sys.path.insert(0, str(RAIZ_BACKEND))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from auth.models import Usuario
from db.connection import SesionLocal
from main import aplicacion
from solicitudes.models import Medicamento, Solicitud

CONTRASENA = "clave-segura"
ENTREGA = {
    "numero_orden": "ORD-99",
    "direccion": "Cra 10 # 20-30",
    "telefono": "3001234567",
    "correo": "entrega@ejemplo.com",
}


def _limpiar(usuario_id: int, medicamentos: list[int]) -> None:
    with SesionLocal() as sesion:
        sesion.execute(delete(Solicitud).where(Solicitud.usuario_id == usuario_id))
        if medicamentos:
            sesion.execute(delete(Medicamento).where(Medicamento.id.in_(medicamentos)))
        sesion.execute(delete(Usuario).where(Usuario.id == usuario_id))
        sesion.commit()


def _crear_medicamento(creados: dict, nombre: str, es_no_pos: bool) -> int:
    with SesionLocal() as sesion:
        medicamento = Medicamento(nombre=nombre, es_no_pos=es_no_pos)
        sesion.add(medicamento)
        sesion.commit()
        sesion.refresh(medicamento)
        creados["medicamentos"].append(medicamento.id)
        return medicamento.id


@pytest.fixture
def sesion_usuario():
    correo = f"sol-{uuid.uuid4().hex}@ejemplo.com"
    with TestClient(aplicacion) as cliente:
        alta = cliente.post("/registro", json={"correo": correo, "contrasena": CONTRASENA})
        assert alta.status_code == 201
        usuario_id = alta.json()["id"]
        entrada = cliente.post(
            "/iniciar-sesion",
            json={"correo": correo, "contrasena": CONTRASENA},
        )
        assert entrada.status_code == 200
        headers = {"Authorization": f"Bearer {entrada.json()['token']}"}
        creados = {"medicamentos": []}
        try:
            yield cliente, headers, creados
        finally:
            _limpiar(usuario_id, creados["medicamentos"])


def test_crea_solicitud_pos_simple(sesion_usuario):
    cliente, headers, creados = sesion_usuario
    medicamento_id = _crear_medicamento(creados, f"pos-{uuid.uuid4().hex}", False)

    catalogo = cliente.get("/medicamentos", headers=headers)
    assert catalogo.status_code == 200
    encontrado = next(item for item in catalogo.json() if item["id"] == medicamento_id)
    assert encontrado["es_no_pos"] is False

    respuesta = cliente.post(
        "/solicitudes",
        json={"medicamento_id": medicamento_id},
        headers=headers,
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["medicamento_id"] == medicamento_id
    assert cuerpo["numero_orden"] is None
    assert cuerpo["direccion"] is None
    assert cuerpo["telefono"] is None
    assert cuerpo["correo"] is None


def test_crea_solicitud_no_pos_con_campos_extra(sesion_usuario):
    cliente, headers, creados = sesion_usuario
    medicamento_id = _crear_medicamento(creados, f"no-pos-{uuid.uuid4().hex}", True)
    respuesta = cliente.post(
        "/solicitudes",
        json={"medicamento_id": medicamento_id, **ENTREGA},
        headers=headers,
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["medicamento_id"] == medicamento_id
    for campo, valor in ENTREGA.items():
        assert cuerpo[campo] == valor


def test_rechaza_no_pos_sin_campos(sesion_usuario):
    cliente, headers, creados = sesion_usuario
    medicamento_id = _crear_medicamento(creados, f"no-pos-{uuid.uuid4().hex}", True)

    sin_campos = cliente.post(
        "/solicitudes",
        json={"medicamento_id": medicamento_id},
        headers=headers,
    )
    assert sin_campos.status_code == 400
    assert sin_campos.json()["detail"]

    incompleta = cliente.post(
        "/solicitudes",
        json={
            "medicamento_id": medicamento_id,
            "numero_orden": ENTREGA["numero_orden"],
            "direccion": ENTREGA["direccion"],
            "correo": ENTREGA["correo"],
        },
        headers=headers,
    )
    assert incompleta.status_code == 400
    assert incompleta.json()["detail"]


def test_lista_solicitudes_con_paginacion(sesion_usuario):
    cliente, headers, creados = sesion_usuario
    medicamento_id = _crear_medicamento(creados, f"pos-{uuid.uuid4().hex}", False)
    for _ in range(3):
        creada = cliente.post(
            "/solicitudes",
            json={"medicamento_id": medicamento_id},
            headers=headers,
        )
        assert creada.status_code == 201

    sin_token = cliente.get("/solicitudes")
    assert sin_token.status_code == 401
    assert sin_token.json()["detail"]

    pagina_1 = cliente.get(
        "/solicitudes",
        params={"pagina": 1, "por_pagina": 2},
        headers=headers,
    )
    assert pagina_1.status_code == 200
    cuerpo_1 = pagina_1.json()
    assert cuerpo_1["pagina"] == 1
    assert cuerpo_1["por_pagina"] == 2
    assert cuerpo_1["total"] == 3
    assert len(cuerpo_1["solicitudes"]) == 2

    pagina_2 = cliente.get(
        "/solicitudes",
        params={"pagina": 2, "por_pagina": 2},
        headers=headers,
    )
    assert pagina_2.status_code == 200
    cuerpo_2 = pagina_2.json()
    assert cuerpo_2["total"] == 3
    assert len(cuerpo_2["solicitudes"]) == 1
