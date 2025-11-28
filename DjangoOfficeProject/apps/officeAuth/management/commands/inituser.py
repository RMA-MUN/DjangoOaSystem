"""
这里初始化一些用户数据
    - lzl管理：技术部， 运营部
    - bei_e管理：销售部， 人力部， 财政部

    董事会成员：
        - 灵自灵（superuser, 董事会leader）
        - 北枙（superuser）
    技术部成员：
        - 瀚辰 (技术部leader)
    财务部成员：
        - 靖易 (财务部leader)
    人事部成员：
        - 鑫然 (人事部leader)
    销售部成员：
        - 慕梓 (销售部leader)
    运营部成员：
        - 云乔 (运营部leader)

"""

from apps.officeAuth.models import OfficeUser, OfficeDepartment
from django.core.management.base import BaseCommand
from django.db import IntegrityError

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        创建初始化用户数据
        1. 董事会的默认都是superuser
        2. 其他部门的默认都是普通用户
        3. 所有人的密码都默认666666
        """
        # 先检查并创建必要的部门
        departments = {
            "董事会": None,
            "销售部": None,
            "技术部": None,
            "运营部": None,
            "人力部": None,
            "财政部": None
        }
        
        for dept_name in departments:
            # 使用get_or_create避免重复创建部门
            department, created = OfficeDepartment.objects.get_or_create(name=dept_name)
            departments[dept_name] = department
            if created:
                self.stdout.write(f"创建部门: {dept_name}")
        
        # 为了避免重复创建用户，先检查用户是否已存在
        def get_or_create_user(email, username, password, department, is_superuser=False):
            try:
                # 尝试通过email查找用户
                return OfficeUser.objects.get(email=email)
            except OfficeUser.DoesNotExist:
                # 用户不存在，创建新用户
                if is_superuser:
                    return OfficeUser.objects.create_superuser(
                        username=username,
                        password=password,
                        email=email,
                        telephone='1380000' + str(len(email.split('@')[0]) % 10000).zfill(4),  # 生成11位电话号码
                        department=department,
                        status=1  # 假设1表示激活状态
                    )
                else:
                    return OfficeUser.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        telephone='1380000' + str(len(email.split('@')[0]) % 10000).zfill(4),  # 生成11位电话号码
                        department=department,
                        status=1  # 假设1表示激活状态
                    )
        
        # 创建用户
        lzl = get_or_create_user(
            email="lzl@qq.com",
            username="灵自灵",
            password="666666",
            department=departments["董事会"],
            is_superuser=True
        )

        bei_e = get_or_create_user(
            email="bei_e@qq.com",
            username="北枙",
            password="666666",
            department=departments["董事会"],
            is_superuser=True
        )

        mu_zi = get_or_create_user(
            email="sales@qq.com",
            username="慕梓",
            password="666666",
            department=departments["销售部"]
        )
        
        han_chen = get_or_create_user(
            email="developer@qq.com",
            username="瀚辰",
            password="666666",
            department=departments["技术部"]
        )
        
        yun_qiao = get_or_create_user(
            email="operator@qq.com",
            username="云乔",
            password="666666",
            department=departments["运营部"]
        )
        
        xin_ran = get_or_create_user(
            email="office@qq.com",
            username="忻然",
            password="666666",
            department=departments["人力部"]
        )
        
        jing_yi = get_or_create_user(
            email="finance@qq.com",
            username="静怡",
            password="666666",
            department=departments["财政部"]
        )

        # 重置并设置部门的leader和manager
        # 为了确保关系正确，先更新所有部门的数据
        department_updates = [
            {"name": "董事会", "leader": lzl, "manager": None},
            {"name": "销售部", "leader": mu_zi, "manager": bei_e},
            {"name": "技术部", "leader": han_chen, "manager": lzl},
            {"name": "运营部", "leader": yun_qiao, "manager": lzl},
            {"name": "人力部", "leader": xin_ran, "manager": bei_e},
            {"name": "财政部", "leader": jing_yi, "manager": bei_e}
        ]
        
        for update in department_updates:
            dept = departments[update["name"]]
            old_leader = dept.leader.username if dept.leader else None
            old_manager = dept.manager.username if dept.manager else None
            
            # 更新部门信息
            dept.leader = update["leader"]
            dept.manager = update["manager"]
            dept.save()
            
            # 记录更新信息
            new_leader = update["leader"].username if update["leader"] else None
            new_manager = update["manager"].username if update["manager"] else None
            self.stdout.write(
                f"更新部门: {update['name']} "
                f"| Leader: {old_leader} -> {new_leader} "
                f"| Manager: {old_manager} -> {new_manager}"
            )
        
        # 验证更新结果
        self.stdout.write("\n验证部门关系设置:")
        for dept_name, dept in departments.items():
            # 重新从数据库获取以确保读取最新数据
            fresh_dept = OfficeDepartment.objects.get(id=dept.id)
            leader = fresh_dept.leader.username if fresh_dept.leader else "None"
            manager = fresh_dept.manager.username if fresh_dept.manager else "None"
            self.stdout.write(
                f"部门: {dept_name} "
                f"| Leader: {leader} (ID: {fresh_dept.leader_id}) "
                f"| Manager: {manager} (ID: {fresh_dept.manager_id})"
            )

        self.stdout.write(self.style.SUCCESS("初始化用户数据完成"))
        