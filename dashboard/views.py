from django.shortcuts import render
from django.http import HttpResponse
import firebase_utils

cursor = firebase_utils.FirebaseSDK('ledgerzap-firebase.json')

def dashboard(request):
    return render(request, 'dashboard.html', {})

def create_org(request):
    """
    A function which responds to the user's request to create a organization.
    :param request: Http Request, requesting the create organization page
    :type request: HTTP_REQUEST
    :return: Http response containing the create org page
    :rtype: HTTP_RESPONSE
    """
    return render(request, 'create_org.html', {})

def post_create_org(request):
    """
    Function which creates an organization instance in firebase and redirects to the user back to the dashboard. The
    user can access the organization from the section under my organization.
    :param request: Http request containing the organization's information
    :type request: HTTP_REQUEST
    :return: Http Response containing the Dashboard of the user.
    :rtype: HTTP_RESPONSE
    """
    pass

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