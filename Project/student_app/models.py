from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class TrainingSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.course.name} ({self.start_date} to {self.end_date})"

class StudentOptInOut(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    schedule = models.ForeignKey(TrainingSchedule, on_delete=models.CASCADE)
    opted_in = models.BooleanField(default=False)
    opted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'schedule')

    def __str__(self):
        status = "Opted In" if self.opted_in else "Opted Out"
        return f"{self.student.name} - {self.schedule} [{status}]"
