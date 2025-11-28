from django.core.management.base import BaseCommand
from apps.officeAuth.models import OfficeDepartment

class Command(BaseCommand):
    def handle(self, *args, **options):
        """创建初始化部门数据"""
        boarder = OfficeDepartment.objects.create(
            name="董事会",
            introduction="负责公司的战略决策和管理",
        )

        # 销售部
        sales = OfficeDepartment.objects.create(
            name="销售部",
            introduction="销售产品和服务",
        )

        # 技术部
        developer = OfficeDepartment.objects.create(
            name="技术部",
            introduction="开发和维护公司的软件产品",
        )

        # 运营部
        operator = OfficeDepartment.objects.create(
            name="运营部",
            introduction="日常运营和管理",
        )

        # 人力部
        hr = OfficeDepartment.objects.create(
            name="人力部",
            introduction="人力资源管理",
        )

        # 财政部
        finance = OfficeDepartment.objects.create(
            name="财政部",
            introduction="财务管理",
        )

        self.stderr.write(self.style.SUCCESS("初始化部门数据完成"))
