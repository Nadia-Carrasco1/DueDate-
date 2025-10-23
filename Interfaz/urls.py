from django.urls import path
from . import views

urlpatterns = [
    path("api/tareas/", views.listar_tareas_rest, name="listar_tareas_rest"),
    path("api/tareas/<int:id>/", views.obtener_tarea_por_id_rest, name="obtener_tarea_por_id_rest"),
    path("api/tareas/estado/<str:estado>/", views.listar_tareas_por_estado_rest, name="listar_tareas_por_estado_rest"),
]
