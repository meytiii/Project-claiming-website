from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Professor, Project, Student
from .serializers import ProfessorSerializer, ProjectSerializer, StudentSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, authenticate the user after registration
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
            return redirect('home')  # Replace 'home' with your desired URL name
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            # Serialize user data
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.student.first_name if hasattr(user, 'student') else user.professor.first_name,
                'last_name': user.student.last_name if hasattr(user, 'student') else user.professor.last_name,
                'student_id': user.student.student_id if hasattr(user, 'student') else None,
                'professor_id': user.professor.professor_id if hasattr(user, 'professor') else None,
                'token': token
            }
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

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
        project = Project.objects.get(id=project_id)
        # Check if project is available for claiming
        if project.is_available:
            student = request.user.student
            project.claimed_by = student
            project.is_available = False
            project.save()
            return Response({'message': 'Project claimed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Project already claimed'}, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(username=serializer.validated_data['username'],
                                            email=serializer.validated_data['email'],
                                            password=serializer.validated_data['password'])
            # Generate a token for the newly registered user
            refresh = RefreshToken.for_user(user)

            # You can optionally log in the user after registration
            login(request, user)
            
            # Return a response with the token and other relevant data
            return Response({'message': 'User registered successfully',
                             'token': str(refresh.access_token)}, 
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Serialize the user object to include all fields
            user_serializer = StudentSerializer(user.student)
            
            # Generate a token for the logged-in user
            refresh = RefreshToken.for_user(user)

            # Return a response with the token and other relevant data
            return Response({'message': 'User logged in successfully',
                             'token': str(refresh.access_token),
                             'user': user_serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)