from rest_framework import serializers
from django.core.validators import FileExtensionValidator

class ImgSerializer(serializers.Serializer):
    """图片上传序列化器"""
    img = serializers.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        error_messages={
            'required': '请上传图片',
            'invalid_image': '仅支持jpg、jpeg、png、gif格式',
        }
    )
    @staticmethod
    def validate_img(image):
        """这里要对图片进行验证"""
        if image.size > 1024 * 1024:
            raise serializers.ValidationError('图片大小不能超过1MB')
        return image
