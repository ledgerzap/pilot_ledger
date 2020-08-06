from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard),
    path('createorg/', views.create_org),
    path('createorg/post_create_org/', views.post_create_org),
]
