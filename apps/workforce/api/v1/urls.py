from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.workforce.api.v1 import views
from apps.workforce.api.v1.views.manager import (
    ManagerListView,
    DepartmentManagerView,
)
from apps.workforce.api.v1.views.notification import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationUnreadCountView,
)
from apps.workforce.api.v1.views.employee_letter import EmployeeLetterDataView
from apps.workforce.api.v1.views.profile import ProfileView
from apps.workforce.api.v1.views.document import EmployeeDocumentUploadView
from apps.workforce.api.v1.views.change_password import ChangePasswordView
from apps.workforce.api.v1.views.generated_letter import GeneratedLetterCreateView

urlpatterns = [
    # Auth
    path('auth/login/',          views.LoginView.as_view()),
    path('auth/logout/',         views.LogoutView.as_view()),
    path('auth/login/refresh/',  TokenRefreshView.as_view()),

    # Dashboard
    path('dashboard/',           views.DashboardStatsView.as_view()),

    # Departments
    path('departments/',         views.DepartmentListView.as_view()),
    path('departments/<str:pk>/', views.DepartmentDetailView.as_view()),

    # Employees
    path('employees/',           views.EmployeeListView.as_view()),
    path('employees/<str:pk>/',  views.EmployeeDetailView.as_view()),
    path('employees/<str:emp_pk>/exit-interview/send/',
         views.SendExitInterviewView.as_view()),

    # document
    path('employees/<uuid:pk>/documents/', EmployeeDocumentUploadView.as_view()),
    path('employees/<uuid:pk>/documents/<uuid:doc_id>/', EmployeeDocumentUploadView.as_view()),

    # Attrition
    path('attrition/',           views.AttritionRecordListView.as_view()),
    path('attrition/stats/',     views.AttritionStatsView.as_view()),
    path('attrition/analytics/', views.AttritionAnalyticsView.as_view()),

    # Exit Reasons
    path('exit-reasons/',        views.ExitReasonListView.as_view()),
    path('exit-reasons/top/',    views.TopExitReasonsView.as_view()),

    # Exit Interview
    path('exit-interviews/',     views.ExitInterviewListView.as_view()),
    path('exit-interview/<str:emp_id>/<uuid:token>/',
         views.SubmitExitInterviewView.as_view()),

    # Concerns
    path('concerns/',            views.ConcernListView.as_view()),
    path('concerns/<str:pk>/',   views.ConcernDetailView.as_view()),
    path('concerns/<str:pk>/response/', views.ConcernResponseView.as_view()),
    path('respond/<uuid:token>/',        views.PublicConcernRespondView.as_view()),

    # Audit
    path('audit-logs/',          views.AuditLogListView.as_view()),

    path(
    'managers/',
    ManagerListView.as_view(),
    name='manager-list'
),

    path(
        'departments/<uuid:dept_pk>/manager/',
        DepartmentManagerView.as_view(),
        name='department-manager'
    ),
    # notification
    path('notifications/',              NotificationListView.as_view()),
    path('notifications/mark-read/',    NotificationMarkReadView.as_view()),
    path('notifications/mark-read/<uuid:pk>/', NotificationMarkReadView.as_view()),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view()),

    # Letter
    path('employees/<uuid:pk>/letter-data/', EmployeeLetterDataView.as_view()),
    
    # Profile
    path(
    'profile/',
    ProfileView.as_view(),
    name='profile'
),
# change password
path(
    'profile/change-password/',
    ChangePasswordView.as_view(),
    name='change-password'
),
# generated letter
path('employees/<uuid:pk>/generated-letters/', GeneratedLetterCreateView.as_view()),
]