from django.shortcuts import render
from django.http import HttpResponse

from .models import *

def index(request):
    if request.method =='GET':  
        return render(request, 'index.html')
    if  request.method =='POST':
        usuarios = Usuario.objects.all()
        correo=request.POST['email']
        password=request.POST['password']
        for usuario in usuarios:
            if usuario.correo_usuario==correo and usuario.contrasenia_usuario==password:
                request.session["user"]=correo
                return render(request, 'index.html')
            else:
                context = {
                    "message" : "Error, usuario o contraseña erroneo"
                }
                return render(request, 'index.html', context)

def registro(request):
    if request.method =='GET':  
        comunas = Comuna.objects.all()
        context = {
        "comunas" : comunas
         }
        return render(request, 'registro.html', context)

def desconectar(request):
    if 'user' in request.session:
        del request.session['user']
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

def db(request):
    greeting = Greeting()
    greeting.save()
    greetings = Greeting.objects.all()
    return render(request, 'db.html', {'greetings': greetings})

