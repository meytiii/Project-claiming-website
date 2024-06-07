from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import JsonResponse, FileResponse
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Professor, Project, Student, ProjectClaim
from .serializers import ProfessorSerializer, ProjectSerializer, StudentSerializer, ProjectClaimSerializer
from datetime import datetime
import logging

@method_decorator(csrf_exempt, name='dispatch')
class ProjectSearchView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        availability = self.request.query_params.get('availability')
        if availability:
            if availability == 'available':
                queryset = queryset.filter(is_available=True)
            elif availability == 'taken':
                queryset = queryset.filter(is_available=False)

        capacity = self.request.query_params.get('capacity')
        if capacity:
            queryset = queryset.filter(max_students=capacity)

        search_query = self.request.query_params.get('search_query')
        search_by = self.request.query_params.get('search_by')
        if search_query and search_by:
            if search_by == 'title':
                queryset = queryset.filter(title__icontains=search_query)
            elif search_by == 'professor':
                queryset = queryset.filter(professor__first_name__icontains=search_query) | \
                           queryset.filter(professor__last_name__icontains=search_query)

        return queryset

    
@method_decorator(csrf_exempt, name='dispatch')
class ProfessorListView(APIView):
    def get(self, request):
        professors = Professor.objects.all()
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)
    
@method_decorator(csrf_exempt, name='dispatch')
class ProjectListView(APIView):
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class ClaimProjectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request, project_id):
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        student_ids = request.data.get('student_ids', [])

        invalid_ids = []
        valid_students = []
        for suid in student_ids:
            try:
                student = Student.objects.get(suid=suid)
                valid_students.append(student)
            except Student.DoesNotExist:
                invalid_ids.append(suid)

        if invalid_ids:
            return Response({'message': f"One or more student IDs are invalid: {', '.join(invalid_ids)}"}, status=status.HTTP_400_BAD_REQUEST)

        if len(valid_students) > project.max_students:
            return Response({'message': f'You can only claim the project for up to {project.max_students} students'}, status=status.HTTP_400_BAD_REQUEST)

        if ProjectClaim.objects.filter(project=project, is_approved=True).exists():
            return Response({'message': 'This project is already approved for another student'}, status=status.HTTP_400_BAD_REQUEST)

        accepted_claims = ProjectClaim.objects.filter(students__in=valid_students, is_approved=True)
        if accepted_claims.exists():
            return Response({'message': 'One or more students already have an accepted project'}, status=status.HTTP_400_BAD_REQUEST)

        for student in valid_students:
            if ProjectClaim.objects.filter(project=project, students=student).exists():
                return Response({'message': f'Student {student.suid} has already claimed this project'}, status=status.HTTP_400_BAD_REQUEST)

        if project.claimed_by.count() + len(valid_students) > project.max_students:
            return Response({'message': 'Project already claimed by the maximum number of students'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            project_claim = ProjectClaim.objects.create(project=project)
            project_claim.students.add(*valid_students)

        return Response({'message': 'Claim request sent successfully'}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ApproveClaimRequestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'professor'):
            return Response({'message': 'Only professors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        project_id = request.data.get('project_id')
        student_id = request.data.get('student_id')
        status_value = request.data.get('status')

        if status_value is None:
            return Response({'message': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(project_id=project_id)
            student = Student.objects.get(suid=student_id)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Student.DoesNotExist:
            return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            claim = ProjectClaim.objects.get(project=project, students=student)
        except ProjectClaim.DoesNotExist:
            return Response({'message': 'Claim request not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != project.professor.user:
            return Response({'message': 'Only the professor can approve or delete this claim'}, status=status.HTTP_403_FORBIDDEN)

        if status_value == True:
            if claim.is_approved:
                return Response({'message': 'Claim request is already approved'}, status=status.HTTP_400_BAD_REQUEST)

            claim.is_approved = True
            claim.approved_at = timezone.now()
            claim.save()

            project.is_available = False
            project.claimed_at = timezone.now()
            project.save()

            for student in claim.students.all():
                project.claimed_by.add(student)

            students_in_claim = claim.students.all()

            for student in students_in_claim:
                ProjectClaim.objects.filter(students=student).exclude(id=claim.id).delete()

            return Response({'message': 'Claim request approved successfully'}, status=status.HTTP_200_OK)

        elif status_value == False:
            claim.delete()
            return Response({'message': 'Claim request deleted successfully'}, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)




@method_decorator(csrf_exempt, name='dispatch')
class ProfessorDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):
        if not hasattr(request.user, 'professor'):
            return Response({'message': 'Only professors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        professor = request.user.professor
        projects = Project.objects.filter(professor=professor)
        
        claims = ProjectClaim.objects.filter(project__in=projects)
        
        projects_data = []
        for project in projects:
            project_claims = claims.filter(project=project)
            project_data = {
                'project': ProjectSerializer(project).data,
                'claims': ProjectClaimSerializer(project_claims, many=True).data
            }
            projects_data.append(project_data)

        return Response(projects_data, status=status.HTTP_200_OK)
    
@method_decorator(csrf_exempt, name='dispatch')
class StudentDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        if not hasattr(request.user, 'student'):
            return Response({'message': 'Only students can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        student = request.user.student
        claims = ProjectClaim.objects.filter(students=student)
        serializer = ProjectClaimSerializer(claims, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if hasattr(user, 'student'):
                user_serializer = StudentSerializer(user.student)
                role = 'student'
            elif hasattr(user, 'professor'):
                user_serializer = ProfessorSerializer(user.professor)
                role = 'professor'
            else:
                return Response({'message': 'User role not found'}, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User logged in successfully',
                'token': str(refresh.access_token),
                'user': user_serializer.data,
                'role': role
            }, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class AvailableProjectsListView(generics.ListAPIView):
    queryset = Project.objects.filter(is_available=True)
    serializer_class = ProjectSerializer

@method_decorator(csrf_exempt, name='dispatch')
class CreateProjectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        professor = request.user.professor
        
        name = request.data.get('name')
        capacity = request.data.get('capacity')
        
        if not (name and capacity):
            return Response({'message': 'Name and capacity are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if capacity not in range(1, 5):
            return Response({'message': 'Capacity must be between 1 and 4'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Project.objects.filter(title=name).exists():
            return Response({'message': 'A project with this title already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        project = Project.objects.create(professor=professor, title=name, max_students=capacity)
        serializer = ProjectSerializer(project)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
@method_decorator(csrf_exempt, name='dispatch')
class UploadFileView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, project_id):
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            student_id = request.user.student.suid
        except AttributeError:
            return Response({'message': 'Only students can upload files'}, status=status.HTTP_403_FORBIDDEN)

        try:
            claim = ProjectClaim.objects.get(project=project, students__suid=student_id)
        except ProjectClaim.DoesNotExist:
            return Response({'message': 'You have not claimed this project'}, status=status.HTTP_400_BAD_REQUEST)

        if not claim.is_approved:
            return Response({'message': 'Your claim for this project has not been approved'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES.get('file')
        if not file:
            return Response({'message': 'File not found in request'}, status=status.HTTP_400_BAD_REQUEST)

        project.project_file = file
        project.file_upload_date = timezone.now()
        project.save()

        return Response({'message': 'File uploaded successfully'}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class DownloadProjectFile(APIView):
    def get(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)
        project_file = project.project_file
        if project_file:
            response = FileResponse(project_file.open('rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{project_file.name}"'
            return response
        else:
            return Response({'message': 'File not found for this project'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class StudentCancelClaimView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def delete(self, request, project_id):
        try:
            student = request.user.student
        except AttributeError:
            return Response({'message': 'Only students can cancel a claim'}, status=status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            claim = ProjectClaim.objects.get(project=project, students=student)
        except ProjectClaim.DoesNotExist:
            return Response({'message': 'Claim request not found'}, status=status.HTTP_404_NOT_FOUND)

        if claim.is_approved:
            return Response({'message': 'Cannot cancel an approved claim'}, status=status.HTTP_400_BAD_REQUEST)

        claim.delete()

        return Response({'message': 'Claim request canceled successfully'}, status=status.HTTP_200_OK)
    
@method_decorator(csrf_exempt, name='dispatch')
class ProfessorCancelClaimView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def delete(self, request, project_id, student_id):
        try:
            professor = request.user.professor
        except AttributeError:
            return Response({'message': 'Only professors can cancel a claim'}, status=status.HTTP_403_FORBIDDEN)

        try:
            project = Project.objects.get(project_id=project_id, professor=professor)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            claim = ProjectClaim.objects.get(project=project, students__suid=student_id)
        except ProjectClaim.DoesNotExist:
            return Response({'message': 'Claim request not found'}, status=status.HTTP_404_NOT_FOUND)

        if claim.is_approved:
            return Response({'message': 'Cannot cancel an approved claim'}, status=status.HTTP_400_BAD_REQUEST)

        claim.delete()

        return Response({'message': 'Claim request canceled successfully'}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class CompletedProjectsView(APIView):
    def get(self, request):
        completed_projects = Project.objects.filter(is_available=False).exclude(project_file='')
        serializer = ProjectSerializer(completed_projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)