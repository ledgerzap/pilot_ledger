from django.shortcuts import render
from django.http import HttpResponse
import firebase_utils
from lz_backend.views import cursor

#cursor = firebase_utils.FirebaseSDK('ledgerzap-firebase.json')


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
    name = request.POST.get('name')
    super_user = request.POST.get('user_uid')
    org_uid = cursor.add_organization(name, super_user)


def my_org(request):
    """
    A function to fetch the names of all registered organizations under the user's id.
    :param request: Http_request containing the information of all the user that is user unique id
    :type request: HTTP_REQUEST
    :return: Response containing the list of all the organization.
    :rtype: HTTP_RESPONSE
    """
    user_uid = request.POST.get('user_uid')
    my_orgs = cursor.fetch_orgs(user_uid)
    return render(request, 'my_orgs.html', {'orgs': my_orgs})


"""
todo : Add the following functions in DashViews:

-Within Orgs:
    -Org Settings
    -Curr Deals
    -Past all deals
    -Add deals

Add URLs to function.
"""
