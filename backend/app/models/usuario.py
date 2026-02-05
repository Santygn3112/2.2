from pydantic import BaseModel, EmailStr
from typing import Optional


# Lo que recibimos al registrarse
class UsuarioRegistro(BaseModel):
    nombre: str
    email: EmailStr
    password: str


# Lo que recibimos al hacer login
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


# Lo que guardamos en la BD
class UsuarioDB(BaseModel):
    id: Optional[str] = None
    nombre: str
    email: str
    hashed_password: str
