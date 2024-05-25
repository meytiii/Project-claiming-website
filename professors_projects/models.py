from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max

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
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    project_id = models.CharField(max_length=4, unique=True, default='1000')  # Temporary default
    max_students = models.PositiveIntegerField(default=4)
    is_available = models.BooleanField(default=True)
    claimed_by = models.ManyToManyField(Student, through='ProjectClaim')
    claimed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.project_id or self.project_id == '1000':  # Check if the project_id is not set or default
            last_project_id = Project.objects.aggregate(Max('project_id'))['project_id__max']
            if last_project_id:
                new_project_id = int(last_project_id) + 1
                if new_project_id > 9999:
                    new_project_id = 1000  # Reset to 1000 if it exceeds 9999
                self.project_id = str(new_project_id)
            else:
                self.project_id = '1000'
        super().save(*args, **kwargs)

    def update_availability(self):
        if self.claimed_by.count() >= self.max_students:
            self.is_available = False
        else:
            self.is_available = True
        self.save()

class ProjectClaim(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} : {self.project.title}"
