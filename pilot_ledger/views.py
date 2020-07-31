from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import auth
import firebase_utils


firebaseConfig = {
    'apiKey': "AIzaSyAbVymBBzthUgBOt4RcL1MvxWf7LfKOISk",
    'authDomain': "ledgerzap.firebaseapp.com",
    'databaseURL': "https://ledgerzap.firebaseio.com",
    'projectId': "ledgerzap",
    'storageBucket': "ledgerzap.appspot.com",
    'messagingSenderId': "767427613315",
    'appId': "1:767427613315:web:1f85d1e72c30bef88cc1b6",
    'measurementId': "G-2CBEVQ99KF"
}
cursor = firebase_utils.FirebaseSDK('ledgerzap-firebase.json')


def homepage(request):
    """
    This function renders and redirects to the homepage or sign in page of the application.
    :param request: Http request
    :type request: HTTP_REQUEST
    :return: Http Request with the homepage
    :rtype: HTTP_RESPONSE
    """
    return render(request, 'homepage.html', {})


def authenticate(request):
    """
    This Function authenticates the user and redirects them to the dashboard window. If authentication fails error
    message is displayed and the user returns to the homepage.
    :param request: Http request containing the username and password.
    :type request: HTTP_REQUEST
    :return: Http response with the dashboard window.
    :rtype: HTTP_RESPONSE
    """
    email = request.POST.get('email')
    passwd = request.POST.get('passwd')
    print(email, passwd)
    res = cursor.signin_using_email_pass(email, passwd)
    if res:
        return redirect('/dashboard/')
    else:
        return HttpResponse("try again")

def signup(request):
    return render(request, 'signup.html', {})


def postsignup(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    passwd = request.POST.get("passwd")
    rpasswd = request.POST.get("rpasswd")
    contact_no = request.POST.get("contact")
    pass


def logout(request):
    auth.logout(request)
    return render(request, 'homepage.html')
