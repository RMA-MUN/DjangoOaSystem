from django.urls import path
from .views import LoginView, ResetPasswordView, TokenRefreshView, UserDetailView, UpdateDepartmentLeaderAPIView

app_name = 'officeAuth'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh-token'),
    path('user/detail/', UserDetailView.as_view(), name='user-detail'),
    path('department/update-leader/', UpdateDepartmentLeaderAPIView.as_view(), name='update_department_leader'),
]