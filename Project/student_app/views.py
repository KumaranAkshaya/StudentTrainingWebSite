from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import *
from .forms import *

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
            return redirect('dashboard', tab='students')
        else:
            return render(request, 'student_app/login.html', {'errors': serializer.errors, 'data': request.POST})
    return render(request, 'student_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request, tab='students'):
    # Validate tab parameter
    if tab not in ['students', 'courses', 'schedules', 'opts']:
        tab = 'students'

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'student':
            student_id = request.POST.get('id')
            if student_id:
                student = get_object_or_404(Student, id=student_id)
                form = StudentForm(request.POST, instance=student)
            else:
                form = StudentForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Student saved successfully.")
                return redirect('dashboard', tab='students')

        elif form_type == 'course':
            course_id = request.POST.get('id')
            if course_id:
                course = get_object_or_404(Course, id=course_id)
                form = CourseForm(request.POST, instance=course)
            else:
                form = CourseForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Course saved successfully.")
                return redirect('dashboard', tab='courses')

        elif form_type == 'schedule':
            schedule_id = request.POST.get('id')
            if schedule_id:
                schedule = get_object_or_404(TrainingSchedule, id=schedule_id)
                form = TrainingScheduleForm(request.POST, instance=schedule)
            else:
                form = TrainingScheduleForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Schedule saved successfully.")
                return redirect('dashboard', tab='schedules')

        elif form_type == 'opt':
            record_id = request.POST.get('id')
            if record_id:
                instance = get_object_or_404(StudentOptInOut, id=record_id)
                form = StudentOptInOutForm(request.POST, instance=instance)
            else:
                form = StudentOptInOutForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Opt record saved successfully.")
                return redirect('dashboard', tab='opts')

    # Handle delete requests
    if request.method == 'GET' and 'delete' in request.GET:
        delete_type = request.GET.get('type')
        if delete_type == 'student':
            student = get_object_or_404(Student, id=request.GET.get('delete'))
            student.delete()
            messages.success(request, "Student deleted successfully.")
            return redirect('dashboard', tab='students')
        elif delete_type == 'course':
            course = get_object_or_404(Course, id=request.GET.get('delete'))
            course.delete()
            messages.success(request, "Course deleted successfully.")
            return redirect('dashboard', tab='courses')
        elif delete_type == 'schedule':
            schedule = get_object_or_404(TrainingSchedule, id=request.GET.get('delete'))
            schedule.delete()
            messages.success(request, "Schedule deleted successfully.")
            return redirect('dashboard', tab='schedules')
        elif delete_type == 'opt':
            record = get_object_or_404(StudentOptInOut, id=request.GET.get('delete'))
            record.delete()
            messages.success(request, "Opt record deleted successfully.")
            return redirect('dashboard', tab='opts')

    # Fetch data for all tabs
    students = Student.objects.all()
    courses = Course.objects.all()
    schedules = TrainingSchedule.objects.all()
    opts = StudentOptInOut.objects.select_related('student', 'schedule').all()

    # Initialize forms
    student_form = StudentForm()
    course_form = CourseForm()
    schedule_form = TrainingScheduleForm()
    opt_form = StudentOptInOutForm()

    # Handle edit forms
    edit_id = request.GET.get('id')
    edit_student = Student.objects.filter(id=edit_id).first() if edit_id and request.GET.get('type') == 'student' else None
    edit_course = Course.objects.filter(id=edit_id).first() if edit_id and request.GET.get('type') == 'course' else None
    edit_schedule = TrainingSchedule.objects.filter(id=edit_id).first() if edit_id and request.GET.get('type') == 'schedule' else None
    edit_opt = StudentOptInOut.objects.filter(id=edit_id).first() if edit_id and request.GET.get('type') == 'opt' else None

    edit_student_form = StudentForm(instance=edit_student) if edit_student else None
    edit_course_form = CourseForm(instance=edit_course) if edit_course else None
    edit_schedule_form = TrainingScheduleForm(instance=edit_schedule) if edit_schedule else None
    edit_opt_form = StudentOptInOutForm(instance=edit_opt) if edit_opt else None

    return render(request, 'student_app/dashboard.html', {
        'active_tab': tab,
        'students': students,
        'courses': courses,
        'schedules': schedules,
        'records': opts,
        'student_form': student_form,
        'course_form': course_form,
        'schedule_form': schedule_form,
        'opt_form': opt_form,
        'edit_student': edit_student,
        'edit_course': edit_course,
        'edit_schedule': edit_schedule,
        'edit_opt': edit_opt,
        'edit_student_form': edit_student_form,
        'edit_course_form': edit_course_form,
        'edit_schedule_form': edit_schedule_form,
        'edit_opt_form': edit_opt_form,
    })

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