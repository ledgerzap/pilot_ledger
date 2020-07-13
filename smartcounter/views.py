from django.http import HttpResponse
from django.shortcuts import render

def homepage(request):
    return render(request, 'homepage.html', {})

def auth(request):
    email = request.POST.get('email')
    passwd = request.POST.get('passwd')
    
    return HttpResponse("WELCOME")
    pass
