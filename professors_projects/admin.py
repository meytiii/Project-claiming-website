from django.contrib import admin
from .models import Professor, Project, Student, ProjectClaim

admin.site.register(Professor)
admin.site.register(Project)
admin.site.register(Student)
admin.site.register(ProjectClaim)