from django.contrib.auth import views
from django.urls import path
from .views import Login, Register



urlspattern = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    # path('logout/', Logout.as_view()),

]