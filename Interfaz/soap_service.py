from spyne import Application, rpc, ServiceBase, Unicode, Integer, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from .models import Task

class TaskService(ServiceBase):

    @rpc(_returns=Iterable(Unicode))
    def listar_tareas(ctx):
        """Devuelve los títulos de todas las tareas almacenadas en la BD."""
        tareas = Task.objects.all().values_list("title", flat=True)
        for t in tareas:
            yield t

    @rpc(Integer, _returns=Unicode)
    def obtener_tarea_por_id(ctx, id):
        """Devuelve la descripción de una tarea por su ID."""
        try:
            tarea = Task.objects.get(id=id)
            return f"Título: {tarea.title}, Descripción: {tarea.description}"
        except Task.DoesNotExist:
            return "No existe una tarea con ese ID."
        
    @rpc(Unicode, _returns=Iterable(Unicode))
    def listar_tareas_por_estado(ctx, estado):
        """Devuelve los títulos de tareas según su estado lógico."""
        tareas = Task.objects.all()
        for tarea in tareas:
            if tarea.status() == estado:
                yield tarea.title

# Aplicación SOAP
soap_app = Application(
    [TaskService],
    tns='tareas.soap.service',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

soap_application = DjangoApplication(soap_app)
