from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Professor, Project, Student, ProjectClaim

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfessorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Professor
        fields = ['id', 'user', 'first_name', 'last_name', 'suid', 'phone_number']

class ProjectSerializer(serializers.ModelSerializer):
    professor_name = serializers.SerializerMethodField()
    claimed_by = serializers.SerializerMethodField()
    file_upload_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Project
        fields = ['id', 'professor_name', 'title', 'description', 'project_id', 'is_available', 'claimed_by', 'claimed_at', 'project_file', 'file_upload_date', 'max_students']

    def get_professor_name(self, obj):
        return f"{obj.professor.first_name} {obj.professor.last_name}"

    def get_claimed_by(self, obj):
        claimed_by_data = []
        for student in obj.claimed_by.all():
            student_data = {
                'id': student.suid,
                'name': student.get_full_name(),
            }
            claimed_by_data.append(student_data)
        return claimed_by_data

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'first_name', 'last_name', 'suid', 'phone_number', 'year_attended']

class ProjectClaimSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()
    project = ProjectSerializer()  # Nest the ProjectSerializer

    def get_students(self, obj):
        students_data = []
        for student in obj.students.all():
            student_data = {
                'id': student.suid,
                'name': student.get_full_name(),
            }
            students_data.append(student_data)
        return students_data

    class Meta:
        model = ProjectClaim
        fields = '__all__'