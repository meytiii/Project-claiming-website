from django.db import models
from django.contrib.auth.models import User

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    professor_id = models.CharField(max_length=10, unique=True, default='0000000000')
    phone_number = models.CharField(max_length=15, default='')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    student_id = models.CharField(max_length=10, unique=True, default='0000000000')
    phone_number = models.CharField(max_length=15, default='')
    year_attended = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Project(models.Model):
    id = models.IntegerField(primary_key=True)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    claimed_by = models.ForeignKey(Student, on_delete=models.SET_NULL, blank=True, null=True)
    claimed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title