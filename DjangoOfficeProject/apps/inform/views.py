"""
通知视图集

此模块提供了通知的CRUD操作，包括创建、读取、更新、删除通知。
1. 创建通知时，根据department_ids指定部门可见， 当department_ids包含[0]， 则表示通知对所有部门可见
2. 读取通知时，根据用户权限返回不同的通知列表
3. 更新通知时，只能更新自己发布的通知
4. 删除通知时，只能删除自己发布的通知

"""

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.inform.models import Inform
from apps.inform.serializers import InformSerializer


class InformViewSet(viewsets.ModelViewSet):
    queryset = Inform.objects.all()
    serializer_class = InformSerializer

    def get_queryset(self):
        """
        根据用户权限返回不同的通知列表
        当通知为public=True, inform_department包含了用户所在的部门， 用户为发布者， 则返回所有通知
        当通知为public=False, inform_department包含了用户所在的部门， 用户为发布者， 则返回所有通知
        当通知为public=False, inform_department不包含了用户所在的部门， 用户为发布者， 则返回空列表
        当通知为public=False, inform_department不包含了用户所在的部门， 用户为普通用户， 则返回所有通知
        """
        queryset = self.queryset.prefetch_related('reads').filter(Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user))
        return queryset

    def get_object(self):
        """
        重写get_object方法，确保根据ID精确获取单个对象
        """
        obj = Inform.objects.get(id=self.kwargs.get('pk'))
        # 验证用户是否有权限访问此对象
        if not (obj.public or self.request.user.department in obj.departments.all() or obj.author == self.request.user):
            raise PermissionError("您没有权限访问此通知")
        return obj

    def destroy(self, request, *args, **kwargs) ->Response:
        """
        删除通知， 只能删除自己发布的通知
        :param request:
        :param args:
        :param kwargs:
        :return: Response
        """
        instance = self.get_object()  # 使用重写后的get_object方法
        if instance.author.uuid == request.user.uuid:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)