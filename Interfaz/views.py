from django.shortcuts import render, redirect
from .models import Task
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .soap_service import soap_application
from Interfaz.utils.soap_client import listar_tareas_por_estado_soap, listar_tareas_soap, obtener_tarea_por_id_soap
from celery import shared_task
from django.core.mail import send_mail
from pytz import timezone as pytz_timezone

def home_view(request):
    return render(request, 'home_page.html') 

TIMEZONE_ARGENTINA = pytz_timezone('America/Argentina/Buenos_Aires')
#REMINDER_OFFSET = timedelta(days=1)
REMINDER_OFFSET = timedelta(minutes=1)

@login_required
def add_task(request):
    if request.method == "POST":
        recipient_email = request.user.email
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        due_date_str = request.POST.get("due_date")
        reminder_checked = 'reminder' in request.POST
        
        due_date_obj = None
        if due_date_str:
            try:
                due_date_obj = datetime.fromisoformat(due_date_str)
                due_date_obj = timezone.make_aware(due_date_obj, timezone.get_current_timezone())
            except ValueError:
                messages.error(request, "El formato de fecha y hora no es válido.")
                return redirect("/")

        task = Task.objects.create(
            title=title,
            description=description,
            due_date=due_date_obj,
            completed=False,
            reminder=reminder_checked
        )

        if reminder_checked and task.due_date:
            due_date_timezone = task.due_date.astimezone(TIMEZONE_ARGENTINA)
            #reminder_time = due_date_timezone - REMINDER_OFFSET
            reminder_time = due_date_timezone + REMINDER_OFFSET

            if reminder_time > timezone.now():
                enviar_mail_recordatorio.apply_async(
                    args=[
                        task.title,
                        recipient_email
                    ],
                    eta=reminder_time
                )
                messages.info(request, f"Recordatorio programado para el {reminder_time.strftime('%d/%m/%Y a las %H:%M')}.")
            else:
                messages.warning(request, "La fecha del recordatorio ya ha pasado. Tarea guardada sin programación.")
       
        messages.success(request, "Tarea agregada con éxito 🎉")
        return redirect("/")

    return redirect("/")

@shared_task
def enviar_mail_recordatorio(task_title, recipient_email):
    subject = f"Recordatorio programado: {task_title}"
    message = (
        f"Hola!,\n\n"
        f"Tu tarea: '{task_title}' vence mañana.\n"
        f"No olvides completarla!"
    )

    send_mail (
        subject,
        message,
        None,
        [recipient_email],
        fail_silently=False
    )

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