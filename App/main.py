from fastapi import FastAPI, Request, Header, Depends
import uvicorn
from models import *
from dao import *
from security import RoleChecker

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# def obtener_rol_simulado(
#     rol_simulado: str = Header(default="Usuario", description="Simula el rol del usuario que hace la peticion")):
#     return rol_simulado

acceso_admin = RoleChecker(["Supervisor","Organizador"])
acceso_total = RoleChecker(["Supervisor","Organizador","Usuario"])
acceso_supervisor = RoleChecker(["Supervisor"])

@app.get("/")
async def root():
    return "Bienvenido a la APIRest de usuarios externos"

# ── HECTOR BERNABE - USUARIOS ───────────────────────────────────────────────

@app.post("/usuarios",tags=["usuarios"],summary="Crear un usuario",response_model=Salida)
@limiter.limit("5/minute")
async def CrearUsuarios(request:Request,usuario:CrearUsuario, user:UsuarioConsulta=Depends(acceso_total))->Salida:
    cn=Conexion(user.correo, user.password)
    usuarioDAO=UsuarioDAO(cn.db)
    salida = usuarioDAO.agregarUsuario((usuario))
    cn.cerrar()
    return salida
@app.get("/usuarios/{idUsuario}",tags=["usuarios"],summary="Consulta un usuario por su ID",response_model=ConsultaSalida)
@limiter.limit("5/minute")
async def ConsultaUsuarioPorId(request:Request,idUsuario,user:UsuarioConsulta=Depends(acceso_total))->ConsultaSalida:
    cn=Conexion(user.correo, user.password)
    usuarioDAO=UsuarioDAO(cn.db)
    salida = usuarioDAO.consultarPorId(idUsuario)
    cn.cerrar()
    return salida

@app.patch("/usuarios/{idUsuario}",tags=["usuarios"],summary="Actualiza un usuario", response_model=Salida)
@limiter.limit("5/minute")
async def ActualizarUsuario(request:Request,idUsuario,usuario:ModificarUsuario,user:UsuarioConsulta=Depends(acceso_total))->Salida:
    cn=Conexion(user.correo, user.password)
    usuarioDAO=UsuarioDAO(cn.db)
    salida = usuarioDAO.modificarUsuario(usuario,idUsuario,user.rol)
    cn.cerrar()
    return salida

@app.patch("/admin/usuarios/{idUsuario}",tags=["usuarios"],summary="Actualiza un usuario siendo admin", response_model=Salida)
@limiter.limit("5/minute")
async def AdminActualizarUsuario(request:Request,idUsuario,usuario:AdminModificarUsuario,user:UsuarioConsulta=Depends(acceso_admin))->Salida:
    cn=Conexion(user.correo,user.password)
    usuarioDAO=UsuarioDAO(cn.db)
    salida = usuarioDAO.AdminModificarUsuario(usuario,idUsuario,user.rol)
    cn.cerrar()
    return salida

@app.patch("/usuarios/{idUsuario}/perfil",tags=['usuarios'],summary="Modificar perfil del usuario", response_model=Salida)
@limiter.limit("5/minute")
async def ActualizarPerfilUsuario(request:Request,idUsuario,perfil_usuario:PerfilUsuario,user:UsuarioConsulta=Depends(acceso_total))->Salida:
    cn=Conexion(user.correo,user.password)
    usuarioDAO=UsuarioDAO(cn.db)
    salida = usuarioDAO.ModificarPerfilUsuario(idUsuario,perfil_usuario)
    cn.cerrar()
    return salida

@app.patch("/usuarios/eliminar/{idUsuario}",tags=['usuarios'],summary="Borrar un usuario", response_model=Salida)
@limiter.limit("5/minute")
async def BorrarUsuario(request:Request,idUsuario,user:UsuarioConsulta=Depends(acceso_admin))->Salida:
    cn=Conexion(user.correo,user.password)
    usuarioDAO=UsuarioDAO(cn.db)
    salida = usuarioDAO.BorrarUsuario(idUsuario)
    cn.cerrar()
    return salida

@app.get("/usuarios",tags=["usuarios"],summary="Listar usuarios",response_model=ConsultaGeneralSalida)
@limiter.limit("5/minute")
async def ConsultaGeneralUsuarios(request:Request, user:UsuarioConsulta=Depends(acceso_admin))->ConsultaGeneralSalida:
    cn=Conexion(user.correo,user.password)
    usuarioDAO=UsuarioDAO(cn.db)
    salida = usuarioDAO.consultaGeneral()
    cn.cerrar()
    return salida

@app.get("/usuarios/estatus/{estatus}",tags=['usuarios'],summary="Consulta por estatus", response_model=ConsultaGeneralSalida)
@limiter.limit("5/minute")
async def ConsultaPorEstatus(request:Request,estatus:str,user:UsuarioConsulta=Depends(acceso_admin))->ConsultaGeneralSalida:
    cn=Conexion(user.correo,user.password)
    usuarioDAO= UsuarioDAO(cn.db)
    salida = usuarioDAO.consultaPorEstatus(estatus)
    cn.cerrar()
    return salida

@app.patch("/usuarios/{idUsuario}/acreditacion",tags=["usuarios"],summary="Acreditar acceso al usuario", response_model=Salida)
@limiter.limit("5/minute")
async def AcreditacionUsuario(request:Request,idUsuario,user:UsuarioConsulta=Depends(acceso_admin))->Salida:
    cn=Conexion(user.correo,user.password)
    usuarioDAO=UsuarioDAO(cn.db)
    salida = usuarioDAO.acreditarAcceso(idUsuario)
    cn.cerrar()
    return salida


# ── JESUS ESTRADA ALEJANDRE - INSTITUCIONES ────────────────────────────────────────────────
 
@app.post("/instituciones",tags=["Instituciones"],summary="Crear institución de procedencia",response_model=Salida,status_code=201)
@limiter.limit("5/minute")
async def crearInstitucion(request: Request, institucion: InstitucionCreate, user: UsuarioConsulta = Depends(acceso_admin)) -> Salida:
    cn = Conexion(user.correo, user.password)
    dao = InstitucionDAO(cn.db)
    salida = dao.agregarInstitucion(institucion, user.rol)
    cn.cerrar()
    return salida
 
@app.get("/instituciones",tags=["Instituciones"],summary="Consultar todas las instituciones de procedencia",response_model=ConsultaGeneralSalidaInstitucion)
@limiter.limit("5/minute")
async def obtenerInstituciones(request: Request, user: UsuarioConsulta = Depends(acceso_total)) -> ConsultaGeneralSalidaInstitucion:
    cn = Conexion(user.correo, user.password)
    dao = InstitucionDAO(cn.db)
    salida = dao.consultaGeneral()
    cn.cerrar()
    return salida
 
@app.get("/instituciones/id/{id}",tags=["Instituciones"],summary="Consultar institución por ID",response_model=ConsultaSalidaInstitucion)
@limiter.limit("5/minute")
async def obtenerInstitucionPorId(request: Request, id: str, user: UsuarioConsulta = Depends(acceso_total)) -> ConsultaSalidaInstitucion:
    cn = Conexion(user.correo, user.password)
    dao = InstitucionDAO(cn.db)
    salida = dao.consultarPorId(id)
    cn.cerrar()
    return salida
 
@app.get("/instituciones/nombre/{nombre}",tags=["Instituciones"],summary="Consultar instituciones por nombre",response_model=ConsultaGeneralSalidaInstitucion)
@limiter.limit("5/minute")
async def obtenerInstitucionesPorNombre(request: Request, nombre: str, user: UsuarioConsulta = Depends(acceso_total)) -> ConsultaGeneralSalidaInstitucion:
    cn = Conexion(user.correo, user.password)
    dao = InstitucionDAO(cn.db)
    salida = dao.consultarPorNombre(nombre)
    cn.cerrar()
    return salida
 
@app.get("/instituciones/ciudad/{ciudad}",tags=["Instituciones"],summary="Consultar instituciones por ciudad",response_model=ConsultaGeneralSalidaInstitucion)
@limiter.limit("5/minute")
async def obtenerInstitucionesPorCiudad(request: Request, ciudad: str, user: UsuarioConsulta = Depends(acceso_total)) -> ConsultaGeneralSalidaInstitucion:
    cn = Conexion(user.correo, user.password)
    dao = InstitucionDAO(cn.db)
    salida = dao.consultarPorCiudad(ciudad)
    cn.cerrar()
    return salida
 
@app.put("/instituciones/{id}",tags=["Instituciones"],summary="Actualizar institución de procedencia",response_model=Salida)
@limiter.limit("5/minute")
async def actualizarInstitucion(request: Request, id: str, datos: InstitucionUpdate, user: UsuarioConsulta = Depends(acceso_admin)) -> Salida:
    cn = Conexion(user.correo, user.password)
    dao = InstitucionDAO(cn.db)
    salida = dao.modificarInstitucion(id, datos, user.rol)
    cn.cerrar()
    return salida
 
@app.delete("/instituciones/{id}",tags=["Instituciones"],summary="Eliminar institución de procedencia",response_model=Salida)
@limiter.limit("5/minute")
async def eliminarInstitucion(request: Request, id: str, user: UsuarioConsulta = Depends(acceso_supervisor)) -> Salida:
    cn = Conexion(user.correo, user.password)
    dao = InstitucionDAO(cn.db)
    salida = dao.eliminarInstitucion(id, user.rol)
    cn.cerrar()
    return salida
 


# ── JORGE ANDRES AVILA MEDINA - EVENTOS ────────────────────────────────────────────────────

@app.post("/eventos", tags=["Eventos"], summary="Crear un nuevo evento", response_model=Salida, status_code=201)
@limiter.limit("5/minute")
async def crearEvento(
    request: Request,
    evento: EventoCreate,
    user: UsuarioConsulta = Depends(acceso_admin)
) -> Salida:
    cn = Conexion(user.correo, user.password)
    dao = EventoDAO(cn.db)
    salida = dao.agregarEvento(evento, user.rol)
    cn.cerrar()
    return salida


@app.get("/eventos", tags=["Eventos"], summary="Consultar todos los eventos", response_model=ConsultaGeneralSalidaEvento)
@limiter.limit("5/minute")
async def obtenerEventos(
    request: Request,
    user: UsuarioConsulta = Depends(acceso_total)
) -> ConsultaGeneralSalidaEvento:
    cn = Conexion(user.correo, user.password)
    dao = EventoDAO(cn.db)
    salida = dao.consultaGeneral()
    cn.cerrar()
    return salida


@app.get("/eventos/{idEvento}", tags=["Eventos"], summary="Consultar un evento por ID", response_model=ConsultaSalidaEvento)
@limiter.limit("5/minute")
async def obtenerEventoPorId(
    request: Request,
    idEvento: str,
    user: UsuarioConsulta = Depends(acceso_total)
) -> ConsultaSalidaEvento:
    cn = Conexion(user.correo, user.password)
    dao = EventoDAO(cn.db)
    salida = dao.consultarPorId(idEvento)
    cn.cerrar()
    return salida


@app.put("/eventos/{idEvento}", tags=["Eventos"], summary="Modificar un evento", response_model=Salida)
@limiter.limit("5/minute")
async def modificarEvento(
    request: Request,
    idEvento: str,
    datos: EventoUpdate,
    user: UsuarioConsulta = Depends(acceso_total)
) -> Salida:
    cn = Conexion(user.correo, user.password)
    dao = EventoDAO(cn.db)
    salida = dao.modificarEvento(idEvento, datos, user.rol)
    cn.cerrar()
    return salida


@app.delete("/eventos/{idEvento}", tags=["Eventos"], summary="Eliminar un evento", response_model=Salida)
@limiter.limit("5/minute")
async def eliminarEvento(
    request: Request,
    idEvento: str,
    user: UsuarioConsulta = Depends(acceso_supervisor)
) -> Salida:
    cn = Conexion(user.correo, user.password)
    dao = EventoDAO(cn.db)
    salida = dao.eliminarEvento(idEvento, user.rol)
    cn.cerrar()
    return salida


# @app.on_event("startup")
# def startup():
#     conexion = Conexion()
#     app.cn=conexion
#
# @app.on_event("shutdown")
# def shutdown():
#     app.cn.cerrar()

if __name__ == "__main__":
    uvicorn.run("main:app",reload=True)