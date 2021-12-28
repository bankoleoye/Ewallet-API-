from django.urls import path
from .views import register, login_user, dashboard 


app_name = "accounts"

urlpatterns = [
    path('register/', register, name="register"),
    path('login/', login_user, name="login"),
    path('', dashboard, name="dashboard"),
]
