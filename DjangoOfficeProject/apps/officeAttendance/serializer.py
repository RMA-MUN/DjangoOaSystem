"""
此模块定义了处理考勤记录和考勤类型的序列化器，负责将数据库模型转换为可传输的JSON格式，
以及将用户输入的JSON数据验证并转换为模型实例。

主要功能:
- 定义考勤记录的序列化与反序列化规则
- 处理考勤类型的数据转换
- 实现考勤记录的创建和审批逻辑
- 验证用户输入数据的有效性

类:
    - AttendanceTypeSerializer: 处理考勤类型的数据序列化
    - AttendanceSerializer: 处理考勤记录的创建、更新和数据序列化

依赖关系:
    - rest_framework.serializers: Django REST framework的序列化器基类
    - apps.officeAuth.serializers.UserSerializer: 用户信息序列化器
    - apps.officeAttendance.models: 考勤相关的数据模型
    - apps.officeAttendance.utils: 考勤相关的工具函数
"""

from rest_framework import serializers
from apps.officeAuth.serializers import UserSerializer
from apps.officeAttendance.models import Attendance, Attendance_Status, AttendanceType
from rest_framework import exceptions
from apps.officeAttendance.utils import get_approver, validate_approver  # 导入新的工具函数

class AttendanceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceType
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    """
    read_only: 只会在序列化时使用，不会在反序列化时使用
    write_only: 只会在反序列化时使用，不会在序列化时使用
    """
    attendance_type = AttendanceTypeSerializer(read_only=True)
    attendance_type_id = serializers.IntegerField(write_only=True)
    requester = UserSerializer(read_only=True)
    responser = UserSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'

    # 验证事件id是否存在
    def validate_attendance_type_id(self, value) -> int:
        """验证事件id是否存在"""
        if not AttendanceType.objects.filter(id=value).exists():
            raise exceptions.ValidationError(detail="事件id不存在")
        return value

    def create(self, validated_data) -> Attendance:
        """创建考勤记录"""
        # 直接从context中获取request对象，然后获取user
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise exceptions.AuthenticationFailed(detail="用户未认证")
        
        user = request.user
        
        # 获取审批者
        responser = get_approver(user)
        
        # 验证审批者并更新数据
        validate_approver(responser, user, validated_data)

        attendance = Attendance.objects.create(**validated_data, requester=user, responser=responser)

        return attendance

    def update(self, instance, validated_data) -> Attendance:
        """审批考勤"""
        if instance.status != Attendance_Status.PENDING:
            raise exceptions.PermissionDenied(detail="该考勤记录已被处理")

        # 从context中获取request对象，然后获取user
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise exceptions.AuthenticationFailed(detail="用户未认证")
        
        user = request.user

        # 审批人必须是考勤记录的审批人
        if instance.responser.uuid != user.uuid:
            raise exceptions.PermissionDenied(detail="该考勤记录的审批人不是您")

        instance.status = validated_data['status']
        instance.approval_content = validated_data['approval_content']
        instance.save()
        
        return instance