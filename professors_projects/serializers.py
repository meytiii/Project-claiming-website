from rest_framework import serializers
from .models import Professor, Project, Student

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['id', 'user', 'first_name', 'last_name', 'professor_id', 'phone_number']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'professor', 'title', 'description', 'project_id', 'claimed_by', 'claimed_at']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'first_name', 'last_name', 'student_id', 'phone_number', 'year_attended']
