"""
序列化模块：
    - LoginSerializer： 登录序列化器，对用户输入的登录信息进行验证
        - validate： 验证用户名或邮箱是否存在，密码是否正确，用户状态是否为激活，最后返回dict

    - DepartmentSerializer： 部门序列化器，对部门信息进行验证
        - Meta: 对指定字段进行验证， 为OfficeUser序列化的内容进行嵌套序列化
    - UserSerializer： 用户序列化器， 序列化用户信息
        - Meta: 序列化用户模型并返回，使用嵌套序列化器DepartmentSerializer使返回的部门信息更详细

"""

from rest_framework import serializers
from .models import OfficeUser, UserStatusChoice, OfficeDepartment
from django.db.models import Q

class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(required=False, allow_blank=True, help_text="用户名")
    email = serializers.EmailField(required=False, help_text="邮箱")
    password = serializers.CharField(max_length=20, min_length=6, required=True, help_text="密码")

    def validate(self, attrs) -> dict:
        """验证用户名或邮箱是否存在，密码是否正确，用户状态是否为激活"""
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        # 验证用户名或邮箱至少提供一个
        if not username and not email:
            raise serializers.ValidationError("用户名或邮箱至少提供一个")

        # 验证用户名或邮箱是否存在
        user_query = OfficeUser.objects.filter(Q(username=username) | Q(email=email)) if username and email else \
                    OfficeUser.objects.filter(username=username) if username else \
                    OfficeUser.objects.filter(email=email)
                     
        if not user_query.exists():
            raise serializers.ValidationError("用户名或邮箱不存在")

        # 获取用户对象
        user = user_query.first()
        
        # 验证密码是否正确
        if not user.check_password(password):
            raise serializers.ValidationError("密码错误")

        # 验证用户状态是否为激活
        if user.status != UserStatusChoice.ACTIVE:
            raise serializers.ValidationError("用户状态异常，请检查是否激活或已被锁定")

        # 将用户对象添加到验证数据中，便于视图使用，减少SQL语句的查询次数
        attrs['user'] = user
        return attrs

class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    class Meta:
        model = OfficeDepartment
        # fields = '__all__'
        exclude = ('introduction', 'leader', 'manager')

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    # 读取时使用嵌套序列化器显示详细信息
    department_info = DepartmentSerializer(source='department', read_only=True)
    # 写入时使用PrimaryKeyRelatedField允许通过ID更新
    department = serializers.PrimaryKeyRelatedField(queryset=OfficeDepartment.objects.all(), allow_null=True)
    
    class Meta:
        model = OfficeUser
        exclude = ('password', 'groups', 'user_permissions',)


class ResetPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""
    old_password = serializers.CharField(max_length=20, min_length=6, required=True, help_text="旧密码")
    new_password = serializers.CharField(max_length=20, min_length=6, required=True, help_text="新密码")
    confirm_password = serializers.CharField(max_length=20, min_length=6, required=True, help_text="确认密码")

    def validate(self, attrs) -> dict:
        """验证新密码和确认密码是否一致"""
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        # 验证旧密码是否正确
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError("请检查旧密码是否正确")

        # 新密码不能和旧密码相同
        if new_password == old_password:
            raise serializers.ValidationError("新密码不能和旧密码相同")

        if new_password != confirm_password:
            raise serializers.ValidationError("新密码和确认密码不一致")
        
        # 将user添加到验证数据中，以便视图使用
        attrs['user'] = user
        return attrs


class UpdateDepartmentLeaderSerializer(serializers.Serializer):
    """更新部门领导的序列化器"""
    department_id = serializers.IntegerField(required=True, help_text='部门ID')
    new_leader_uuid = serializers.CharField(required=True, help_text='新领导的UUID')
    
    def validate(self, attrs):
        """验证部门和新领导是否存在"""
        department_id = attrs.get('department_id')
        new_leader_uuid = attrs.get('new_leader_uuid')
        
        # 验证部门是否存在
        if not OfficeDepartment.objects.filter(id=department_id).exists():
            raise serializers.ValidationError({'department_id': '部门不存在'})
        
        # 验证新领导是否存在
        if not OfficeUser.objects.filter(uuid=new_leader_uuid).exists():
            raise serializers.ValidationError({'new_leader_uuid': '用户不存在'})
        
        # 获取部门和用户对象
        department = OfficeDepartment.objects.get(id=department_id)
        new_leader = OfficeUser.objects.get(uuid=new_leader_uuid)
        
        # 确保新领导属于该部门
        if new_leader.department_id != department_id:
            raise serializers.ValidationError({'new_leader_uuid': '新领导必须属于该部门'})
        
        # 将验证后的对象添加到validated_data中
        attrs['department'] = department
        attrs['new_leader'] = new_leader
        
        return attrs