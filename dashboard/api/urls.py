from django.urls import path
from . import views

urlpatterns = [
    path('addorg/', views.add_organization, name="add_org_end_point"),
]