from bson import ObjectId
from pymongo import MongoClient
from models import *
from datetime import datetime

DATABASEURL = "mongodb://localhost:27017"
DATABASE = 'UsuariosExternos'

class Conexion:
    _cliente = None
    _db = None

    def __init__(self):
        try:
            self._cliente = MongoClient(DATABASEURL)
            self._db = self._cliente.UsuariosExternos
            print(f"Conexion exitosa con la base de datos: {DATABASE}")
        except Exception as ex:
            print(f"Error al conectar con la base de datos por el error: {ex}")

    def cerrar(self):
        try:
            print(f"Conexcion cerrada: {DATABASE}")
        except Exception as ex:
            print(f"Error al cerrar con la base de datos por el error: {ex}")
    @property
    def db(self):
        return self._db

class UsuarioDAO:
    def __init__(self,db):
        self.db = db
        self.col=self.db.UsuariosExternos
        self.view=self.db.UsuariosView

    def agregarUsuario(self,usuario:CrearUsuario):
        try:
            salida = Salida(codigo=0,mensaje="")
            data=usuario.model_dump()
            data['fechaRegistro']=datetime.utcnow()
            data['estatus']='Registrado'
            #convertimos los strings a objectId
            data['idInstitucion']=ObjectId(usuario.idInstitucion)
            if 'idEventos' in data and data['idEventos']:
                data['idEventos'] = [ObjectId(id_ev) for id_ev in data['idEventos']]

            result=self.db.Usuarios.insert_one(data)
            salida.codigo=201
            salida.mensaje=f"El usuario creado exitosamnente con id {result.inserted_id}"
        except Exception as ex:
            salida.codigo=500
            salida.mensaje=f"Error al agregar usuario: {ex}"
        return salida