from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='register'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/<str:tab>/', dashboard, name='dashboard'),  
    path('dashboard/', dashboard, name='dashboard'), 
    # API Views
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
]