"""
员工相关的API视图集

DepartmentListAPIView:
    部门列表API视图类，返回的是部门的id、name、leader、members字段。

OfficeUserListAPIView:
    用户列表API视图类，返回的是自定义的用户列表，包含id、username、email、department、date_joined字段。

StaffAPIView:
    员工API视图类，用于添加新员工。给新添加的员工发送激活邮件，包含激活链接。

ActivateEmailAPIView：
    当新员工访问激活链接的时候，调用这个API视图类，激活新员工的账号。
    激活成功后，返回一个成功的响应。


"""

import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.officeAuth.models import OfficeDepartment, OfficeUser, UserStatusChoice
from apps.officeAuth.serializers import DepartmentSerializer, UserSerializer
from apps.secret.make_it_secret import StringEncryptor
from apps.staff.serializer import AddStaffSerializer
from apps.staff.tasks import send_email


class DepartmentListAPIView(ListAPIView):
    """部门列表"""
    queryset = OfficeDepartment.objects.all()
    serializer_class = DepartmentSerializer


class OfficeUserListAPIView(ListAPIView):
    """用户列表"""
    # 移除了直接的queryset定义，改为通过get_queryset()方法动态获取
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        根据请求用户的身份返回相应的员工列表：
        1. 超级用户：返回所有员工
        2. 部门负责人或经理：返回所在部门的员工
        3. 普通员工：默认只返回自己或同部门员工
        """
        user = self.request.user

        # 超级用户可以查看所有员工
        if user.is_superuser:
            return OfficeUser.objects.all()

        # 部门负责人或经理可以查看本部门员工
        if user.department:
            # 检查是否是部门负责人
            if user.department.leader == user:
                return OfficeUser.objects.filter(department=user.department)
            # 检查是否是部门经理
            elif user.department.manager == user:
                return OfficeUser.objects.filter(department=user.department)
            # 普通员工，这里可以根据需求定制，例如只返回自己
            else:
                # 普通员工，默认只返回自己或同部门员工
                return OfficeUser.objects.filter(uuid=user.uuid) | OfficeUser.objects.filter(department=user.department)

        # 无部门的用户，默认只返回自己
        return OfficeUser.objects.filter(uuid=user.uuid)

    def user_list(self, queryset):
        """
        排序：
            1. 先根据部门排序，根据department的id字段进行从小到大排序
            2. 一个部门里，先显示部门leader，也就是user.uuid等于department.leader.uuid的用户
            3. 部门leader后面，根据用户的date_joined字段，时间越早，越靠前排序
            4. 返回规则：
            {
                部门1 {
                    leader:[

                    ],
                    members:[

                    ]
                }
            }
        """
        # 先按部门ID排序，然后我们将在代码中手动处理leader优先显示的逻辑
        users_by_dept = {}

        # 首先按部门分组
        for user in queryset:
            dept_name = user.department.name if user.department else '无部门'
            if dept_name not in users_by_dept:
                users_by_dept[dept_name] = {
                    'leader': [],
                    'members': [],
                    'department': user.department,
                    'status': user.status,
                    'superuser': user.is_superuser
                }
            users_by_dept[dept_name]['all_users'].append(user) if 'all_users' in users_by_dept[dept_name] else users_by_dept[dept_name].update({'all_users': [user]})

        # 对每个部门内的用户进行排序
        result = {}
        for dept_name, dept_data in users_by_dept.items():
            result[dept_name] = {
                'leader': [],
                'members': []
            }

            # 先找出部门领导
            leader = None
            if dept_data['department'] and dept_data['department'].leader:
                # 找到与部门leader匹配的用户
                for user in dept_data['all_users']:
                    if user.uuid == dept_data['department'].leader.uuid:
                        leader = user
                        break

            # 如果找到领导，先添加到leader列表
            if leader:
                result[dept_name]['leader'].append({
                    'uuid': leader.uuid,
                    'username': leader.username,
                    'email': leader.email,
                    'date_joined': leader.date_joined,
                    'status': leader.status,
                    'superuser': leader.is_superuser,
                    # 可以根据需要添加其他字段
                })

            # 然后添加其他成员，按date_joined升序排列
            members = [user for user in dept_data['all_users'] if user != leader]
            members.sort(key=lambda x: x.date_joined)

            for member in members:
                result[dept_name]['members'].append({
                    'uuid': member.uuid,
                    'username': member.username,
                    'email': member.email,
                    'date_joined': member.date_joined,
                    'status': member.status,
                    # 可以根据需要添加其他字段
                })

        return result


    def list(self, request, *args, **kwargs):
        # 获取查询集 - 现在会通过get_queryset()获取已过滤的结果
        queryset = self.filter_queryset(self.get_queryset())

        # 使用自定义的userList方法处理查询集
        ordered_data = self.user_list(queryset)

        # 返回自定义格式的数据
        return Response(ordered_data)


class StaffAPIView(APIView):
    """
    添加员工的API类视图

    post； 使用celery异步发送邮件，然后添加员工到数据库
    """

    def post(self, request):
        """添加员工"""
        serializer = AddStaffSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            email = serializer.validated_data.get('email')
            department_id = request.user.department

            # 使用加密处理邮箱
            encryptor = StringEncryptor()
            key = encryptor.encrypt(email)

            try:
                # 异步发送邮件，使用delay确保真正的非阻塞执行
                activate_url = request.build_absolute_uri(reverse('activate_email')) + f'?key={key}'
                # 使用delay方法而不是apply_async，确保简单可靠的异步执行
                def send_activation_email():
                    try:
                        send_email.delay(
                            email,
                            f'您已被添加为{request.user.department.name}的员工',
                            f'{username}，您的初始密码是{password}，请点击下方链接激活。登录系统后，请先修改密码。{activate_url}'
                        )
                    except Exception as email_error:
                        # 记录异步任务提交失败的错误

                        logging.error(f'提交发送激活邮件任务失败: {str(email_error)}')

                # 立即执行邮件发送函数，但不等待其完成
                send_activation_email()

                # 任务添加到celery以后，保存用户到数据库
                user = OfficeUser.objects.create_user(username=username, password=password, email=email)
                user.department_id = department_id
                user.save()
                # 返回成功信息
                return Response({'message':'添加员工成功，激活邮件正在发送中'}, status=status.HTTP_201_CREATED)

            except Exception as e:
                # 捕获所有异常，确保用户创建后不会回滚
                # 记录错误日志，但仍然返回成功响应
                import logging
                logging.error(f'发送激活邮件失败: {str(e)}')
                return Response({'message':'添加员工成功，邮件发送可能延迟'}, status=status.HTTP_201_CREATED)

        else:
            return Response({'error_message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ActivateEmailAPIView(APIView):
    """
    激活邮箱的API类视图

    get： 访问激活链接页面，将key存储在cookie中
    post： 激活页面输入信息后验证，验证通过后激活用户
    """
    def get(self, request):
        """访问激活链接页面"""

        # 获取key
        key = request.GET.get('key')
        response = render(request, 'activation.html')
        response.set_cookie('key', key)

        return response


    def post(self, request) -> JsonResponse:
        """激活页面输入信息后验证"""

        key = request.COOKIES.get('key')
        # 对key进行解密
        try:
            encryptor = StringEncryptor()
            key = encryptor.decrypt(key)
            # 解密成功，验证邮箱是否存在
            try:
                user = OfficeUser.objects.get(email=key)
            except OfficeUser.DoesNotExist:
                return JsonResponse({'error_message':'激活链接无效'}, status=status.HTTP_400_BAD_REQUEST)
            # 邮箱存在，验证密码是否正确
            password = request.data.get('password')

            # 密码为空
            if not password:
                return JsonResponse({'error_message':'请输入密码'}, status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(password):
                # 在验证用户是否已经激活
                if user.is_active or user.status == 1:
                    return JsonResponse({'error_message':'该用户已激活'}, status=status.HTTP_400_BAD_REQUEST)

                if user.department_id == 1:
                    # 证明该用户是董事会成员，is_superuser=True
                    user.is_superuser = True

                user.is_active = True
                user.status = 1
                user.save()
                return JsonResponse({'message':'邮箱激活成功'}, status=status.HTTP_200_OK)

            else:
                return JsonResponse({'error_message':'密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse({'error_message':'激活链接无效'}, status=status.HTTP_400_BAD_REQUEST)


class EditStaffAPIView(UpdateAPIView):
    """
    编辑员工的API类视图
    """
    
    # 定义查询集和序列化器
    queryset = OfficeUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'uuid'  # 使用uuid作为查找字段
    
    def put(self, request, *args, **kwargs) -> JsonResponse:
        """编辑员工的API类视图"""
        
        partial = kwargs.pop('partial', True)  # 允许只更新部分字段
        
        # 获取员工实例
        instance = self.get_object()
        
        # 权限验证：只有超级用户或部门负责人可以编辑员工
        current_user = request.user
        
        # 检查是否是超级用户
        if not current_user.is_superuser:
            # 检查是否是部门负责人
            if instance.department and instance.department.leader_id != current_user.uuid:
                # 检查是否是员工本人（只能编辑自己的部分信息）
                if instance.uuid != current_user.uuid:
                    return JsonResponse({'error_message': '您没有权限编辑该员工信息'}, 
                                      status=status.HTTP_403_FORBIDDEN)
        
        # 创建序列化器实例
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        # 验证数据
        if not serializer.is_valid():
            return JsonResponse({'error_message': serializer.errors}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        # 在保存前检查部门是否发生变化
        # 获取原始部门名称和新部门ID
        original_department = instance.department
        new_department_id = request.data.get('department')
        
        # 如果部门字段有变化
        if new_department_id is not None:
            # 获取新部门实例
            try:
                new_department = OfficeDepartment.objects.get(id=new_department_id)
                # 检查是否是从董事会转到其他部门
                if original_department and original_department.name == '董事会' and new_department.name != '董事会':
                    # 从董事会转出，设置is_superuser为False
                    instance.is_superuser = False
                # 检查是否是从其他部门转到董事会
                elif (not original_department or original_department.name != '董事会') and new_department.name == '董事会':
                    # 转入董事会，设置is_superuser为True
                    instance.is_superuser = True
            except OfficeDepartment.DoesNotExist:
                # 如果新部门ID无效，这里不需要处理，因为serializer.is_valid()已经验证过了
                pass
        
        # 保存更新
        try:
            serializer.save()
            return JsonResponse({'message': '员工信息更新成功', 'data': serializer.data}, 
                              status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'error_message': f'更新失败: {str(e)}'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StaffDownloadAPIView(APIView):
    """
    下载员工的excel表的视图

    前端传来一个包含了员工uuid的列表，后端根据uuid查询员工信息，
    并将员工信息下载为excel表。
    """

    def get(self, request, *args, **kwargs):
        """
        /staff/download?uuid=uuid1&uuid=uuid2&uuid=uuid3

        直接获取uuid列表，根据uuid查询员工信息。
        如果uuid不存在，返回错误响应。
        """
        # 直接获取uuid列表
        uuid_list = request.GET.getlist('uuid')

        if not uuid_list:
            return JsonResponse({'error_message':'请检查uuid参数是否正确传入'}, status=status.HTTP_400_BAD_REQUEST)

        # 去除列表中的空值并清理UUID（移除尾部斜杠等）
        uuid_list = [uuid.rstrip('/') for uuid in uuid_list if uuid]
        if not uuid_list:
            return JsonResponse({'error_message':'uuid列表不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        # 如果当前用户不是超级用户，则只允许下载自己部门的员工信息
        filtered_uuids = uuid_list
        if not request.user.is_superuser:
            # 检查用户是否有部门
            if not request.user.department:
                return JsonResponse({'error_message': '您没有所属部门，无法下载员工信息'}, 
                                  status=status.HTTP_403_FORBIDDEN)
            
            # 判断是否为部门的领导
            if request.user.department.leader_id != request.user.uuid:
                return JsonResponse({'error_message': '您没有权限下载该部门的员工信息'}, 
                                  status=status.HTTP_403_FORBIDDEN)

            # 获取当前用户所属部门
            current_department = request.user.department
            if not current_department:
                return JsonResponse({'error_message': '无法获取您的部门信息'}, 
                                  status=status.HTTP_403_FORBIDDEN)

            # 过滤出当前部门的员工UUID
            valid_uuids = set(OfficeUser.objects.filter(department=current_department).values_list('uuid', flat=True))
            
            # 检查请求中的UUID是否都在当前部门
            filtered_uuids = [uuid for uuid in uuid_list if uuid in valid_uuids]
            
            if not filtered_uuids:
                return JsonResponse({'error_message': '您只能下载属于您部门的员工信息'}, 
                                  status=status.HTTP_403_FORBIDDEN)

        try:
            # 去重
            filtered_uuids = list(set(filtered_uuids))
            
            # 从数据库中查询所有符合条件的员工信息，使用username替换name
            staff_infos = list(OfficeUser.objects.filter(uuid__in=filtered_uuids).values(
                'uuid', 'username', 'email', 'telephone', 'department__name', 'is_superuser', 'status', 'date_joined'
            ))
            
            # 检查查询结果是否为空
            if not staff_infos:
                return JsonResponse({'error_message': '未找到符合条件的员工信息'}, 
                                  status=status.HTTP_404_NOT_FOUND)

            # 转换为DataFrame对象
            df = pd.DataFrame(staff_infos)
            
            # 重命名列名
            df.columns = ['UUID', '姓名', '邮箱', '手机号', '部门', '超级用户', '状态', '入职时间']
            
            # 状态字段转换为中文
            df['状态'] = df['状态'].map({
                UserStatusChoice.ACTIVE: '在职',
                UserStatusChoice.DISABLED: '离职',
                UserStatusChoice.LOCKED: '已锁定'
            })

            # 格式化日期时间字段
            df['入职时间'] = pd.to_datetime(df['入职时间']).dt.strftime('%Y-%m-%d %H:%M:%S')

            response = HttpResponse(content_type='application/xlsx')
            response['Content-Disposition'] = 'attachment; filename="员工信息.xlsx"'

            # 写入Excel文件
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='员工信息')

                # 获取工作表对象
                worksheet = writer.sheets['员工信息']

                # 设置列宽，特别是日期列
                column_widths = {
                    'A': 36,  # UUID
                    'B': 10,  # 姓名
                    'C': 30,  # 邮箱
                    'D': 15,  # 手机号
                    'E': 15,  # 部门
                    'F': 10,  # 超级用户
                    'G': 8,   # 状态
                    'H': 20   # 入职时间
                }

                # 设置列宽
                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width

            return response
            
        except Exception as e:
            import logging
            logging.error(f'下载员工信息失败: {str(e)}')
            return JsonResponse({'error_message': f'出现异常: {str(e)}'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)