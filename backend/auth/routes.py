from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from auth.service import iniciar_sesion, registrar_usuario
from db.connection import obtener_sesion

router = APIRouter()


class Credenciales(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=8)


@router.post("/registro", status_code=201)
def registrar(datos: Credenciales, sesion: Session = Depends(obtener_sesion)):
    try:
        usuario = registrar_usuario(sesion, datos.correo, datos.contrasena)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"id": usuario.id, "correo": usuario.correo}


@router.post("/iniciar-sesion")
def entrar(datos: Credenciales, sesion: Session = Depends(obtener_sesion)):
    try:
        token = iniciar_sesion(sesion, datos.correo, datos.contrasena)
    except PermissionError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return {"token": token}
