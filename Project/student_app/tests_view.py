import unittest
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user
from rest_framework.test import APIClient
from .models import Student, Course, TrainingSchedule, StudentOptInOut
from .forms import *
from .serializers import *

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.student = Student.objects.create(
            name='John Doe',
            phone='1234567890',
            email='john@example.com',
            address='123 Test St'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Description',
            duration='2 hours'
        )
        self.schedule = TrainingSchedule.objects.create(
            course=self.course,
            start_date='2025-08-01',
            end_date='2025-08-02',
            time='10:00',
            location='Room 101'
        )
        self.opt = StudentOptInOut.objects.create(
            student=self.student,
            schedule=self.schedule,
            opted_in=True
        )

    # Tests for MVT views
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/register.html')

    def test_register_view_post_success(self):
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_invalid(self):
        data = {
            'username': '',
            'password': 'short',
            'email': 'invalid'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/register.html')
        self.assertTrue('errors' in response.context)

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/login.html')

    def test_login_view_post_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard', kwargs={'tab': 'students'}))
        self.assertTrue(get_user(self.client).is_authenticated)

    def test_login_view_post_invalid(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/login.html')
        self.assertTrue('errors' in response.context)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_dashboard_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard', kwargs={'tab': 'students'}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=' + reverse('dashboard', kwargs={'tab': 'students'}))

    def test_dashboard_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard', kwargs={'tab': 'students'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_app/dashboard.html')
        self.assertEqual(response.context['active_tab'], 'students')

    def test_dashboard_view_invalid_tab(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard', kwargs={'tab': 'invalid'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_tab'], 'students')

    def test_dashboard_student_create(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'form_type': 'student',
            'name': 'Jane Doe',
            'phone': '0987654321',
            'email': 'jane@example.com',
            'address': '456 Test St'
        }
        response = self.client.post(reverse('dashboard', kwargs={'tab': 'students'}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Student.objects.filter(name='Jane Doe').exists())

    def test_dashboard_student_update(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'form_type': 'student',
            'id': self.student.id,
            'name': 'John Updated',
            'phone': '1234567890',
            'email': 'john@example.com',
            'address': '123 Test St'
        }
        response = self.client.post(reverse('dashboard', kwargs={'tab': 'students'}), data)
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, 'John Updated')

    def test_dashboard_student_delete(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard', kwargs={'tab': 'students'}) + f'?delete={self.student.id}&type=student')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Student.objects.filter(id=self.student.id).exists())

    # Similar tests for course, schedule, and opt forms
    def test_dashboard_course_create(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'form_type': 'course',
            'name': 'New Course',
            'description': 'New Description',
            'duration': '3 hours'
        }
        response = self.client.post(reverse('dashboard', kwargs={'tab': 'courses'}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(name='New Course').exists())

    def test_dashboard_schedule_create(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'form_type': 'schedule',
            'course': self.course.id,
            'start_date': '2025-09-01',
            'end_date': '2025-09-02',
            'time': '14:00',
            'location': 'Room 202'
        }
        response = self.client.post(reverse('dashboard', kwargs={'tab': 'schedules'}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TrainingSchedule.objects.filter(location='Room 202').exists())

    def test_dashboard_opt_create(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'form_type': 'opt',
            'student': self.student.id,
            'schedule': self.schedule.id,
            'opted_in': True
        }
        response = self.client.post(reverse('dashboard', kwargs={'tab': 'opts'}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StudentOptInOut.objects.filter(student=self.student, schedule=self.schedule).exists())

    # Tests for API views
    def test_register_api_success(self):
        data = {
            'username': 'apiuser',
            'password': 'apipass123',
            'email': 'api@example.com'
        }
        response = self.api_client.post(reverse('api_register'), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Registration successful')
        self.assertTrue(User.objects.filter(username='apiuser').exists())

    def test_register_api_invalid(self):
        data = {
            'username': '',
            'password': 'short',
            'email': 'invalid'
        }
        response = self.api_client.post(reverse('api_register'), data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('errors' not in response.data)  # Errors are in response.data directly

    def test_login_api_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.api_client.post(reverse('api_login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertEqual(response.data['username'], 'testuser')

    def test_login_api_invalid(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.api_client.post(reverse('api_login'), data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('errors' not in response.data)  # Errors are in response.data directly

if __name__ == '__main__':
    unittest.main()