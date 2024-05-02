from django.contrib import admin
from .models import Professor, Project, Student

admin.site.register(Professor)
admin.site.register(Project)
admin.site.register(Student)