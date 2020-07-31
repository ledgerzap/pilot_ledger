from django.shortcuts import render
from django.http import HttpResponse
import firebase_utils


# Create your views here.


def createorg(request):
    return render(request, 'createorg.html', {})


class DashDisplay(object):
    def __init__(self):
        self.app = firebase_utils.FirebaseSDK()
        self.db_dealer = firebase_utils.Deals()

    def dashboard(self, request, user_uid):
        user_ref = self.app.fetch_firestore('user', user_uid)
        user_dict = user_ref.get().to_dict()
        # user_dict : {
        #             'name': name,
        #             'email': email,
        #             'password': password,
        #             'contact': contact,
        #             'organizations': []
        #         }
        return render(request, 'dashboard.html', user_dict)

    def displayorgs(self, request):
        pass

    def postcreateorg(self, request):
        name = request.POST.get('name')
        details = {'name': name, 'user': 'mud'}
        self.app.add_to_firestore(details, 'organizations')
        return HttpResponse("org created")


def dashboard(request):
    return HttpResponse("hi")
