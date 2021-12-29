from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, CustomAuthForm
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import  login_required


# Create your views here.

def register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new_user = form.save()
            return redirect('accounts:register')
    return render(request, "accounts/register.html", context={"form":form})

def login_user(request):
    form = CustomAuthForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, email = cd['email'], password=cd['password']) 
            if user is not None:
                login(request, user)
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Account does not exist')
    return render(request, "accounts/login.html", context = {"form":form})

@login_required
def dashboard(request):
    return render(request, "dashboard.html", context={})
