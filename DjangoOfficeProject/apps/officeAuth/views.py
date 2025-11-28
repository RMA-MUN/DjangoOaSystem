"""
视图模块：
    - LoginView(post): 类视图，用于用户登录，验证用户登录信息，并调用jwt生成器生成token

    - ResetPasswordView(post): 类视图，继承自AuthenticatedView父类用于身份验证，重置用户密码

    - TokenRefreshView(post): 类视图，返回刷新后的token

    - UserDetailView(get): 类视图，返回序列化后的当前用户信息

"""
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from .serializers import LoginSerializer, UserSerializer, ResetPasswordSerializer
from datetime import datetime
from .authentications import JWTAuthentication, JWTTokenGenerator
from rest_framework.response import Response
from rest_framework import status
from .fatherClass import AuthenticatedView
from .models import OfficeDepartment, OfficeUser
from .serializers import UpdateDepartmentLeaderSerializer

# Create your views here.

authentication = JWTAuthentication()
jwttoken = JWTTokenGenerator()


class LoginView(APIView):
    """类视图，处理用户登录"""
    def post(self, request) -> Response:
        """
        处理post请求，验证用户登录
        :param request: post请求，包含用户登录信息
        :return: Response对象，包含登录成功信息，用户对象和token
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')  # 从序列化器中获取用户对象
            user.last_login = datetime.now()  # 更新用户最后登录时间
            user.save()  # 保存用户对象
            # 生成JWT token - 正确处理返回的元组
            token, expire_time = jwttoken.generate_token(user)
            return Response({
                            "message": f"{user.username} 登录成功",
                            "user": UserSerializer(user).data,
                            "token": token}, 
                            status=status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(AuthenticatedView):
    """类视图，处理用户重置密码"""

    def post(self, request) -> Response:
        """
        处理post请求，重置用户密码
        :param request: old_password, new_password, confirm_password
        :return: Response对象，包含重置密码成功或失败的信息
        """

        serializer = ResetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data.get('user')  # 从序列化器中获取用户对象
            user.set_password(serializer.validated_data.get('new_password'))  # 设置新密码
            user.save()  # 保存用户对象
            return Response({
                "message": "密码重置成功"
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    """处理Token刷新请求"""
    def post(self, request) -> Response:
        """
        处理post请求，刷新用户Token
        :param request: post请求，包含旧Token
        :return: Response对象，包含新Token和过期时间
        """
        token = request.data.get('token')
        if not token:
            return Response({
                "detail": "Token不能为空"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_token, expire_time = jwttoken.refresh_token(token)
            return Response({
                "message": "Token刷新成功",
                "token": new_token,
                "expire_time": expire_time
            }, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response({
                "detail": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "detail": "Token刷新失败"
            }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(AuthenticatedView):
    """获取当前登录用户详情"""
    def get(self, request) -> Response:
        """
        处理get请求，获取当前登录用户详情
        :param request: get请求
        :return: Response对象，包含用户详情
        """
        serializer = UserSerializer(request.user)
        return Response({
            "message": "获取用户详情成功",
            "user": serializer.data
        }, status=status.HTTP_200_OK)


class UpdateDepartmentLeaderAPIView(APIView):
    """更新部门领导的API视图"""
    
    def post(self, request, *args, **kwargs):
        """处理部门领导变更请求"""
        # 权限验证：只有超级用户或高级管理层可以变更部门领导
        user = request.user
        if not user.is_superuser and not user.manager_department.exists():
            return Response(
                {'error_message': '您没有权限变更部门领导'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 验证请求数据
        serializer = UpdateDepartmentLeaderSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取验证后的对象
        department = serializer.validated_data['department']
        new_leader = serializer.validated_data['new_leader']
        
        # 保存旧领导信息（可选，用于日志记录）
        old_leader = department.leader
        
        try:
            # 更新部门领导
            department.leader = new_leader
            department.save()  # OfficeDepartment模型的save方法会自动更新leader_name
            
            # 返回成功响应
            return Response(
                {
                    'message': '部门领导变更成功',
                    'department': department.name,
                    'old_leader': old_leader.username if old_leader else None,
                    'new_leader': new_leader.username
                }, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error_message': f'更新失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )