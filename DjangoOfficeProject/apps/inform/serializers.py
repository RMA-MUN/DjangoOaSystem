"""
通知模块序列化器

此模块定义了通知模型的序列化器，用于将通知数据转换为JSON格式，以及将JSON数据反序列化为通知模型实例。

序列化器包括：InformSerializer：通知模型的序列化器，包含通知的所有字段，以及作者和可见部门的序列化器。

"""

from rest_framework import serializers
from .models import Inform
from apps.officeAuth.models import OfficeDepartment, OfficeUser
from apps.officeAuth.serializers import UserSerializer, DepartmentSerializer

class InformSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    departments = DepartmentSerializer(many=True, read_only=True)  # 修改为复数形式
    # 前端传的部门列表，用于创建通知时指定部门可见
    department_ids = serializers.ListField(write_only=True, required=True)  # 明确设置required=True

    class Meta:
        model = Inform
        fields = ['id', 'title', 'content', 'create_time', 'update_time', 'public', 
                 'author', 'departments', 'department_ids']  # 明确列出字段，避免__all__包含不需要的字段


    # 重写create方法，在创建通知时，根据department_ids指定部门可见
    def create(self, validated_data):
        department_ids = validated_data.pop('department_ids', [])
        
        # 验证department_ids不为空
        if not department_ids:
            raise serializers.ValidationError({"department_ids": "部门列表不能为空"})
            
        # 转换为整数
        try:
            department_ids = [int(id) for id in department_ids]
        except ValueError:
            raise serializers.ValidationError({"department_ids": "部门ID必须为数字"})
        
        # 从validated_data中移除可能存在的public键，避免参数重复
        if 'public' in validated_data:
            validated_data.pop('public')

        # 判断是否存在[0]，如果存在，则表示通知对所有部门可见
        if 0 in department_ids:
            inform = Inform.objects.create(public=True, author=self.context['request'].user, **validated_data)
        else:
            # 否则，根据department_ids指定部门可见
            departments = OfficeDepartment.objects.filter(id__in=department_ids).all()
            if not departments:
                raise serializers.ValidationError({"department_ids": "指定的部门不存在"})
                
            inform = Inform.objects.create(public=False, author=self.context['request'].user, **validated_data)
            inform.departments.set(departments)
            inform.save()
        return inform