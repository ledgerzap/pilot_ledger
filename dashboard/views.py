from django.shortcuts import render
from django.http import HttpResponse
from firebase_utils import app

# Create your views here.
def dashboard(request):
    org_ref = app.fetch_firestore('organizations')
    return render(request, 'dashboard.html', info)


def createorg(request):
    return render(request, 'createorg.html', {})


def postcreateorg(request):
    name = request.POST.get('name')
    details = {'name':name, 'user': 'mud'}
    app.add_to_firestore(details, 'organizations')
    return HttpResponse("org created")



