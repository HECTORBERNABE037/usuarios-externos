from pydantic import BaseModel,Field, model_validator
from typing import Literal,List,Optional
from datetime import datetime

class Salida(BaseModel):
    codigo: int
    mensaje: str

class PerfilUsuario(BaseModel):
    nivelEstudios: Optional[str] = None
    carrera: Optional[str] = None
    requerimientosEspeciales: Optional[str] = None
    costo: Optional[float] = None
    cv: Optional[str] = None
    # estatus: str

class CrearUsuario(BaseModel):
    nombre: str
    apellido: str
    telefono: str = Field(...,pattern=r"^\d{10}$")
    correo: str
    #fechaRegistro: datetime
    #estatus: str
    tipo:Literal["Expositor","Estudiante","Invitado"]
    #rol: str
    idInstitucion:str
    idEvento:List[str] = []
    perfilUsuario: Optional[PerfilUsuario] = None

class UsuarioConsulta(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    correo: str
    fechaRegistro: datetime
    estatus: str
    tipo: str
    #rol: str
    idInstitucion: str
    nombreInstitucion: str
    nombresEventosInscritos: List[str]
    perfilUsuario: PerfilUsuario

class ConsultaSalida(Salida):
    usuario:Optional[UsuarioConsulta]=None

class ConsultaGeneralSalida(Salida):
    usuarios:Optional[List[UsuarioConsulta]]=None

class ModificarUsuario(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = Field(default=None,pattern=r"^\d{10}$")
    correo: Optional[str] = None
    idInstitucion: Optional[str] = None
    idEvento: Optional[List[str]] = None

class AdminModificarUsuario(ModificarUsuario):
    tipo: Optional[Literal["Expositor","Estudiante","Invitado"]] = None
    estatus: Optional[str] = None
    rol: Optional[Literal["Usuario","Organizador","Supervisor"]] = None

class ModificarPerfilUsuario(BaseModel):
    nivelEstudios: Optional[str] = None
    carrera: Optional[str] = None
    requerimientosEspeciales: Optional[str] = None
    costo: Optional[float] = None
    cv: Optional[str] = None

class InstitucionCreate(BaseModel):
    nombre: str
    tipo: str
    ciudad: str
    estado: str
 
 
class InstitucionUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
 
 
class InstitucionConsulta(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    fechaRegistro: Optional[datetime] = None
 
    model_config = {"populate_by_name": True}
 
 
class ConsultaSalidaInstitucion(BaseModel):
    codigo: int
    mensaje: str
    institucion: Optional[InstitucionConsulta] = None
 
 
class ConsultaGeneralSalidaInstitucion(BaseModel):
    codigo: int
    mensaje: str
    instituciones: List[InstitucionConsulta] = []


# ── JORGE ANDRES AVILA MEDINA - EVENTOS ────────────────────────────────────────────────────

EstatusEvento = Literal[
    "Captura", "Revision", "Rechazado", "Autorizado", "Cancelado",
    "Planeacion", "Difusion", "Pospuesto", "Proceso", "Finalizado"
]


class EventoCreate(BaseModel):
    nombre: str
    fechaInicio: datetime
    fechaFin: datetime
    estatus: EstatusEvento
    asistencia: bool


class EventoUpdate(BaseModel):
    nombre: Optional[str] = None
    fechaInicio: Optional[datetime] = None
    fechaFin: Optional[datetime] = None
    estatus: Optional[EstatusEvento] = None
    asistencia: Optional[bool] = None


class EventoConsulta(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nombre: Optional[str] = None
    fechaInicio: Optional[datetime] = None
    fechaFin: Optional[datetime] = None
    estatus: Optional[str] = None
    asistencia: Optional[bool] = None

    model_config = {"populate_by_name": True}


class ConsultaSalidaEvento(Salida):
    evento: Optional[EventoConsulta] = None


class ConsultaGeneralSalidaEvento(Salida):
    eventos: List[EventoConsulta] = []

