from rest_framework import serializers

from apps.officeAuth.models import OfficeUser, OfficeDepartment

class AddStaffSerializer(serializers.Serializer):
    """添加员工的序列化器"""
    username = serializers.CharField(
        max_length=20,
        min_length=2,
        required=True,
        help_text='用户名',
        error_messages={
            'max_length':'用户名最多20个字符',
            'min_length':'用户名最少2个字符'
        })

    password = serializers.CharField(
        max_length=20,
        min_length=6,
        required=True,
        help_text='密码',
        error_messages={
            'max_length':'密码最多20个字符',
            'min_length':'密码最少6个字符'
        })
    email = serializers.EmailField(
        required=True,
        help_text='邮箱',
        error_messages={
            'invalid':'邮箱格式错误'
        })
    department = serializers.IntegerField(
        required=True,
        help_text='部门ID',
        error_messages={
            'required':'部门ID不能为空'
        })


    def validate(self, attrs):
        """验证添加员工的序列化器"""
        # 验证邮箱是否已存在
        email = attrs.get('email')
        if OfficeUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email':'邮箱已存在'})

        # 验证用户是否为leader, 获取到当前用户的uuid，与department的leader_id进行比较
        department_id = attrs.get('department')
        department = OfficeDepartment.objects.filter(id=department_id).first()
        if department.leader_id != self.context['request'].user.uuid:
            raise serializers.ValidationError({'department':'您不是该部门的负责人，不能添加员工'})

        return attrs