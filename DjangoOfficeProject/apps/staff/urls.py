from django.urls import path
from .views import DepartmentListAPIView, OfficeUserListAPIView, StaffAPIView, ActivateEmailAPIView, EditStaffAPIView, \
    StaffDownloadAPIView

urlpatterns = [
    path('department/', DepartmentListAPIView.as_view(), name='department'),
    path('user/', OfficeUserListAPIView.as_view(), name='user'),
    path('staff/', StaffAPIView.as_view(), name='staff'),
    path('staff/activate/', ActivateEmailAPIView.as_view(), name='activate_email'),
    path('staff/edit/<str:uuid>/', EditStaffAPIView.as_view(), name='edit_staff'),
    path('download/', StaffDownloadAPIView.as_view(), name='download_staff'),
]

