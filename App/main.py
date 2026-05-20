from urllib import request

from fastapi import FastAPI, Request, Header, Depends
import uvicorn
from models import *
from dao import *

app = FastAPI()

def obtener_rol_simulado(
    rol_simulado: str = Header(default="Usuario", description="Simula el rol del usuario que hace la peticion")):
    return rol_simulado

@app.get("/")
async def root():
    return "Bienvenido a la APIRest de usuarios externos"

# ── HECTOR BERNABE - USUARIOS ───────────────────────────────────────────────

@app.post("/usuarios",tags=["usuarios"],summary="Crear un usuario",response_model=Salida)
async def CrearUsuarios(request:Request,usuario:CrearUsuario)->Salida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.agregarUsuario(usuario)
@app.get("/usuarios/{idUsuario}",tags=["usuarios"],summary="Consulta un usuario por su ID",response_model=ConsultaSalida)
async def ConsultaUsuarioPorId(request:Request,idUsuario)->ConsultaSalida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.consultarPorId(idUsuario)

@app.patch("/usuarios/{idUsuario}",tags=["usuarios"],summary="Actualiza un usuario", response_model=Salida)
async def ActualizarUsuario(request:Request,idUsuario,usuario:ModificarUsuario,rol_actor:str=Depends(obtener_rol_simulado))->Salida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.modificarUsuario(usuario,idUsuario,rol_actor)

@app.patch("/admin/usuarios/{idUsuario}",tags=["usuarios"],summary="Actualiza un usuario siendo admin", response_model=Salida)
async def ActualizarUsuario(request:Request,idUsuario,usuario:AdminModificarUsuario,rol_actor:str=Depends(obtener_rol_simulado))->Salida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.AdminModificarUsuario(usuario,idUsuario,rol_actor)

@app.patch("/usuarios/{idUsuario}/perfil",tags=['usuarios'],summary="Modificar perfil del usuario", response_model=Salida)
async def ActualizarPerfilUsuario(request:Request,idUsuario,perfil_usuario:PerfilUsuario)->Salida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.ModificarPerfilUsuario(idUsuario,perfil_usuario)

@app.patch("/usuarios/eliminar/{idUsuario}",tags=['usuarios'],summary="Borrar un usuario", response_model=Salida)
async def BorrarUsuario(request:Request,idUsuario)->Salida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.BorrarUsuario(idUsuario)

@app.get("/usuarios",tags=["usuarios"],summary="Listar usuarios",response_model=ConsultaGeneralSalida)
async def ConsultaGeneralUsuarios(request:Request)->ConsultaGeneralSalida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.consultaGeneral()

@app.get("/usuarios/estatus/{estatus}",tags=['usuarios'],summary="Consulta por estatus", response_model=ConsultaGeneralSalida)
async def ConsultaPorEstatus(request:Request,estatus:str)->ConsultaGeneralSalida:
    usuarioDAO= UsuarioDAO(request.app.cn.db)
    return usuarioDAO.consultaPorEstatus(estatus)

@app.patch("/usuarios/{idUsuario}/acreditacion",tags=["usuarios"],summary="Acreditar acceso al usuario", response_model=Salida)
async def AcreditacionUsuario(request:Request,idUsuario)->Salida:
    usuarioDAO=UsuarioDAO(request.app.cn.db)
    return usuarioDAO.acreditarAcceso(idUsuario)


# ── JESUS ESTRADA ALEJANDRE - INSTITUCIONES ────────────────────────────────────────────────
 
@app.post("/instituciones",tags=["Instituciones"],summary="Crear institución de procedencia",response_model=Salida,status_code=201)
async def crearInstitucion(request: Request, institucion: InstitucionCreate) -> Salida:
    dao = InstitucionDAO(request.app.cn.db)
    return dao.agregarInstitucion(institucion)
 
@app.get("/instituciones",tags=["Instituciones"],summary="Consultar todas las instituciones de procedencia",response_model=ConsultaGeneralSalidaInstitucion)
async def obtenerInstituciones(request: Request) -> ConsultaGeneralSalidaInstitucion:
    dao = InstitucionDAO(request.app.cn.db)
    return dao.consultaGeneral()
 
@app.get("/instituciones/id/{id}",tags=["Instituciones"],summary="Consultar institución por ID",response_model=ConsultaSalidaInstitucion)
async def obtenerInstitucionPorId(request: Request, id: str) -> ConsultaSalidaInstitucion:
    dao = InstitucionDAO(request.app.cn.db) 
    return dao.consultarPorId(id)
 
@app.get("/instituciones/nombre/{nombre}",tags=["Instituciones"],summary="Consultar instituciones por nombre",response_model=ConsultaGeneralSalidaInstitucion)
async def obtenerInstitucionesPorNombre(request: Request, nombre: str) -> ConsultaGeneralSalidaInstitucion:
    dao = InstitucionDAO(request.app.cn.db)
    return dao.consultarPorNombre(nombre)
 
@app.get("/instituciones/ciudad/{ciudad}",tags=["Instituciones"],summary="Consultar instituciones por ciudad",response_model=ConsultaGeneralSalidaInstitucion)
async def obtenerInstitucionesPorCiudad(request: Request, ciudad: str) -> ConsultaGeneralSalidaInstitucion:
    dao = InstitucionDAO(request.app.cn.db)
    return dao.consultarPorCiudad(ciudad)
 
@app.put("/instituciones/{id}",tags=["Instituciones"],summary="Actualizar institución de procedencia",response_model=Salida)
async def actualizarInstitucion(request: Request, id: str, datos: InstitucionUpdate) -> Salida:
    dao = InstitucionDAO(request.app.cn.db)
    return dao.modificarInstitucion(id, datos)
 
@app.delete("/instituciones/{id}",tags=["Instituciones"],summary="Eliminar institución de procedencia",response_model=Salida)
async def eliminarInstitucion(request: Request, id: str) -> Salida:
    dao = InstitucionDAO(request.app.cn.db)
    return dao.eliminarInstitucion(id)
 


# ── JORGE ANDRES AVILA MEDINA - EVENTOS ────────────────────────────────────────────────────

@app.post("/eventos", tags=["Eventos"], summary="Crear un nuevo evento", response_model=Salida, status_code=201)
async def crearEvento(request: Request, evento: EventoCreate) -> Salida:
    dao = EventoDAO(request.app.cn.db)
    return dao.agregarEvento(evento)

@app.get("/eventos", tags=["Eventos"], summary="Consultar todos los eventos", response_model=ConsultaGeneralSalidaEvento)
async def obtenerEventos(request: Request) -> ConsultaGeneralSalidaEvento:
    dao = EventoDAO(request.app.cn.db)
    return dao.consultaGeneral()

@app.get("/eventos/{idEvento}", tags=["Eventos"], summary="Consultar un evento por ID", response_model=ConsultaSalidaEvento)
async def obtenerEventoPorId(request: Request, idEvento: str) -> ConsultaSalidaEvento:
    dao = EventoDAO(request.app.cn.db)
    return dao.consultarPorId(idEvento)

@app.put("/eventos/{idEvento}", tags=["Eventos"], summary="Modificar un evento", response_model=Salida)
async def modificarEvento(request: Request, idEvento: str, datos: EventoUpdate) -> Salida:
    dao = EventoDAO(request.app.cn.db)
    return dao.modificarEvento(idEvento, datos)

@app.delete("/eventos/{idEvento}", tags=["Eventos"], summary="Eliminar un evento", response_model=Salida)
async def eliminarEvento(request: Request, idEvento: str) -> Salida:
    dao = EventoDAO(request.app.cn.db)
    return dao.eliminarEvento(idEvento)


@app.on_event("startup")
def startup():
    conexion = Conexion()
    app.cn=conexion

@app.on_event("shutdown")
def shutdown():
    app.cn.cerrar()

if __name__ == "__main__":
    uvicorn.run("main:app",reload=True)