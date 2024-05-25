from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Professor, Project, Student, ProjectClaim
from .serializers import ProfessorSerializer, ProjectSerializer, StudentSerializer, ProjectClaimSerializer
from datetime import datetime
import logging

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
            queryset = queryset.filter(max_students__gte=capacity)

        search_query = self.request.query_params.get('search_query')
        search_by = self.request.query_params.get('search_by')
        if search_query and search_by:
            if search_by == 'title':
                queryset = queryset.filter(title__icontains=search_query)
            elif search_by == 'professor':
                queryset = queryset.filter(professor__user__username__icontains=search_query)

        return queryset

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

class ProfessorListView(APIView):
    def get(self, request):
        professors = Professor.objects.all()
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)

class ProjectListView(APIView):
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

class ClaimProjectView(APIView):
    def post(self, request, project_id):
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        student_ids = request.data.get('student_ids', [])

        invalid_ids = []
        valid_students = []
        for student_id in student_ids:
            try:
                student = Student.objects.get(student_id=student_id)
                valid_students.append(student)
            except Student.DoesNotExist:
                invalid_ids.append(student_id)

        if invalid_ids:
            return Response({'message': f"One or more student IDs are invalid: {', '.join(invalid_ids)}"}, status=status.HTTP_400_BAD_REQUEST)

        if len(valid_students) > project.max_students:
            return Response({'message': f'You can only claim the project for up to {project.max_students} students'}, status=status.HTTP_400_BAD_REQUEST)

        if ProjectClaim.objects.filter(project=project, is_approved=True).exists():
            return Response({'message': 'This project is already approved for another student'}, status=status.HTTP_400_BAD_REQUEST)

        accepted_claims = ProjectClaim.objects.filter(students__in=valid_students, is_approved=True)
        if accepted_claims.exists():
            return Response({'message': 'One or more students already have an accepted project'}, status=status.HTTP_400_BAD_REQUEST)

        if project.claimed_by.count() + len(valid_students) > project.max_students:
            return Response({'message': 'Project already claimed by the maximum number of students'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            project_claim = ProjectClaim.objects.create(project=project)
            project_claim.students.add(*valid_students)

        return Response({'message': 'Claim request sent successfully'}, status=status.HTTP_200_OK)

class ApproveClaimRequestView(APIView):
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')
        student_id = request.data.get('student_id')

        try:
            project = Project.objects.get(project_id=project_id)
            student = Student.objects.get(student_id=student_id)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Student.DoesNotExist:
            return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            claim = ProjectClaim.objects.get(project=project, students=student)
        except ProjectClaim.DoesNotExist:
            return Response({'message': 'Claim request not found'}, status=status.HTTP_404_NOT_FOUND)

        if claim.is_approved:
            return Response({'message': 'Claim request is already approved'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user != project.professor.user:
            return Response({'message': 'Only the professor can approve this claim'}, status=status.HTTP_403_FORBIDDEN)

        claim.is_approved = True
        claim.approved_at = timezone.now()
        claim.save()
        project.update_availability()

        return Response({'message': 'Claim request approved successfully'}, status=status.HTTP_200_OK)


class ProfessorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'professor'):
            return Response({'message': 'Only professors can access this dashboard'}, status=status.HTTP_403_FORBIDDEN)

        professor = request.user.professor
        claims = ProjectClaim.objects.filter(project__professor=professor, is_approved=False)
        serializer = ProjectClaimSerializer(claims, many=True)
        return Response(serializer.data)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data['user']
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            student = Student.objects.create(
                user=user,
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                student_id=serializer.validated_data['student_id'],
                phone_number=serializer.validated_data['phone_number'],
                year_attended=serializer.validated_data['year_attended']
            )
            refresh = RefreshToken.for_user(user)
            login(request, user)
            return Response({
                'message': 'User registered successfully',
                'token': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if hasattr(user, 'student'):
                user_serializer = StudentSerializer(user.student)
            else:
                user_serializer = ProfessorSerializer(user.professor)
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User logged in successfully',
                'token': str(refresh.access_token),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)

class AvailableProjectsListView(generics.ListAPIView):
    queryset = Project.objects.filter(is_available=True)
    serializer_class = ProjectSerializer
