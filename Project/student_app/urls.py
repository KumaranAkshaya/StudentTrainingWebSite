# student_app/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    # MVT Views
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),

    # API Views
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),

    path('course/', course_list, name='course_list'),
]
