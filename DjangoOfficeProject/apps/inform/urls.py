from rest_framework.routers import DefaultRouter
from apps.inform.views import InformViewSet

app_name = 'inform'

router = DefaultRouter()

router.register(r'inform', InformViewSet, basename='inform')

urlpatterns = [

] + router.urls