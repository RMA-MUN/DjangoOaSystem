""""
此模块定义了处理考勤相关功能的视图类，负责接收HTTP请求，调用相应的业务逻辑，
并返回适当的HTTP响应。视图类主要实现了考勤的发起、审批、查询等核心功能。

主要功能:
    - 发起新的考勤申请
    - 审批待处理的考勤申请
    - 查询不同权限范围内的考勤记录
    - 获取所有的考勤类型信息
    - 查询当前用户的考勤审批人

类:
    - AbsentViewSet: 处理考勤的创建、更新和列表查询
    - AttendanceTypeViewSet: 处理考勤类型的查询
    - AttendanceResponserViewSet: 处理考勤审批人的查询

依赖关系:
    - rest_framework: Django REST framework的视图基类和混合类
    - apps.officeAttendance.models: 考勤相关的数据模型
    - apps.officeAttendance.serializer: 考勤相关的序列化器
    - apps.officeAttendance.utils: 考勤相关的工具函数
    - apps.officeAuth.fatherClass: 认证相关的父类视图
    - apps.officeAuth.serializers: 用户相关的序列化器
"""

from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.officeAttendance.models import Attendance, AttendanceType
from apps.officeAttendance.serializer import AttendanceSerializer, AttendanceTypeSerializer
from apps.officeAttendance.utils import get_approver, CustomPageNumberPagination
from apps.officeAuth.fatherClass import AuthenticatedView
from apps.officeAuth.serializers import UserSerializer


# Create your views here.

class AbsentViewSet(AuthenticatedView,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    GenericViewSet,
                    mixins.ListModelMixin,
                   ):

    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    # 添加分页器
    pagination_class = CustomPageNumberPagination

    def update(self, request, *args, **kwargs):
        """允许只更新部分字段"""
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def get_serializer_context(self) -> dict:
        """添加request到serializer的context中"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def post(self, request, *args, **kwargs) -> Response:
        return self.create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs) ->Response:
        """
        获取考勤列表

        逻辑：
            - 如果who为'requester'，则返回所有发起的考勤记录
            - 如果who为'responser'，则返回所有被处理的考勤记录
            - 如果who为'leader'，则返回所有作为responser和requester的考勤记录
            - 如果who为'manager'，则返回所有的考勤记录

        args:
            - who: 可选参数，指定查询范围，可选值为'requester', 'responser', 'leader', 'manager'

        :returns: 包含考勤记录的JSON响应
        """
        queryset = self.get_queryset()
        who = request.query_params.get('who', None)

        if who == 'leader':
            queryset = queryset.filter(responser=request.user) | queryset.filter(requester=request.user)
        elif who == 'manager':
            queryset = queryset.all()
        else:
            queryset = queryset.filter(requester=request.user) | queryset.filter(responser=request.user)

        # 分页查询
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

class AttendanceTypeViewSet(APIView):
    """获取到所有考勤类型的类视图"""
    def get(self, request, *args, **kwargs) -> Response:
        type = AttendanceType.objects.all()
        serializer = AttendanceTypeSerializer(type, many=True)
        return Response(serializer.data)


class AttendanceResponserViewSet(APIView):
    def get(self, request, *args, **kwargs) -> Response:
        """
        获取所有的考勤审批者
        """
        responser = get_approver(request.user)
        serializer = UserSerializer(responser)
        return Response(serializer.data)
