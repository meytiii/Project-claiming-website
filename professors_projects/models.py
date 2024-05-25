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
        return f"{self.first_name} {self.last_name} {self.student_id}"

class Project(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    project_id = models.CharField(max_length=4, unique=True)  # Removed default, handle it manually in save method
    max_students = models.PositiveIntegerField(default=4)
    is_available = models.BooleanField(default=True)
    claimed_by = models.ManyToManyField(Student, through='ProjectClaimRelation')
    claimed_at = models.DateTimeField(null=True, blank=True)
    project_file = models.FileField(upload_to='project_files/', null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.project_id:
            last_project_id = Project.objects.aggregate(Max('project_id'))['project_id__max']
            if last_project_id:
                new_project_id = int(last_project_id) + 1
                if new_project_id > 9999:
                    new_project_id = 1000
                self.project_id = str(new_project_id)
            else:
                self.project_id = '1000'
        super().save(*args, **kwargs)

    def update_availability(self):
        self.is_available = self.claimed_by.count() < self.max_students
        self.save()

class ProjectClaim(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        students_str = ', '.join([student.student_id for student in self.students.all()])
        return f"Students: {students_str} - Project: {self.project.title}"

class ProjectClaimRelation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('project', 'student')