from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import auth
import pyrebase


firebaseConfig = {
    'apiKey': "AIzaSyCuwsWy5bvz7c0Yv15M4GO9I42We4ZeSBk",
    'authDomain': "smartcounter-7195c.firebaseapp.com",
    'databaseURL': "https://smartcounter-7195c.firebaseio.com",
    'projectId': "smartcounter-7195c",
    'storageBucket': "smartcounter-7195c.appspot.com",
    'messagingSenderId': "241009535777",
    'appId': "1:241009535777:web:b9eaf5a4c10f84a7e6ec60",
    'measurementId': "G-JD5WVQ3GC8"
}
firebase = pyrebase.initialize_app(firebaseConfig)
authen = firebase.auth()

def homepage(request):
    return render(request, 'homepage.html', {})

def authenticate(request):
    email = request.POST.get('email')
    passwd = request.POST.get('passwd')
    try:
        user = authen.sign_in_with_email_and_password(email, passwd)
    except:
        txt = "Invalid Credentials"
        return render(request, 'homepage.html', {'message': txt})
    return redirect('/dashboard/')

def signup(request):
    return render(request, 'signup.html', {})

def postsignup(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    passwd = request.POST.get("passwd")
    rpasswd = request.POST.get("rpasswd")
    if passwd!=rpasswd:
        return render(request, 'signup.html', {'message':"PASSWORD DO NOT MATCH"})
    else:
        try:
            user = authen.create_user_with_email_and_password(email, passwd)
        except:
            return render(request, 'signup.html', {'message':"USER ALREADY EXIST"})
        return redirect('/')

def logout(request):
    auth.logout(request)
    return render(request, 'homepage.html')
