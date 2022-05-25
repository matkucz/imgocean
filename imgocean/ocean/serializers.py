from uuid import uuid4
from django.conf import settings
from rest_framework import serializers
from .const import CONTENT_TYPE_MAPPER
from .models import Image, User


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'account_type',
        ]
        extra_kwargs = {
            'password': {
                'write_only': True
            },
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            password=validated_data['password'],
            account_type=validated_data['account_type']
        )
        return user


class ImageUploadSerializer(serializers.Serializer):
    img = serializers.ImageField(max_length=50, allow_empty_file=False)
    exp_after = serializers.IntegerField(min_value=300, max_value=30000)

    def _generate_filename(self, content_type:str) -> str:
        file_extension = CONTENT_TYPE_MAPPER[content_type]
        return f'{uuid4()}.{file_extension}'
    
    def _save_image(self, img, filename):        
        try:
            with open(settings.IMAGE_ROOT / '' / filename, 'wb') as file:
                file.write(img.getbuffer())
            return True
        except FileNotFoundError:
            return False
        
    def create(self, validated_data):
        owner = validated_data['owner']
        img = getattr(validated_data['img'], 'file')
        content_type = getattr(validated_data['img'], 'content_type')
        filename = self._generate_filename(content_type)
        self._save_image(img, filename)
        Image.objects.create(owner=owner, name=filename)
        return False