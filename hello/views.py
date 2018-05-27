from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting
from .models import Comuna

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')
def comunas(request):
    # return HttpResponse('Hello from Python!')
    obj = Comuna.objects.all()
    for abc in obj:
        obj_nombres = abc.nombre_comuna
    
    context = {
        "obj" : obj
    }
    return render(request, 'comunas.html', context)


def db(request):
    greeting = Greeting()
    greeting.save()
    greetings = Greeting.objects.all()
    return render(request, 'db.html', {'greetings': greetings})

