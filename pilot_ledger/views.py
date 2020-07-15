from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import auth
import pyrebase
from firebase_utils import app

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
firebase = pyrebase.initialize_app(firebaseConfig)
authen = firebase.auth()
db = firebase.database()


def homepage(request):
    return render(request, 'homepage.html', {})


def authenticate(request):
    email = request.POST.get('email')
    passwd = request.POST.get('passwd')
    app.signin_using_email_pass(email, passwd)


"""
    try:
        user = authen.sign_in_with_email_and_password(email, passwd)
    except:
        txt = "Invalid Credentials"
        return render(request, 'homepage.html', {'message': txt})
    sessions_id = user['idToken']
    request.session['uid'] = str(sessions_id)
    return redirect('/dashboard/')
"""

def signup(request):
    return render(request, 'signup.html', {})


def postsignup(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    passwd = request.POST.get("passwd")
    rpasswd = request.POST.get("rpasswd")
    contact_no = request.POST.get("contact")
    if passwd != rpasswd:
        return render(request, 'signup.html', {'message': "PASSWORD DO NOT MATCH"})
    else:
        try:
            user = authen.create_user_with_email_and_password(email, passwd)
        except:
            return render(request, 'signup.html', {'message': "USER ALREADY EXIST"})
            # makeit return redirect(signup)
        uid = user['localId']
        data = {'name': name, 'email': email, 'password': passwd}
        db.child("users").child(uid).set(data)
        return redirect('/')


def logout(request):
    auth.logout(request)
    return render(request, 'homepage.html')
