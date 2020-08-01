from django.shortcuts import render
from django.http import HttpResponse
import firebase_utils


def dashboard(request):
    return render(request, 'dashboard.html', {})

"""
# todo : Add the following functions in DashViews:
-Create org
-My Orgs
-Within Orgs:
    -Org Settings
    -Curr Deals
    -Past all deals
    -Add deals
"""