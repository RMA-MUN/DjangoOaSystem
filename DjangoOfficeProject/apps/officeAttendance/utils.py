"""
考勤相关的工具函数和类

get_approver: 获取指定用户的请假审批者
        Args:
            user: OfficeUser实例，请假的用户

        Returns:
            OfficeUser实例或None：审批者用户实例

        Raises:
            exceptions.ValidationError: 当部门没有设置manager且用户不是董事会成员时抛出
validate_approver: 验证审批者是否有效
        Args:
            approver: OfficeUser实例或None，审批者
            user: OfficeUser实例，请假的用户
            validated_data: 验证后的数据字典

        Returns:
            None

        Raises:
            exceptions.ValidationError: 当审批者不是部门manager、leader或董事会成员时抛出

CustomPageNumberPagination: 自定义分页器类
        Args:
            request: HttpRequest实例，请求对象
            queryset: QuerySet实例，查询集
            view: View实例，视图对象

        Returns:
            PaginationResult：分页结果对象

        Raises:
            None

        PS: 目前分页功能前端有些问题，需要前端做出相应的调整
"""

from rest_framework import exceptions
from rest_framework.response import Response

from apps.officeAttendance.models import Attendance_Status
from apps.officeAuth.models import OfficeUser
from rest_framework.pagination import PageNumberPagination


def get_approver(user: OfficeUser) -> OfficeUser or None:
    """
    获取指定用户的请假审批者
    
    逻辑：
    - 如果用户是部门负责人，则审批人为部门manager
    - 如果用户是董事会成员，则审批人为None（直接审批通过）
    - 如果用户是普通员工，则审批人为部门leader
    
    Args:
        user: OfficeUser实例，请假的用户
    
    Returns:
        OfficeUser实例或None：审批者用户实例
    
    Raises:
        exceptions.ValidationError: 当部门没有设置manager且用户不是董事会成员时抛出
    """
    # 新的审批人逻辑：如果用户是部门负责人，则审批人为部门manager
    if user.department and user.department.leader and user.department.leader.uuid == user.uuid:
        # 用户是部门负责人
        if user.department.name == "董事会":
            # 董事会成员没有上级，直接审批通过
            return None
        else:
            # 使用部门manager作为审批人
            return user.department.manager
    else:
        # 普通员工，使用部门leader作为审批人
        return user.department.leader if user.department else None


def validate_approver(approver: OfficeUser or None, user: OfficeUser, validated_data: dict) -> None:
    """
    验证审批者是否有效，并根据情况更新验证数据
    
    Args:
        approver: OfficeUser实例或None，审批者
        user: OfficeUser实例，请假的用户
        validated_data: 验证后的数据字典
    
    Raises:
        exceptions.ValidationError: 当部门没有设置manager且用户不是董事会成员时抛出
    """
    if approver is None and user.department and user.department.name != "董事会":
        # 如果manager不存在，抛出异常
        raise exceptions.ValidationError(detail="当前部门没有设置经理作为审批人")

    if approver is None:
        # 董事会成员或没有审批人，直接审批通过
        validated_data['status'] = Attendance_Status.APPROVED


class CustomPageNumberPagination(PageNumberPagination):
    """自定义分页器类"""
    # 默认每页显示的数据条数
    page_size = 10
    # URL中表示每页数据条数的参数名
    page_size_query_param = 'page_size'
    # 每页最多显示的数据条数
    max_page_size = 100
    # URL中表示页码的参数名
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """自定义分页响应格式"""
        return Response({
            'code': 200,
            'message': 'success',
            'total_count': self.page.paginator.count,
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })