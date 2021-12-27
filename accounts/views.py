from django.shortcuts import render, redirect

from .forms import UserRegistrationForm


# Create your views here.

def register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new_user = form.save()
            return redirect('accounts:register')
    return render(request, "accounts/register.html", context = {"form":form})

