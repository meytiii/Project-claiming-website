from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import AvailableProjectsListView, ClaimProjectView, ApproveClaimRequestView, ProfessorDashboardView

urlpatterns = [
    path('api/professors/', views.ProfessorListView.as_view(), name='api-professors-list'),
    path('api/projects/', views.ProjectListView.as_view(), name='api-projects-list'),
    path('api/claim-project/<int:project_id>/', ClaimProjectView.as_view(), name='api-claim-project'),
    path('api/approve-claim/', ApproveClaimRequestView.as_view(), name='api-approve-claim'),
    path('api/professor-dashboard/', ProfessorDashboardView.as_view(), name='api-professor-dashboard'),
    path('api/student-dashboard/', views.StudentDashboardView.as_view(), name='api-student-dashboard'),
    path('api/login/', views.UserLoginView.as_view(), name='api-user-login'),
    path('api/logout/', views.UserLogoutView.as_view(), name='api-user-logout'),
    path('api/available-projects/', AvailableProjectsListView.as_view(), name='api-available-projects'),
    path('api/project-search/', views.ProjectSearchView.as_view(), name='api-project-search'),
    path('api/create-project/', views.CreateProjectView.as_view(), name='api-create-project'),
]
