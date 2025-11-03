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

import datetime
import os
from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime
import pytz
import json

TIMEZONE_ARGENTINA = pytz_timezone('America/Argentina/Buenos_Aires')
#REMINDER_OFFSET = timedelta(days=1)
REMINDER_OFFSET = timedelta(minutes=1)



def home_view(request):
    return render(request, 'home_page.html')

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
        due_date = request.POST.get("due_date")
        sync_calendar = request.POST.get("sync_calendar") 

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
        if sync_calendar and 'credentials' in request.session:
            creds_data = request.session['credentials']
            creds = Credentials(**creds_data)

            try:
                parsed_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M")
                iso_date = parsed_date.isoformat()

                service = build('calendar', 'v3', credentials=creds)
                event = {
                    'summary': title,
                    'description': description,
                    'start': {'dateTime': iso_date, 'timeZone': 'America/Argentina/Buenos_Aires'},
                    'end': {'dateTime': iso_date, 'timeZone': 'America/Argentina/Buenos_Aires'},
                }
                service.events().insert(calendarId='primary', body=event).execute()
                messages.success(request, "Tarea agregada y sincronizada con Google Calendar")

            except Exception as e:
                messages.warning(request, f"Tarea agregada, pero hubo un problema con Google Calendar: {e}")

        else:
            messages.success(request, "Tarea agregada con éxito")

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

def google_authorize(request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["https://www.googleapis.com/auth/calendar.events"]
    )

    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    request.session['state'] = state
    return redirect(authorization_url)


def oauth2callback(request):
    """Recibe el token de Google y lo guarda en la sesión del usuario."""
    state = request.session['state']
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["https://www.googleapis.com/auth/calendar.events"],
        state=state
    )

    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    messages.success(request, "Conectado con Google Calendar")
    return redirect("/")
