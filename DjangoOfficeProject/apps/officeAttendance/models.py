"""
此模块定义了考勤相关的数据模型，包括考勤状态属性，考勤类型，考勤详情。

主要功能：
    - 定义考勤状态属性，包括审核中、已审批、已拒绝共三种考勤状态，分别用PENDING, APPROVED, REJECTED表示
    - 定义考勤类型模型，包括考勤类型名称，创建时间
    - 定义考勤详情模型，包括请假人、审批人、考勤类型、考勤时间、请假详情、考勤状态、审批状态

类:
    - Attendance_Status: 考勤状态属性
    - AttendanceType: 考勤类型
    - Attendance: 考勤详情模型(详细属性见模型注释)

依赖关系：
    - rest_framework: Django REST framework的模型类
    - apps.officeAuth.models: 认证相关的数据模型
    - apps.officeAuth.serializers: 用户相关的序列化器
    - apps.officeAttendance.serializers: 考勤相关的序列化器
    - apps.officeAttendance.utils: 考勤相关的工具函数

"""

from django.db import models
from django.contrib.auth import get_user_model

from apps.officeAuth.models import OfficeUser

officeUser = get_user_model()

# Create your models here.

class Attendance_Status(models.Model):
    """考勤状态属性"""
    PENDING = 1 # 审核中
    APPROVED = 2 # 已审批
    REJECTED = 3 # 已拒绝
    
    ATTENDANCE_STATUS = (
        (PENDING, "审核中"),
        (APPROVED, "已审批"),
        (REJECTED, "已拒绝"),
    )

class AttendanceType(models.Model):
    """
     考勤类型模型
    """
    name = models.CharField(max_length=100, verbose_name='考勤类型名称')
    creat_time = models.DateTimeField(auto_now_add=True)

class Attendance(models.Model):
    """
     考勤详情模型
      - 请假人(名称,关联用户模型)
          - 审批人(名称,关联用户模型)
          - 考勤类型(关联考勤类型模型)
          - 考勤时间(日期时间字段)
              - 开始时间
              - 结束时间
              - 发起时间
              - 审批时间
          - 请假详情(text字段,用于记录请假详情)
          - 考勤状态(choices字段,例如: 正常,迟到,早退,缺勤)
          - 审批状态(choices字段,例如: 待审批,已审批,已拒绝)

     - 审批人(名称,关联用户模型)
          - 审批状态(choices字段,例如: 待审批,已审批,已拒绝)
          - 审批时间(日期时间字段)
          - 审批详情(text字段,用于记录审批详情)
    """
    title = models.CharField(max_length=200, verbose_name='考勤标题')
    request_content = models.TextField(verbose_name='考勤详情')
    attendance_type = models.ForeignKey(
        AttendanceType,
        on_delete=models.CASCADE,
        verbose_name='考勤类型',
        related_name='attendance',
        related_query_name='attendance'
    )
    # 如果一个模型中有多个外键指向同一个模型，需要使用related_name和related_query_name参数来避免命名冲突
    requester = models.ForeignKey(
        officeUser,
        on_delete=models.CASCADE,
        verbose_name='请假人',
        related_name="attendance_requests",
        related_query_name='attendance_requests'
    )
    # 获取到当前发起请假人的name存储为requester_name
    requester_name = models.CharField(max_length=100, verbose_name='请假人名称', blank=True, null=True)
    # 获取到当前发起请假人的审批人(部门领导)存储为responser_name
    responser_name = models.CharField(max_length=100, verbose_name='审批人名称', blank=True, null=True)
    responser = models.ForeignKey(
        officeUser,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='审批人',
        related_name="attendance_responsers",
        related_query_name='attendance_responsers'
    )
    status = models.IntegerField(
        choices=Attendance_Status.ATTENDANCE_STATUS,
        default=Attendance_Status.PENDING,
        verbose_name='考勤状态'
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField(verbose_name="请假开始时间")
    end_time = models.DateTimeField(verbose_name="请假结束时间")
    approval_time = models.DateTimeField(
        verbose_name="审批时间",
        null=True,
        blank=True
    )
    approval_content = models.TextField(
        verbose_name='审批详情',
        null=True,
        blank=True
    )

    ordering = ['-create_time']

    class Meta:
        db_table = 'attendance'
        verbose_name = '考勤详情'
        verbose_name_plural = '考勤详情'
        ordering = ['-create_time']

    # 根据发起请假人的id查询到用户的username并存储到requester_name字段中
    def get_name_by_id(self, user_id):
        try:
            user = OfficeUser.objects.get(uuid=user_id)
            return user.username
        except OfficeUser.DoesNotExist:
            return None

    # 重写save方法以确保数据一致性
    def save(self, *args, **kwargs):
        # 更新发起请假人和审批人的名字
        if self.requester:
            self.requester_name = self.requester.username
        else:
            self.requester_name = None
            
        if self.responser:
            self.responser_name = self.responser.username
        else:
            self.responser_name = None

        super().save(*args, **kwargs)