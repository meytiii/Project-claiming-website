from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Front-end views for user registration, login, logout
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # API URLs for managing professors, projects, and user authentication
    path('api/professors/', views.ProfessorListView.as_view(), name='api-professors-list'),
    path('api/projects/', views.ProjectListView.as_view(), name='api-projects-list'),
    path('api/claim-project/<int:project_id>/', views.ClaimProjectView.as_view(), name='api-claim-project'),
    path('api/register/', views.UserRegistrationView.as_view(), name='api-user-register'),
    path('api/login/', views.UserLoginView.as_view(), name='api-user-login'),
    path('api/logout/', views.UserLogoutView.as_view(), name='api-user-logout'),

    # Add other URLs as needed
]