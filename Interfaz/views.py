from django.shortcuts import render, redirect
from .models import Task
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .soap_service import soap_application
from Interfaz.utils.soap_client import listar_tareas_por_estado_soap, listar_tareas_soap, obtener_tarea_por_id_soap

def home_view(request):
    return render(request, 'home_page.html') 

@login_required
def add_task(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        due_date = request.POST.get("due_date")

        Task.objects.create(
            title=title,
            description=description,
            due_date=due_date if due_date else None,
            completed=False
        )
        messages.success(request, "Tarea agregada con éxito 🎉")
        return redirect("/")

    return redirect("/")

@csrf_exempt
def soap_view(request):
    """Vista que expone el servicio SOAP."""
    response = soap_application(request)
    return response

def listar_tareas_rest(request):
    tareas = listar_tareas_soap()
    return JsonResponse({"tareas": tareas})

def obtener_tarea_por_id_rest(request, id):
    tarea = obtener_tarea_por_id_soap(id)
    return JsonResponse({"id": id, "descripcion": tarea})

def listar_tareas_por_estado_rest(request, estado):
    tareas = listar_tareas_por_estado_soap(estado)
    return JsonResponse({"estado": estado, "tareas": tareas})
