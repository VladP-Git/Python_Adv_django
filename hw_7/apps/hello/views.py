from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def hello_name(request):
    # Замените "Иван" на ваше имя
    return HttpResponse("<h1>Hello, Vlad!</h1>")