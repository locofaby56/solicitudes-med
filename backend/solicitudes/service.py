from sqlalchemy import func, select
from sqlalchemy.orm import Session

from solicitudes.models import Medicamento, Solicitud


def listar_medicamentos(sesion: Session) -> list[Medicamento]:
    consulta = select(Medicamento).order_by(Medicamento.nombre, Medicamento.id)
    return list(sesion.scalars(consulta))


def _texto(valor: str | None) -> str | None:
    if valor is None:
        return None
    limpio = valor.strip()
    return limpio or None


def crear_solicitud(
    sesion: Session,
    usuario_id: int,
    medicamento_id: int,
    numero_orden: str | None,
    direccion: str | None,
    telefono: str | None,
    correo: str | None,
) -> Solicitud:
    medicamento = sesion.get(Medicamento, medicamento_id)
    if medicamento is None:
        raise LookupError("No encontramos ese medicamento")

    numero_orden = _texto(numero_orden)
    direccion = _texto(direccion)
    telefono = _texto(telefono)
    correo = _texto(correo)
    if correo is not None:
        correo = correo.lower()

    if medicamento.es_no_pos:
        if not all((numero_orden, direccion, telefono, correo)):
            raise ValueError(
                "Un medicamento NO POS exige número de orden, dirección, teléfono y correo"
            )
    else:
        # En un POS los datos de entrega se quedan vacíos.
        numero_orden = direccion = telefono = correo = None

    solicitud = Solicitud(
        usuario_id=usuario_id,
        medicamento_id=medicamento_id,
        numero_orden=numero_orden,
        direccion=direccion,
        telefono=telefono,
        correo=correo,
    )
    sesion.add(solicitud)
    sesion.commit()
    sesion.refresh(solicitud)
    return solicitud


def listar_solicitudes(
    sesion: Session, usuario_id: int, pagina: int, por_pagina: int
) -> tuple[list[Solicitud], int]:
    filtro = Solicitud.usuario_id == usuario_id
    total = sesion.scalar(select(func.count(Solicitud.id)).where(filtro)) or 0
    consulta = (
        select(Solicitud)
        .where(filtro)
        .order_by(Solicitud.id)
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
    )
    return list(sesion.scalars(consulta)), total
