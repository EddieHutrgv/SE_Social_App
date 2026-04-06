from django.urls import path
from testApp import views

urlpatterns = [
    path('', views.home, name='home'),
]