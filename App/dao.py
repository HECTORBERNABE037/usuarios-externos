from bson import ObjectId
from pymongo import MongoClient
import urllib
from models import *
from datetime import datetime
 
DATABASEURL = "mongodb://localhost:27017/"
DATABASE = 'UsuariosExternos'

class Conexion:
    _cliente = None
    _db = None

    def __init__(self,correo=None,password=None):
        try:
            if correo and password:
                usr = urllib.parse.quote(correo)
                pwd = urllib.parse.quote(password)
                self.DATABASEURL = f'mongodb://{usr}:{pwd}@localhost:27017/?authSource=admin'

            else:
                self.DATABASEURL = 'mongodb://localhost:27017/'

            self._cliente = MongoClient(self.DATABASEURL)
            self._db = self._cliente[DATABASE]
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
        try:
            return  self._db
        except Exception as ex:
            print("Error al obtener la conexion")

class UsuarioDAO:
    def __init__(self,db):
        self.db = db
        self.col=self.db.UsuariosExternos
        self.view=self.db.UsuariosView

    def autenticar(self, correo: str, password: str):
        try:
            result = self.view.find_one({
                "correo": correo,
                "password": password,
                "estatus": {"$in": ["Registrado", "Acreditado"]}
            })

            if result:
                result["_id"] = str(result["_id"])
                if "idInstitucion" in result:
                    result["idInstitucion"] = str(result["idInstitucion"])

                return UsuarioConsulta(**result)
            return None
        except Exception as ex:
            print(f"Error en autenticacion: {ex}")
            return None

    def agregarUsuario(self,usuario:CrearUsuario):
        try:
            salida = Salida(codigo=0,mensaje="")
            #Regla de negocio (comprobar que el correo no exista previamente)
            usuario_existente = self.db.Usuarios.find_one({"correo":usuario.correo})
            if usuario_existente:
                salida.codigo=409
                salida.mensaje=f"El usuario con el correo {usuario.correo} ya existe"
                return salida
            data=usuario.model_dump()
            data['fechaRegistro']=datetime.utcnow()
            data['estatus']='Registrado'
            data['rol']='Usuario'
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

    def consultarPorId(self,idUsuario:str):
        salida = ConsultaSalida(codigo=0,mensaje="",usuario=None)
        try:
            usuario_existente=self.db["UsuariosView"].find_one({"_id":ObjectId(idUsuario)})
            if usuario_existente:
                usuario_existente["idInstitucion"]=str(usuario_existente["idInstitucion"])
                salida.codigo=200
                salida.mensaje="El usuario se encontro exitosamenente"
                salida.usuario= UsuarioConsulta(**usuario_existente)
                return salida
            else:
                salida.codigo=404
                salida.mensaje="El usuario no existe"
                return salida
        except Exception as ex:
            salida.codigo=500
            salida.mensaje=f"Error al buscar el usuario: {ex}"
            return salida

    def modificarUsuario(self,usuario:ModificarUsuario,idUsuario:str,rol:str):
        salida = Salida(codigo=0,mensaje="")
        try:
            usuario_recuperado = self.db.Usuarios.find_one({"_id":ObjectId(idUsuario)})
            if not(usuario_recuperado):
                salida.codigo=404
                salida.mensaje="El usuario no existe"
                return salida
            data = usuario.model_dump(exclude_unset=True)

            if not data.keys():
                salida.codigo=400
                salida.mensaje="Debes proporcionar informacion para realizar la modificacion"
                return salida
            es_admin = rol.lower() in ["organizador","supervisor"]
            estatus_actual = usuario_recuperado['estatus']

            if estatus_actual in ["Eliminado","Bloqueado"]:
                salida.codigo=409
                salida.mensaje=f"El usuario se encuentra {estatus_actual}"
                return salida

            if 'correo' in data:
                if data['correo']!=usuario_recuperado.get('correo'):
                    correo_existente = self.db.Usuarios.find_one({"correo":data['correo']})
                    if correo_existente:
                        salida.codigo=409
                        salida.mensaje=f"El correo {data['correo']} ya existe"
                        return salida

            campos_restringidos = ["estatus","tipo","rol"]
            for campo in campos_restringidos:
                if campo in data and not es_admin:
                    salida.codigo=403
                    salida.mensaje=f"No tienes permisos de Organizador para modificar el campo: {campo}"
                    return salida

            if 'idInstitucion' in data:
                institucion_existe = self.db.Instituciones.find_one({"_id":ObjectId(data['idInstitucion'])})
                if not institucion_existe:
                    salida.codigo=404
                    salida.mensaje="La institucion proporcionda no existe"
                    return salida
                data['idInstitucion']=ObjectId(data['idInstitucion'])

            if 'idEvento' in data and data['idEvento']:
                ids_eventos = [ObjectId(ev) for ev in data['idEvento']]
                eventos_existentes = self.db.Eventos.count_documents({"_id":{"$in":ids_eventos}})
                if eventos_existentes != len(ids_eventos):
                    salida.codigo=404
                    salida.mensaje="Uno o mas eventos introducidos no existen"
                    return salida
                data['idEvento']=ids_eventos
            data.pop('fechaRegistro',None)

            result = self.db.Usuarios.update_one({"_id":ObjectId(idUsuario)},{"$set":data})

            if result.modified_count > 0:
                salida.codigo=200
                salida.mensaje=f"Usuario modificado con exito"
        except Exception as ex:
            salida.codigo=500
            salida.mensaje=f'Error interno del servidor al modificar el usuario {idUsuario} por el error {ex}'
        return salida

    def AdminModificarUsuario(self, usuario: AdminModificarUsuario, idUsuario: str, rol: str):
        salida = Salida(codigo=0, mensaje="")

        try:
            usuario_recuperado = self.db.Usuarios.find_one({"_id": ObjectId(idUsuario)})
            if not (usuario_recuperado):
                salida.codigo = 404
                salida.mensaje = "El usuario no existe"
                return salida
            data = usuario.model_dump(exclude_unset=True)

            if not data.keys():
                salida.codigo = 400
                salida.mensaje = "Debes proporcionar informacion para realizar la modificacion"
                return salida
            es_admin = rol.lower() in ["organizador", "supervisor"]
            estatus_actual = usuario_recuperado['estatus']

            if not es_admin:
                salida.codigo = 403
                salida.mensaje = "No tienes permisos necesarios"
                return salida

            if 'correo' in data:
                if data['correo'] != usuario_recuperado.get('correo'):
                    correo_existente = self.db.Usuarios.find_one({"correo": data['correo']})
                    if correo_existente:
                        salida.codigo = 409
                        salida.mensaje = f"El correo {data['correo']} ya existe"
                        return salida

            if 'idInstitucion' in data:
                institucion_existe = self.db.Instituciones.find_one({"_id": ObjectId(data['idInstitucion'])})
                if not institucion_existe:
                    salida.codigo = 404
                    salida.mensaje = "La institucion proporcionda no existe"
                    return salida
                data['idInstitucion'] = ObjectId(data['idInstitucion'])

            if 'idEvento' in data and data['idEvento']:
                ids_eventos = [ObjectId(ev) for ev in data['idEvento']]
                eventos_existentes = self.db.Eventos.count_documents({"_id": {"$in": ids_eventos}})
                if eventos_existentes != len(ids_eventos):
                    salida.codigo = 404
                    salida.mensaje = "Uno o mas eventos introducidos no existen"
                    return salida
                data['idEvento'] = ids_eventos
            data.pop('fechaRegistro', None)

            result = self.db.Usuarios.update_one({"_id": ObjectId(idUsuario)}, {"$set": data})

            if result.modified_count > 0:
                salida.codigo = 200
                salida.mensaje = f"Usuario modificado con exito"
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f'Error interno del servidor al modificar el usuario {idUsuario} por el error {ex}'
        return salida

    def ModificarPerfilUsuario(self,idUsuario,perfil_usuario:PerfilUsuario):
        salida=Salida(codigo=0,mensaje="")
        usuario_consultado = self.consultarPorId(idUsuario)
        estatus_valido= ["Registrado","Acreditado"]
        data = perfil_usuario.model_dump(exclude_unset=True)
        if usuario_consultado.codigo == 200:
            if usuario_consultado.usuario.estatus in estatus_valido:
                if data:
                    datos_anidados ={f"perfilUsuario.{key}":value for key,value in data.items()}
                    result = self.db.Usuarios.update_one({"_id":ObjectId(idUsuario)},{"$set":datos_anidados})
                    if result.modified_count > 0:
                        salida.codigo = 200
                        salida.mensaje = f"el perfil del Usuario modificado con exito"
                    else:
                        salida.codigo = 200
                        salida.mensaje = "No se realizaron cambios. Los datos enviados son identicos"
                else:
                    salida.codigo = 400
                    salida.mensaje = "Debes ingresar informacion para actualizar"
            else:
                salida.codigo = 403
                salida.mensaje = f"El usuario {idUsuario} no tiene un estatus valido"
        else:
            salida.codigo = 404
            salida.mensaje = f"El usuario {idUsuario} no existe"
        return salida


    def BorrarUsuario(self,idUsuario):
        salida=Salida(codigo=0,mensaje="")
        usuario_consultado = self.consultarPorId(idUsuario)
        estatus_valido= "Eliminado"

        if usuario_consultado.codigo == 200:
            if usuario_consultado.usuario.estatus == estatus_valido:
                salida.codigo = 200
                salida.mensaje = f"El usuario ya se encontraba {estatus_valido}"
            else:
                result = self.db.Usuarios.update_one({"_id": ObjectId(idUsuario)}, {"$set": {"estatus": estatus_valido}})
                if result.modified_count > 0:
                    salida.codigo = 200
                    salida.mensaje = "Usuario modificado con exito"
        else:
            salida.codigo = 404
            salida.mensaje = "El usuario no existe"
        return salida

    def consultaGeneral(self):
        salida=ConsultaGeneralSalida(codigo=0,mensaje="",usuarios=[])
        try:
            lista_usuarios=list(self.db["UsuariosView"].find())
            lista_limpia=[]
            for usuario_db in lista_usuarios:
                if "idInstitucion" in usuario_db:
                    usuario_db["idInstitucion"] = str(usuario_db["idInstitucion"])
                usuario_validado = UsuarioConsulta(**usuario_db)
                lista_limpia.append(usuario_validado)

            salida.codigo = 200
            salida.mensaje = "Listado de usuarios"
            salida.usuarios = lista_limpia

        except Exception as ex:
            salida.codigo = 404
            salida.mensaje = "Error al consultar"
        return salida

    def consultaPorEstatus(self,estatus:str)->ConsultaGeneralSalida:
        salida=ConsultaGeneralSalida(codigo=0,mensaje="",usuarios=[])
        try:
            lista_usuarios=list(self.db["UsuariosView"].find({"estatus": estatus}))
            lista_limpia=[]
            for usuario_db in lista_usuarios:
                if "idInstitucion" in usuario_db:
                    usuario_db["idInstitucion"] = str(usuario_db["idInstitucion"])
                usuario_validado = UsuarioConsulta(**usuario_db)
                lista_limpia.append(usuario_validado)

            salida.codigo = 200
            salida.mensaje = "Listado de usuarios"
            salida.usuarios = lista_limpia

        except Exception as ex:
            salida.codigo = 404
            salida.mensaje = "Error al consultar"
        return salida

    def acreditarAcceso (self,idUsuario:str):
        usuario_consultado = self.consultarPorId(idUsuario)
        salida = Salida(codigo=0,mensaje="")
        estatus_valido = "Registrado"
        if usuario_consultado.codigo == 200:
            estatus_actual=usuario_consultado.usuario.estatus
            if estatus_actual != estatus_valido:
                salida.codigo = 409
                salida.mensaje = "El ya esta acreditado o se encuentra eliminado"
            else:
                result = self.db.Usuarios.update_one({"_id":ObjectId(idUsuario)}, {"$set": {"estatus": "Acreditado"}})
                if result.modified_count > 0:
                    salida.codigo = 200
                    salida.mensaje = f"Usuario acreditado con exito"
                else:
                    salida.codigo = 500
                    salida.mensaje = "Error al acreditar el usuario"
        else:
            salida.codigo = 404
            salida.mensaje = "Usuario no existe"
        return salida

# ── JESUS ESTRADA ALEJANDRE ───────────────────────────────────────────────

# ─────────────────────────────────────────────
# DAO de Institución
# ─────────────────────────────────────────────
class InstitucionDAO:
    def __init__(self, db):
        self.db = db
        self.col = self.db.Instituciones
 
    def agregarInstitucion(self, institucion: InstitucionCreate, rol: str) -> Salida:
        salida = Salida(codigo=0, mensaje="")
        try:
            # Validar permisos: solo Supervisor y Organizador pueden crear instituciones
            es_admin = rol.lower() in ["organizador", "supervisor"]
            if not es_admin:
                salida.codigo = 403
                salida.mensaje = f"No tienes permisos para crear instituciones. Tu rol '{rol}' no tiene acceso."
                return salida
            
            # Regla de negocio: comprobar que no exista ya una institución con el mismo nombre
            institucion_existente = self.db.Instituciones.find_one({"nombre": institucion.nombre})
            if institucion_existente:
                salida.codigo = 409
                salida.mensaje = f"Ya existe una institucion con el nombre '{institucion.nombre}'"
                return salida
            data = institucion.model_dump()
            data['fechaRegistro'] = datetime.utcnow()
            result = self.db.Instituciones.insert_one(data)
            salida.codigo = 201
            salida.mensaje = f"Institucion creada exitosamente con id {result.inserted_id}"
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al agregar institucion: {ex}"
        return salida
 
    def consultarPorId(self, idInstitucion: str) -> ConsultaSalidaInstitucion:
        salida = ConsultaSalidaInstitucion(codigo=0, mensaje="", institucion=None)
        try:
            institucion_existente = self.db.Instituciones.find_one({"_id": ObjectId(idInstitucion)})
            if institucion_existente:
                institucion_existente["_id"] = str(institucion_existente["_id"])
                salida.codigo = 200
                salida.mensaje = "La institucion se encontro exitosamente"
                salida.institucion = InstitucionConsulta(**institucion_existente)
                return salida
            else:
                salida.codigo = 404
                salida.mensaje = "La institucion no existe"
                return salida
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al buscar la institucion: {ex}"
            return salida
 
    def consultaGeneral(self) -> ConsultaGeneralSalidaInstitucion:
        salida = ConsultaGeneralSalidaInstitucion(codigo=0, mensaje="", instituciones=[])
        try:
            lista_instituciones = list(self.db.Instituciones.find())
            lista_limpia = []
            for inst_db in lista_instituciones:
                inst_db["_id"] = str(inst_db["_id"])
                institucion_validada = InstitucionConsulta(**inst_db)
                lista_limpia.append(institucion_validada)
            salida.codigo = 200
            salida.mensaje = "Listado de instituciones"
            salida.instituciones = lista_limpia
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al consultar instituciones: {ex}"
        return salida
 
    def consultarPorNombre(self, nombre: str) -> ConsultaGeneralSalidaInstitucion:
        salida = ConsultaGeneralSalidaInstitucion(codigo=0, mensaje="", instituciones=[])
        try:
            lista_instituciones = list(self.db.Instituciones.find(
                {"nombre": {"$regex": nombre.strip(), "$options": "i"}}
            ))
            lista_limpia = []
            for inst_db in lista_instituciones:
                inst_db["_id"] = str(inst_db["_id"])
                institucion_validada = InstitucionConsulta(**inst_db)
                lista_limpia.append(institucion_validada)
            if lista_limpia:
                salida.codigo = 200
                salida.mensaje = f"Se encontraron {len(lista_limpia)} institucion(es) con nombre '{nombre}'"
                salida.instituciones = lista_limpia
            else:
                salida.codigo = 404
                salida.mensaje = f"No se encontro ninguna institucion con nombre '{nombre}'"
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al buscar institucion por nombre: {ex}"
        return salida
 
    def consultarPorCiudad(self, ciudad: str) -> ConsultaGeneralSalidaInstitucion:
        salida = ConsultaGeneralSalidaInstitucion(codigo=0, mensaje="", instituciones=[])
        try:
            lista_instituciones = list(self.db.Instituciones.find(
                {"ciudad": {"$regex": ciudad.strip(), "$options": "i"}}
            ))
            lista_limpia = []
            for inst_db in lista_instituciones:
                inst_db["_id"] = str(inst_db["_id"])
                institucion_validada = InstitucionConsulta(**inst_db)
                lista_limpia.append(institucion_validada)
            if lista_limpia:
                salida.codigo = 200
                salida.mensaje = f"Se encontraron {len(lista_limpia)} institucion(es) en la ciudad '{ciudad}'"
                salida.instituciones = lista_limpia
            else:
                salida.codigo = 404
                salida.mensaje = f"No se encontro ninguna institucion en la ciudad '{ciudad}'"
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al buscar institucion por ciudad: {ex}"
        return salida
 
    def modificarInstitucion(self, idInstitucion: str, datos: InstitucionUpdate, rol: str) -> Salida:
        salida = Salida(codigo=0, mensaje="")
        try:
            # Validar permisos: solo Supervisor y Organizador pueden modificar instituciones
            es_admin = rol.lower() in ["organizador", "supervisor"]
            if not es_admin:
                salida.codigo = 403
                salida.mensaje = f"No tienes permisos para modificar instituciones. Tu rol '{rol}' no tiene acceso."
                return salida
            
            institucion_recuperada = self.db.Instituciones.find_one({"_id": ObjectId(idInstitucion)})
            if not institucion_recuperada:
                salida.codigo = 404
                salida.mensaje = "La institucion no existe"
                return salida
            data = datos.model_dump(exclude_unset=True)
            if not data.keys():
                salida.codigo = 400
                salida.mensaje = "Debes proporcionar informacion para realizar la modificacion"
                return salida
            # Regla de negocio: si se cambia el nombre, verificar que no lo tenga otra institución
            if 'nombre' in data:
                if data['nombre'] != institucion_recuperada.get('nombre'):
                    nombre_existente = self.db.Instituciones.find_one({"nombre": data['nombre']})
                    if nombre_existente:
                        salida.codigo = 409
                        salida.mensaje = f"Ya existe una institucion con el nombre '{data['nombre']}'"
                        return salida
            result = self.db.Instituciones.update_one(
                {"_id": ObjectId(idInstitucion)},
                {"$set": data}
            )
            if result.modified_count > 0:
                salida.codigo = 200
                salida.mensaje = "Institucion modificada con exito"
            else:
                salida.codigo = 200
                salida.mensaje = "No se realizaron cambios. Los datos enviados son identicos"
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error interno del servidor al modificar la institucion {idInstitucion} por el error {ex}"
        return salida
 
    def eliminarInstitucion(self, idInstitucion: str, rol: str) -> Salida:
        salida = Salida(codigo=0, mensaje="")
        
        # Validar permisos: solo Supervisor puede eliminar instituciones
        es_supervisor = rol.lower() == "supervisor"
        if not es_supervisor:
            salida.codigo = 403
            salida.mensaje = f"No tienes permisos para eliminar instituciones. Solo Supervisor puede eliminar. Tu rol es '{rol}'."
            return salida
        
        institucion_consultada = self.consultarPorId(idInstitucion)
        if institucion_consultada.codigo == 200:
            try:
                result = self.db.Instituciones.delete_one({"_id": ObjectId(idInstitucion)})
                if result.deleted_count > 0:
                    salida.codigo = 200
                    salida.mensaje = "Institucion eliminada con exito"
                else:
                    salida.codigo = 500
                    salida.mensaje = "Error al eliminar la institucion"
            except Exception as ex:
                salida.codigo = 500
                salida.mensaje = f"Error al eliminar la institucion: {ex}"
        else:
            salida.codigo = 404
            salida.mensaje = "La institucion no existe"
        return salida


# ── EVENTOS - JORGE ANDRES AVILA MEDINA ──────────────────────────────────────────────────────────────────

class EventoDAO:
    def __init__(self, db):
        self.db = db
        self.col = self.db.Eventos

    def agregarEvento(self, evento: EventoCreate, rol: str) -> Salida:
        salida = Salida(codigo=0, mensaje="")
        try:
            if rol.lower() not in ["supervisor", "organizador"]:
                salida.codigo = 403
                salida.mensaje = f"No tienes permisos para crear eventos. Tu rol '{rol}' no tiene acceso."
                return salida

            evento_existente = self.col.find_one({"nombre": evento.nombre})
            if evento_existente:
                salida.codigo = 409
                salida.mensaje = f"Ya existe un evento con el nombre '{evento.nombre}'"
                return salida

            if evento.fechaFin < evento.fechaInicio:
                salida.codigo = 400
                salida.mensaje = "La fechaFin no puede ser anterior a la fechaInicio"
                return salida

            data = evento.model_dump()
            result = self.col.insert_one(data)

            salida.codigo = 201
            salida.mensaje = f"Evento creado exitosamente con id {result.inserted_id}"

        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al agregar evento: {ex}"

        return salida

    def consultarPorId(self, idEvento: str) -> ConsultaSalidaEvento:
        salida = ConsultaSalidaEvento(codigo=0, mensaje="", evento=None)
        try:
            evento_existente = self.col.find_one({"_id": ObjectId(idEvento)})
            if evento_existente:
                evento_existente["_id"] = str(evento_existente["_id"])
                salida.codigo = 200
                salida.mensaje = "El evento se encontro exitosamente"
                salida.evento = EventoConsulta(**evento_existente)
                return salida
            else:
                salida.codigo = 404
                salida.mensaje = "El evento no existe"
                return salida
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al buscar el evento: {ex}"
            return salida

    def consultaGeneral(self) -> ConsultaGeneralSalidaEvento:
        salida = ConsultaGeneralSalidaEvento(codigo=0, mensaje="", eventos=[])
        try:
            lista_eventos = list(self.col.find())
            lista_limpia = []
            for ev_db in lista_eventos:
                ev_db["_id"] = str(ev_db["_id"])
                evento_validado = EventoConsulta(**ev_db)
                lista_limpia.append(evento_validado)
            salida.codigo = 200
            salida.mensaje = "Listado de eventos"
            salida.eventos = lista_limpia
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al consultar eventos: {ex}"
        return salida

    def consultarPorEstatus(self, estatus: str) -> ConsultaGeneralSalidaEvento:
        salida = ConsultaGeneralSalidaEvento(codigo=0, mensaje="", eventos=[])
        try:
            lista_eventos = list(self.col.find({"estatus": estatus}))
            lista_limpia = []
            for ev_db in lista_eventos:
                ev_db["_id"] = str(ev_db["_id"])
                evento_validado = EventoConsulta(**ev_db)
                lista_limpia.append(evento_validado)
            salida.codigo = 200
            salida.mensaje = f"Listado de eventos con estatus '{estatus}'"
            salida.eventos = lista_limpia
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al consultar eventos por estatus: {ex}"
        return salida

    def modificarEvento(self, idEvento: str, datos: EventoUpdate, rol: str) -> Salida:
        salida = Salida(codigo=0, mensaje="")
        try:
            if rol.lower() not in ["supervisor", "organizador", "usuario"]:
                salida.codigo = 403
                salida.mensaje = f"No tienes permisos para modificar eventos. Tu rol '{rol}' no tiene acceso."
                return salida

            evento_recuperado = self.col.find_one({"_id": ObjectId(idEvento)})
            if not evento_recuperado:
                salida.codigo = 404
                salida.mensaje = "El evento no existe"
                return salida

            data = datos.model_dump(exclude_unset=True)
            if not data:
                salida.codigo = 400
                salida.mensaje = "Debes proporcionar informacion para realizar la modificacion"
                return salida

            fecha_inicio = data.get("fechaInicio", evento_recuperado.get("fechaInicio"))
            fecha_fin = data.get("fechaFin", evento_recuperado.get("fechaFin"))

            if fecha_fin < fecha_inicio:
                salida.codigo = 400
                salida.mensaje = "La fechaFin no puede ser anterior a la fechaInicio"
                return salida

            if "nombre" in data and data["nombre"] != evento_recuperado.get("nombre"):
                nombre_existente = self.col.find_one({"nombre": data["nombre"]})
                if nombre_existente:
                    salida.codigo = 409
                    salida.mensaje = f"Ya existe un evento con el nombre '{data['nombre']}'"
                    return salida

            result = self.col.update_one({"_id": ObjectId(idEvento)}, {"$set": data})

            if result.modified_count > 0:
                salida.codigo = 200
                salida.mensaje = "Evento modificado con exito"
            else:
                salida.codigo = 200
                salida.mensaje = "No se realizaron cambios. Los datos enviados son identicos"

        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error interno del servidor al modificar el evento {idEvento}: {ex}"

        return salida

    def eliminarEvento(self, idEvento: str, rol: str) -> Salida:
        salida = Salida(codigo=0, mensaje="")
        try:
            if rol.lower() != "supervisor":
                salida.codigo = 403
                salida.mensaje = f"No tienes permisos para eliminar eventos. Solo Supervisor puede eliminar. Tu rol es '{rol}'."
                return salida

            evento_existente = self.col.find_one({"_id": ObjectId(idEvento)})
            if not evento_existente:
                salida.codigo = 404
                salida.mensaje = "El evento no existe"
                return salida

            usuarios_inscritos = self.db.Usuarios.count_documents({"idEvento": ObjectId(idEvento)})
            if usuarios_inscritos > 0:
                salida.codigo = 409
                salida.mensaje = (
                    f"No se puede eliminar el evento porque tiene {usuarios_inscritos} "
                    f"usuario(s) inscrito(s). Desinscríbalos primero."
                )
                return salida

            result = self.col.delete_one({"_id": ObjectId(idEvento)})

            if result.deleted_count > 0:
                salida.codigo = 200
                salida.mensaje = "Evento eliminado con exito"
            else:
                salida.codigo = 500
                salida.mensaje = "Error al eliminar el evento"

        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error al eliminar el evento: {ex}"

        return salida
