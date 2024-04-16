from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from users.forms import RegisterUserForm, UserProfile
from .models import SocialHubUser
# Create your views here.

def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Redirect to a success page
            login(request, user)
            return redirect('home')
        else:
            # Return to login page
            messages.success(request, ("There was an error logging in!"))
            return redirect('login')

    else:
        return render(request, 'authenticate/login.html', {})
    
def logout_user(request):
    logout(request)
    messages.success(request, ("You are logged out!"))
    return redirect('home')

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Registration Successful!"))
            return redirect('home')
    else:
        form = RegisterUserForm()
    
    return render(request,'authenticate/register_user.html', {'form': form})

def view_profile(request):
    user = request.user
    form = UserProfile(request.POST or None, instance = user)

    if form.is_valid():
        form.save()
        return redirect('home')

    return render(request, 'profile.html', {'user': user, 'form': form})