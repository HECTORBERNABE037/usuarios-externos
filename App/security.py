from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
from dao import Conexion, UsuarioDAO
from models import UsuarioConsulta


security = HTTPBasic()


def getUser(credenciales: HTTPBasicCredentials = Depends(security)):
    correo = credenciales.username
    password = credenciales.password

    cn = Conexion(correo, password)

    if cn.db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de base de datos incorrectas o usuario no existe en Mongo",
            headers={"WWW-Authenticate": "Basic"},
        )

    usuarioDAO = UsuarioDAO(cn.db)

    # Validamos que el usuario exista
    usuario = usuarioDAO.autenticar(correo, password)
    cn.cerrar()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos, o usuario bloqueado/eliminado",
            headers={"WWW-Authenticate": "Basic"},
        )
    return usuario


class RoleChecker:
    def __init__(self, roles: list):
        self.roles_permitidos = roles

    def __call__(self, user: UsuarioConsulta = Depends(getUser)):
        if user is None or user.rol not in self.roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sin autorizacion. Tu rol '{user.rol if user else 'Ninguno'}' no tiene los permisos necesarios."
            )
        return user