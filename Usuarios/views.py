from django.shortcuts import render, redirect
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.core.mail import send_mail
from .forms import RegistroForm


def Registrarse(request):
      
    if request.method == 'GET':
        return render(request, 'Registrarse.html',{
        'form': RegistroForm()
        })
    else:
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)

                # Enviar correo de bienvenida
                send_mail(
                    subject='Bienvenida a Due_Date',
                    message='Tu cuenta fue creada exitosamente.',
                    from_email='Due Date <nadia.carrasco@est.fi.uncoma.edu.ar>',
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                return redirect('home')
            except IntegrityError:
                return render(request, 'Registrarse.html', {
                    'form': RegistroForm(),
                    "error": 'El usuario ya existe'
                })
        return render(request, 'Registrarse.html', {
            'form': form,
            "error": 'Las contraseñas no coinciden o el formulario es inválido'
        })

def CerrarSesion(request):
    logout(request)
    return redirect('home')

def IniciarSesion(request):
    if request.method == 'GET':
        return render(request, 'IniciarSesion.html', {
            'form': AuthenticationForm,
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'IniciarSesion.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrecta'
            })       
        else:
            login(request, user)
            return redirect('home')
