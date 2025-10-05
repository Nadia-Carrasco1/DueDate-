from django.shortcuts import render, redirect
from .models import Task
from django.utils import timezone
from django.contrib import messages
def home_view(request):
    return render(request, 'home_page.html') 

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