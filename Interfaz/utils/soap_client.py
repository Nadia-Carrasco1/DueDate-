from zeep import Client

SOAP_URL = "http://127.0.0.1:8000/soap/?wsdl"

def listar_tareas_soap():
    client = Client(SOAP_URL)
    response = client.service.listar_tareas()
    return list(response)

def obtener_tarea_por_id_soap(task_id):
    client = Client(SOAP_URL)
    response = client.service.obtener_tarea_por_id(task_id)
    return str(response)

def listar_tareas_por_estado_soap(estado):
    client = Client(SOAP_URL)
    response = client.service.listar_tareas_por_estado(estado)
    return list(response)