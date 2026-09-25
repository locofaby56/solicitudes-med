import os
import re
from pathlib import Path

import pymysql
import pytest

RAIZ = Path(__file__).resolve().parents[2]
RUTA_ESQUEMA = RAIZ / "db" / "schema.sql"

COLUMNAS_ESPERADAS = {
    "usuarios": ["id", "correo", "contrasena", "creado_en"],
    "medicamentos": ["id", "nombre", "es_no_pos"],
    "solicitudes": [
        "id",
        "usuario_id",
        "medicamento_id",
        "numero_orden",
        "direccion",
        "telefono",
        "correo",
        "creado_en",
    ],
}


def _cargar_entorno() -> None:
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
    _cargar_entorno()
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        raise RuntimeError(f"Falta la variable de entorno {nombre}")
    return valor


def _sentencias_sql(script: str) -> list[str]:
    lineas = []
    for linea in script.splitlines():
        if linea.strip().startswith("--"):
            continue
        lineas.append(linea)
    return [parte.strip() for parte in "\n".join(lineas).split(";") if parte.strip()]


def _conectar(base: str | None = None) -> pymysql.Connection:
    parametros = {
        "host": _variable("DB_HOST"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": _variable("DB_USERNAME"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "charset": "utf8mb4",
        "autocommit": True,
    }
    if base:
        parametros["database"] = base
    return pymysql.connect(**parametros)


@pytest.fixture(scope="session")
def columnas_por_tabla() -> dict[str, list[str]]:
    nombre_base = _variable("DB_DATABASE")
    if not re.fullmatch(r"[A-Za-z0-9_]+", nombre_base):
        raise RuntimeError("DB_DATABASE contiene caracteres no permitidos")

    script = RUTA_ESQUEMA.read_text(encoding="utf-8")
    conexion = _conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{nombre_base}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(f"USE `{nombre_base}`")
            for sentencia in _sentencias_sql(script):
                cursor.execute(sentencia)
            cursor.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """,
                (nombre_base,),
            )
            encontradas: dict[str, list[str]] = {}
            for tabla, columna in cursor.fetchall():
                encontradas.setdefault(tabla, []).append(columna)
    finally:
        conexion.close()
    return encontradas


@pytest.mark.parametrize("tabla", list(COLUMNAS_ESPERADAS))
def test_la_tabla_existe_con_las_columnas_esperadas(tabla, columnas_por_tabla):
    assert tabla in columnas_por_tabla
    assert columnas_por_tabla[tabla] == COLUMNAS_ESPERADAS[tabla]
