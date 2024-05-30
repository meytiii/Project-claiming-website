from django.contrib import admin
from .models import Professor, Project, Student, ProjectClaim
from django.db.models import Q

admin.site.register(Professor)
admin.site.register(Student)
admin.site.register(ProjectClaim)

@admin.action(description='Clear claimed_by for selected projects')
def clear_claimed_by(modeladmin, request, queryset):
    for project in queryset:
        project.claimed_by.clear()

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'professor', 'is_available']
    actions = [clear_claimed_by]

admin.site.register(Project, ProjectAdmin)