# student_app/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Course
from .forms import CourseForm

# MVT views
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

# API views
@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({'message': 'Login successful', 'username': user.username}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def course_list(request):
    # Handle Create or Update
    if request.method == 'POST':
        course_id = request.GET.get('id')
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            form = CourseForm(request.POST, instance=course)
        else:
            form = CourseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('course_list')

    # Handle Delete
    if request.method == 'GET' and 'delete' in request.GET:
        course = get_object_or_404(Course, id=request.GET.get('delete'))
        course.delete()
        return redirect('course_list')

    courses = Course.objects.all()
    form = CourseForm()
    edit_id = request.GET.get('id')
    edit_course = Course.objects.filter(id=edit_id).first() if edit_id else None
    edit_form = CourseForm(instance=edit_course) if edit_course else None

    return render(request, 'student_app/course_list.html', {
        'courses': courses,
        'form': form,
        'edit_course': edit_course,
        'edit_form': edit_form,
    })
