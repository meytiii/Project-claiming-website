from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import AvailableProjectsListView, ClaimProjectView, ApproveClaimRequestView, ProfessorDashboardView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/professors/', views.ProfessorListView.as_view(), name='api-professors-list'),
    path('api/projects/', views.ProjectListView.as_view(), name='api-projects-list'),
    path('api/claim-project/<int:project_id>/', ClaimProjectView.as_view(), name='api-claim-project'),
    path('api/approve-claim/', ApproveClaimRequestView.as_view(), name='api-approve-claim'),
    path('api/professor-dashboard/', ProfessorDashboardView.as_view(), name='api-professor-dashboard'),
    path('api/register/', views.UserRegistrationView.as_view(), name='api-user-register'),
    path('api/login/', views.UserLoginView.as_view(), name='api-user-login'),
    path('api/logout/', views.UserLogoutView.as_view(), name='api-user-logout'),
    path('api/available-projects/', AvailableProjectsListView.as_view(), name='api-available-projects'),
    path('api/project-search/', views.ProjectSearchView.as_view(), name='api-project-search'),
]
