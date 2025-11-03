# Due_Date/celery.py

import os
from celery import Celery

# Asegúrate de que esta línea contenga el guion bajo
# Esto le dice a Celery dónde está settings.py (Due_Date.settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Due_Date.settings') 

# El nombre de la aplicación puede ser sin guion bajo, pero es mejor ser coherente:
app = Celery('Due_Date')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()