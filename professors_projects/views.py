from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Professor, Project, Student
from .serializers import ProfessorSerializer, ProjectSerializer, StudentSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

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
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(request.user, 'student'):
            return Response({'message': 'Only students can claim projects'}, status=status.HTTP_403_FORBIDDEN)

        if project.is_available:
            student = request.user.student
            project.claimed_by.add(student)
            project.is_available = False
            project.claimed_at = datetime.now()
            project.save()
            return Response({'message': 'Project claimed successfully'}, status=status.HTTP_200_OK)
        return Response({'message': 'Project already claimed'}, status=status.HTTP_400_BAD_REQUEST)

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
            user_serializer = StudentSerializer(user.student)
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