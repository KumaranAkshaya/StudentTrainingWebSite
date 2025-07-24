from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        else:
            return render(request, 'student_app/register.html', {'errors': serializer.errors, 'data': request.POST})
    return render(request, 'student_app/register.html')

def login_view(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect('dashboard')
        else:
            return render(request, 'student_app/login.html', {'errors': serializer.errors, 'data': request.POST})
    return render(request, 'student_app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out.")
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'student_app/dashboard.html')
