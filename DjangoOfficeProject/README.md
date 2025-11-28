# DjangoOfficeProject - 办公自动化系统后端

这是一个基于Django开发的办公自动化系统后端，提供用户认证、考勤管理、员工管理、文件管理和通知管理等功能。

## 技术栈

- **后端框架**：Django 5.2.6 + Django REST Framework
- **数据库**：MySQL
- **缓存**：Redis
- **异步任务**：Celery
- **认证机制**：JWT (JSON Web Token)
- **跨域支持**：CORS
- **邮件服务**：SMTP (QQ邮箱)

## 功能模块

1. **用户认证系统 (officeAuth)**
    - 用户注册、登录、登出
    - JWT令牌管理
    - 用户信息管理
    - 部门管理

2. **考勤管理系统 (officeAttendance)**
    - 请假申请
    - 审批流程
    - 考勤记录查询

3. **员工管理系统 (staff)**
    - 员工信息管理
    - 批量数据导出
    - 异步邮件通知

4. **文件管理系统 (file)**
    - 文件上传下载
    - 文件分类管理

5. **通知系统 (inform)**
    - 通知发布
    - 部门通知可见性控制
    - 通知阅读状态跟踪

6. **首页功能 (home)**
    - 最新通知展示
    - 最新考勤记录
    - 部门人员统计

## 项目结构

```
DjangoOfficeProject/
├── DjangoOfficeProject/         # 项目主配置目录
│   ├── __init__.py              # 初始化文件，包含Celery应用初始化
│   ├── asgi.py                  # ASGI配置文件
│   ├── celery.py                # Celery配置文件
│   ├── settings.py              # Django主配置文件
│   ├── urls.py                  # 主URL路由配置
│   └── wsgi.py                  # WSGI配置文件
├── apps/                        # 应用模块目录
│   ├── file/                    # 文件管理模块
│   │   ├── models.py            # 文件管理数据模型
│   │   ├── serializers.py       # 文件管理序列化器
│   │   ├── urls.py              # 文件管理URL路由
│   │   └── views.py             # 文件管理视图
│   ├── home/                    # 首页功能模块
│   │   ├── urls.py              # 首页URL路由
│   │   └── views.py             # 首页视图
│   ├── inform/                  # 通知管理模块
│   │   ├── models.py            # 通知管理数据模型
│   │   ├── serializers.py       # 通知管理序列化器
│   │   ├── urls.py              # 通知管理URL路由
│   │   └── views.py             # 通知管理视图
│   ├── officeAttendance/        # 考勤管理模块
│   │   ├── models.py            # 考勤管理数据模型
│   │   ├── serializer.py        # 考勤管理序列化器
│   │   ├── urls.py              # 考勤管理URL路由
│   │   ├── utils.py             # 考勤管理工具函数
│   │   └── views.py             # 考勤管理视图
│   ├── officeAuth/              # 用户认证模块
│   │   ├── authentications.py   # 认证相关功能
│   │   ├── fatherClass.py       # 父类定义
│   │   ├── models.py            # 用户认证数据模型
│   │   ├── serializers.py       # 用户认证序列化器
│   │   ├── urls.py              # 用户认证URL路由
│   │   └── views.py             # 用户认证视图
│   └── staff/                   # 员工管理模块
│       ├── models.py            # 员工管理数据模型
│       ├── serializer.py        # 员工管理序列化器
│       ├── tasks.py             # 异步任务定义
│       ├── urls.py              # 员工管理URL路由
│       └── views.py             # 员工管理视图
├── media/                       # 媒体文件存储目录
│   ├── headicon/                # 头像文件
│   └── img/                     # 图片文件
├── templates/                   # HTML模板目录
│   └── activation.html          # 邮件激活模板
├── logs.log                     # 日志文件
├── manage.py                    # Django管理脚本
└── README.md                    # 项目说明文档
```

### 目录说明

- **DjangoOfficeProject/**：项目主配置目录，包含Django和Celery的核心配置
- **apps/**：存放所有业务功能模块的目录，每个子目录对应一个功能模块
- **media/**：用于存储用户上传的媒体文件，如头像和图片
- **templates/**：存放HTML模板，主要用于邮件发送等场景
- **manage.py**：Django项目的命令行工具，用于运行服务器、执行数据库迁移等

### 模块职责表

| 模块名称 | 主要职责 | 文件位置 | 核心文件 |
|---------|---------|---------|--------|
| 用户认证 | 用户登录注册、JWT认证管理 | apps/officeAuth/ | apps/officeAuth/views.py |
| 考勤管理 | 请假申请、审批流程、考勤记录 | apps/officeAttendance/ | apps/officeAttendance/views.py |
| 员工管理 | 员工信息管理、异步邮件通知 | apps/staff/ | apps/staff/views.py |
| 文件管理 | 文件上传下载、分类管理 | apps/file/ | apps/file/views.py |
| 通知系统 | 通知发布、阅读状态跟踪 | apps/inform/ | apps/inform/views.py |
| 首页功能 | 数据统计、信息展示 | apps/home/ | apps/home/views.py |


## 快速开始

### 1. 克隆项目

```bash
git clone https://your-repository-url/DjangoOfficeProject.git
cd DjangoOfficeProject
```

### 2. 创建并激活虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 首先生成requirements.txt文件
pip freeze > requirements.txt

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置数据库

确保MySQL已安装并运行，然后在`DjangoOfficeProject/settings.py`中配置数据库连接信息：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_oa',  # 数据库名
        'USER': 'root',       # 用户名
        'PASSWORD': 'your_password',  # 密码
        'HOST': 'localhost',  # 主机
        'PORT': '3306',       # 端口
    }
}
```

### 5. 配置邮箱服务（用于用户激活）

在`DjangoOfficeProject/settings.py`中配置邮件服务信息，以启用用户注册后的邮箱激活功能：

```python
# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # QQ邮箱SMTP服务器
EMAIL_PORT = 587  # SMTP端口
EMAIL_USE_TLS = True  # 使用TLS加密
EMAIL_HOST_USER = 'your_email@qq.com'  # 发送邮件的邮箱地址
EMAIL_HOST_PASSWORD = 'your_email_password'  # 邮箱授权码（非登录密码）
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # 默认发件人

# 激活邮件设置
ACTIVATION_EXPIRE_DAYS = 7  # 激活链接有效期（天）
```

**重要提示**：
- 如果使用QQ邮箱，需要在QQ邮箱设置中开启SMTP服务并获取授权码
- 如果使用其他邮箱服务（如163、Gmail等），请相应修改SMTP服务器地址和端口
- 确保邮箱密码或授权码设置正确，否则邮件发送会失败
- 邮件模板位于`templates/activation.html`，可以根据需要自定义样式

### 6. 初始化数据库

```bash
python manage.py migrate
```

### 7. 启动Redis服务

确保Redis已安装并运行。Windows用户可以通过WSL或Redis官方Windows版本安装，macOS/Linux用户可以使用系统包管理器安装。

启动Redis服务：

```bash
# Windows (通过Redis CLI)
redis-server.exe

# macOS/Linux
redis-server
```

### 8. 启动Celery Worker

在项目根目录下打开新的终端窗口，运行：

```bash
# Windows
celery -A DjangoOfficeProject worker --pool=solo -l info

# macOS/Linux
celery -A DjangoOfficeProject worker -l info
```

### 9. 启动Django开发服务器

```bash
python manage.py runserver
```

### 10. 访问系统

系统将运行在 http://127.0.0.1:8000

## API文档

系统各模块的API端点：

- 用户认证：`/officeAuth/`
- 考勤管理：`/Attendance/`
- 员工管理：`/staff/`
- 文件管理：`/file/`
- 通知管理：`/inform/`
- 首页功能：`/home/`

## 开发说明

### 环境变量

系统使用以下环境配置（在settings.py中定义）：

- 数据库连接信息
- Redis连接信息
- 邮件服务配置
- Celery配置

### 异步任务

系统使用Celery处理异步任务，主要包括邮件发送等耗时操作。任务定义在各应用的tasks.py文件中。

### 认证机制

系统使用JWT进行身份认证，所有需要认证的API请求需要在请求头中包含有效的JWT令牌。

## 部署说明

在生产环境部署时，建议：

1. 使用Gunicorn或uWSGI作为WSGI服务器
2. 使用Nginx作为反向代理
3. 配置HTTPS
4. 设置更安全的密码和密钥
5. 关闭DEBUG模式
6. 配置适当的ALLOWED_HOSTS

## 项目亮点

1. **异步任务处理**：采用Celery实现异步邮件发送和耗时操作，提高系统响应速度
2. **完善的权限控制**：基于JWT的认证机制，确保API访问安全
3. **模块化设计**：清晰的功能模块划分，便于维护和扩展
4. **多模块协同**：考勤、员工、通知等模块紧密集成，实现办公流程自动化
5. **文件管理**：支持文件上传下载和分类管理，满足办公需求

## 常见问题解答

### 1. 邮件发送失败怎么办？

- 检查`settings.py`中的邮件配置是否正确
- 确保SMTP服务可用且未被防火墙阻止
- 查看日志文件`logs.log`中的错误信息

### 2. Celery任务不执行怎么办？

- 确认Redis服务正在运行
- 检查Celery Worker是否正常启动
- 查看Celery日志中的错误信息
- 验证任务是否正确注册

### 3. 图片上传失败或无法访问？

- 确认`media`目录权限设置正确
- 检查`settings.py`中的`MEDIA_URL`和`MEDIA_ROOT`配置
- 确保开发服务器正确处理媒体文件请求

## 注意事项

1. 开发环境中，确保DEBUG模式设置为True，便于调试
2. 生产环境部署时，务必关闭DEBUG模式并设置正确的ALLOWED_HOSTS
3. 定期备份数据库和媒体文件
4. 对于生产环境，建议配置HTTPS确保数据传输安全
5. 合理配置Redis内存上限，避免内存溢出

## 许可证

[MIT License](LICENSE)