from rest_framework.response import Response
from rest_framework.views import APIView
from apps.inform.models import Inform
from django.db.models import Q, Count
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from apps.inform.serializers import InformSerializer
from apps.officeAuth.models import OfficeDepartment
from apps.officeAttendance.models import Attendance
from apps.officeAttendance.serializer import AttendanceSerializer


class LatestInformView(APIView):
    """
    用于返回最新的十条通知
    """
    # 缓存10分钟
    @method_decorator(cache_page(60 * 10))
    def get(self, request):
        # 返回和当前登录用户相关的通知
        informs = Inform.objects.prefetch_related('departments').filter(
            Q(public=True) |
            Q(departments=request.user.department) |
            Q(author=request.user)
        ).order_by('-create_time')[:10]

        # 序列化通知
        serializer = InformSerializer(informs, many=True)
        return Response(serializer.data)


class LatestAttendanceView(APIView):
    """
    用于返回最新的十条考勤记录
    """
    @method_decorator(cache_page(60 * 10))
    def get(self, request):
        # 返回和当前登录用户相关的考勤记录
        attendances = Attendance.objects.filter(
            Q(requester=request.user) |
            Q(responser=request.user)
        ).order_by('-create_time')[:10]

        # 序列化考勤记录
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

class DepartmentStaffCountView(APIView):
    """
    用于返回每个部门的员工数量
    """
    @method_decorator(cache_page(60 * 10))
    def get(self, request):
        department_counts = OfficeDepartment.objects.annotate(staff_count=Count('users_department')).values('name', 'staff_count')
        return Response(department_counts)