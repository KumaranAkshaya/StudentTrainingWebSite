from django.contrib import admin
from .models import *

admin.site.register(Course)
admin.site.register(StudentOptInOut)
admin.site.register(Student)
admin.site.register(TrainingSchedule)