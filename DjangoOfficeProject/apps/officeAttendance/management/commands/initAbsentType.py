"""
初始化考勤类型
"""

from apps.officeAttendance.models import AttendanceType
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        absent_type_list = ['病假', '事假', '年假', '婚假', '丧假', '工伤假', '产假']
        absents = []
        # 遍历列表，创建AttendanceType对象并添加到absents列表
        for absent_type in absent_type_list:
            absent_obj = AttendanceType(name=absent_type)
            absents.append(absent_obj)

        AttendanceType.objects.bulk_create(absents)
        self.stdout.write(self.style.SUCCESS('成功初始化考勤类型'))