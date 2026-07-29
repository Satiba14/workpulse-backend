from .auth import LoginView, LogoutView
from .dashboard import DashboardStatsView
from .department import DepartmentListView, DepartmentDetailView
from .employee import EmployeeListView, EmployeeDetailView
from .attrition import (
    AttritionStatsView,
    AttritionAnalyticsView,
    AttritionRecordListView,
    ExitReasonListView,
    TopExitReasonsView,
)
from .exit_interview import (
    ExitInterviewListView,
    SendExitInterviewView,
    SubmitExitInterviewView,
)
from .concerns import ConcernListView, ConcernDetailView, ConcernResponseView, PublicConcernRespondView
from .audit import AuditLogListView
from .change_password import ChangePasswordView

__all__ = [
    'LoginView', 'LogoutView',
    'DashboardStatsView',
    'DepartmentListView', 'DepartmentDetailView',
    'EmployeeListView', 'EmployeeDetailView',
    'AttritionStatsView', 'AttritionAnalyticsView',
    'AttritionRecordListView',
    'ExitReasonListView', 'TopExitReasonsView',
    'ExitInterviewListView', 'SendExitInterviewView',
    'SubmitExitInterviewView',
    'ConcernListView', 'ConcernDetailView',
    'AuditLogListView',
]