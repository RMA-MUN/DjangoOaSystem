from django.urls import path
from .views import LatestInformView, LatestAttendanceView, DepartmentStaffCountView

app_name = 'home'

urlpatterns = []

urlpatterns += [
    path('latest/inform/', LatestInformView.as_view(), name='latest-inform'),
    path('latest/attendance/', LatestAttendanceView.as_view(), name='latest-attendance'),
    path('department/staff/count/', DepartmentStaffCountView.as_view(), name='department-staff-count'),
]
