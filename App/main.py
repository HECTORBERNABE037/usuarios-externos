from fastapi import FastAPI, Request
import uvicorn
from models import *
from dao import *

app = FastAPI()

@app.get("/")
async def root():
    return "Bienvenido a la APIRest de usuarios externos"

@app.post("/usuarios",tags=["usuarios"],summary="Crear un usuario",response_model=Salida)
async def CrearUsuarios(request:Request,usuario:CrearUsuario)->Salida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.agregarUsuario(usuario)

@app.put("/usuarios/{idUsuario}",tags=["usuarios"],summary="Actualiza un usuario")
async def ActualizarUsuario(idUsuario):
    return f"Se actualizo el usuario {idUsuario}"

@app.on_event("startup")
def startup():
    conexion = Conexion()
    app.cn=conexion

@app.on_event("shutdown")
def shutdown():
    app.cn.cerrar()

if __name__ == "__main__":
    uvicorn.run("main:app",reload=True)