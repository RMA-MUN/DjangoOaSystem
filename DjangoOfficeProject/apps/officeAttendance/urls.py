from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = "attendance"

router = DefaultRouter()
router.register(r'attendance', views.AbsentViewSet, basename='attendance')

urlpatterns = [
    path('attendance-type/', views.AttendanceTypeViewSet.as_view(), name='attendance-type'),
    path('attendance-responser/', views.AttendanceResponserViewSet.as_view(), name='attendance-responser'),
] + router.urls