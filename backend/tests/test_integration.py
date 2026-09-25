import sys
import uuid
from pathlib import Path

RAIZ_BACKEND = Path(__file__).resolve().parents[1]
if str(RAIZ_BACKEND) not in sys.path:
    sys.path.insert(0, str(RAIZ_BACKEND))

from fastapi.testclient import TestClient
from sqlalchemy import delete

from auth.models import Usuario
from db.connection import SesionLocal
from main import aplicacion
from solicitudes.models import Medicamento, Solicitud

CONTRASENA = "clave-segura"


def _limpiar(usuario_id, medicamento_id):
    with SesionLocal() as sesion:
        if usuario_id is not None:
            sesion.execute(delete(Solicitud).where(Solicitud.usuario_id == usuario_id))
        if medicamento_id is not None:
            sesion.execute(delete(Medicamento).where(Medicamento.id == medicamento_id))
        if usuario_id is not None:
            sesion.execute(delete(Usuario).where(Usuario.id == usuario_id))
        sesion.commit()


def test_registro_login_crear_solicitud_y_listar():
    correo = f"flujo-{uuid.uuid4().hex}@ejemplo.com"
    cliente = TestClient(aplicacion)
    usuario_id = None
    medicamento_id = None
    try:
        alta = cliente.post("/registro", json={"correo": correo, "contrasena": CONTRASENA})
        assert alta.status_code == 201
        usuario_id = alta.json()["id"]
        assert alta.json()["correo"] == correo

        entrada = cliente.post(
            "/iniciar-sesion",
            json={"correo": correo, "contrasena": CONTRASENA},
        )
        assert entrada.status_code == 200
        token = entrada.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        with SesionLocal() as sesion:
            medicamento = Medicamento(nombre=f"flujo-{uuid.uuid4().hex}", es_no_pos=False)
            sesion.add(medicamento)
            sesion.commit()
            sesion.refresh(medicamento)
            medicamento_id = medicamento.id

        primera = cliente.post(
            "/solicitudes",
            json={"medicamento_id": medicamento_id},
            headers=headers,
        )
        segunda = cliente.post(
            "/solicitudes",
            json={"medicamento_id": medicamento_id},
            headers=headers,
        )
        assert primera.status_code == 201
        assert segunda.status_code == 201

        pagina_1 = cliente.get(
            "/solicitudes",
            params={"pagina": 1, "por_pagina": 1},
            headers=headers,
        )
        assert pagina_1.status_code == 200
        cuerpo_1 = pagina_1.json()
        assert cuerpo_1["pagina"] == 1
        assert cuerpo_1["por_pagina"] == 1
        assert cuerpo_1["total"] == 2
        assert len(cuerpo_1["solicitudes"]) == 1
        assert cuerpo_1["solicitudes"][0]["id"] == primera.json()["id"]
        assert cuerpo_1["solicitudes"][0]["medicamento_id"] == medicamento_id

        pagina_2 = cliente.get(
            "/solicitudes",
            params={"pagina": 2, "por_pagina": 1},
            headers=headers,
        )
        assert pagina_2.status_code == 200
        cuerpo_2 = pagina_2.json()
        assert cuerpo_2["total"] == 2
        assert len(cuerpo_2["solicitudes"]) == 1
        assert cuerpo_2["solicitudes"][0]["id"] == segunda.json()["id"]
    finally:
        _limpiar(usuario_id, medicamento_id)
