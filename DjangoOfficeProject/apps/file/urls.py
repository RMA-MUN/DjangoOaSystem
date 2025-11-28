from django.urls import path
from . import views

# http://127.0.0.1:8000/media/img/aqb9AbgYoDxbGyzrpvduWz.jpg
# 访问上传的图片

urlpatterns = [
    path('upload/', views.UploadAPIView.as_view(), name='upload'),
]

