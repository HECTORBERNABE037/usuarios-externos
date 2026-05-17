from pydantic import BaseModel
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
    telefono: str
    correo: str
    #fechaRegistro: datetime
    #estatus: str
    tipo:Literal["Expositor","expositor","participante","Participante","Invitado", "invitado"]
    idInstitucion:str
    idEvento:List[str] = []
    perfilUsuario: Optional[PerfilUsuario] = None





