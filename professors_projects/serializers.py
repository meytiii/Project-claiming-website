from rest_framework import serializers
from .models import Professor, Project, Student
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfessorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Professor
        fields = ['id', 'user', 'first_name', 'last_name', 'professor_id', 'phone_number']

class ProjectSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source='professor.user.username', read_only=True)
    claimed_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'professor_name', 'title', 'description', 'project_id', 'is_available', 'claimed_by', 'claimed_at']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'first_name', 'last_name', 'student_id', 'phone_number', 'year_attended']