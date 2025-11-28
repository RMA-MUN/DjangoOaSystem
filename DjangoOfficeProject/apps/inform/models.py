"""
通知模块模型定义

此模块定义了企业办公系统中的通知相关数据模型，包括：
1. Inform - 通知主模型，存储通知内容、作者、可见范围等信息
2. InformRead - 通知阅读记录模型，跟踪用户对通知的阅读状态

模型设计遵循Django ORM最佳实践，支持通知的发布、权限控制和阅读状态追踪。
"""
from django.db import models
from apps.officeAuth.models import OfficeUser, OfficeDepartment


class Inform(models.Model):
    """
    通知模型
    
    用于存储系统中的通知信息，支持公开通知和部门限定通知两种模式。
    
    字段说明：
    - title: 通知标题，最大长度255个字符
    - content: 通知内容，支持长文本
    - create_time: 通知创建时间，自动设置为创建时的时间
    - update_time: 通知更新时间，自动设置为每次保存时的时间
    - public: 是否为公开通知（对所有部门可见）
    - author: 通知作者，与OfficeUser模型建立外键关系
    - departments: 通知可见部门，与OfficeDepartment模型建立多对多关系
    
    数据权限控制：
    - 如果public=True，表示通知对所有部门可见
    - 如果public=False，表示通知仅对departments字段指定的部门可见
    - 通知作者始终可以看到自己发布的通知
    """
    title = models.CharField(max_length=255, verbose_name="通知标题")
    content = models.TextField(verbose_name="通知内容")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    # 如果前端传的departments中包含[0]，则表示通知对所有部门可见，将public设置为True
    public = models.BooleanField(default=False, verbose_name="是否公开")

    author = models.ForeignKey(
        OfficeUser,
        on_delete=models.CASCADE,
        related_name='inform',
        related_query_name='inform',
        verbose_name="作者"
    )

    # 序列化时使用，将部门转换为部门ID列表， 通过department_ids获取部门ID列表
    departments = models.ManyToManyField(
        OfficeDepartment,
        related_name='inform',
        related_query_name='inform',
        verbose_name="可见部门"
    )

    class Meta:
        """
        Inform模型的元数据配置
        
        - db_table: 指定数据库表名为'inform'
        - ordering: 默认按创建时间降序排列，最新的通知排在前面
        - verbose_name/verbose_name_plural: 模型的中文显示名称
        """
        db_table = "inform"
        ordering = ['-create_time']
        verbose_name = "通知"
        verbose_name_plural = "通知"

    def __str__(self):
        """
        返回通知的字符串表示形式
        """
        return f"{self.title} - {self.author.username}"


class InformRead(models.Model):
    """
    通知阅读模型
    
    记录用户对通知的阅读状态，每个用户对每个通知最多有一条阅读记录。
    
    字段说明：
    - inform: 关联的通知，与Inform模型建立外键关系
    - user: 阅读通知的用户，与OfficeUser模型建立外键关系
    - read_time: 阅读时间，自动设置为创建时的时间
    
    数据完整性保证：
    - 通过unique_together确保一个用户对一个通知只有一条阅读记录
    """
    inform = models.ForeignKey(
        Inform,
        on_delete=models.CASCADE,
        related_name='reads',
        related_query_name='reads',
        verbose_name="通知"
    )

    user = models.ForeignKey(
        OfficeUser,
        on_delete=models.CASCADE,
        related_name='reads',
        related_query_name='reads',
        verbose_name="阅读用户"
    )

    read_time = models.DateTimeField(auto_now_add=True, verbose_name="阅读时间")

    class Meta:
        """
        InformRead模型的元数据配置
        
        - db_table: 指定数据库表名为'inform_read'
        - verbose_name/verbose_name_plural: 模型的中文显示名称
        - unique_together: 确保每个用户对每个通知只有一条阅读记录
        """
        db_table = "inform_read"
        verbose_name = "通知阅读"
        verbose_name_plural = "通知阅读"
        unique_together = ('inform', 'user')

    def __str__(self):
        """
        返回阅读记录的字符串表示形式
        """
        return f"{self.user.username} 阅读了 {self.inform.title}"