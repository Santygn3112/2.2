from fastapi import APIRouter, HTTPException, status
from app.core.database import db
from app.models.usuario import UsuarioRegistro, UsuarioLogin, UsuarioDB
from passlib.context import CryptContext

router = APIRouter()

# Configuración de seguridad (Hashing)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/register", summary="Crear nuevo usuario")
def registrar_usuario(datos: UsuarioRegistro):
    coleccion_usuarios = db.get_db()["usuarios"]

    # 1. Comprobar si el email ya existe
    if coleccion_usuarios.find_one({"email": datos.email}):
        raise HTTPException(status_code=400, detail="Este email ya está registrado")

    # 2. Encriptar contraseña y guardar
    nuevo_usuario = UsuarioDB(
        nombre=datos.nombre,
        email=datos.email,
        hashed_password=get_password_hash(datos.password),
    )

    coleccion_usuarios.insert_one(nuevo_usuario.model_dump())

    return {"mensaje": "Usuario creado correctamente", "nombre": datos.nombre}


@router.post("/login", summary="Iniciar sesión")
def login(datos: UsuarioLogin):
    coleccion_usuarios = db.get_db()["usuarios"]

    # 1. Buscar usuario por email
    usuario_encontrado = coleccion_usuarios.find_one({"email": datos.email})

    if not usuario_encontrado:
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")

    # 2. Verificar contraseña
    if not verify_password(datos.password, usuario_encontrado["hashed_password"]):
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")

    # 3. Login exitoso -> Devolvemos el nombre para el frontend
    return {
        "mensaje": "Login exitoso",
        "usuario": usuario_encontrado["nombre"],
        "email": usuario_encontrado["email"],
    }
