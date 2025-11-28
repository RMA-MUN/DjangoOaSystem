from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.officeAuth.authentications import JWTAuthentication

class AuthenticatedView(APIView):
    """
    认证视图父类，用于处理需要认证的视图
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]