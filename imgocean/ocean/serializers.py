from uuid import uuid4
from PIL import Image as PImage
from django.conf import settings
from django.http import Http404
from rest_framework import serializers
from .const import CONTENT_TYPE_MAPPER
from .models import Image, User, Size


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

    def __generate_filename(self, content_type:str) -> str:
        file_extension = CONTENT_TYPE_MAPPER[content_type]
        return f'{uuid4()}.{file_extension}'
    
    def __save_image(self, img, filename):        
        try:
            with open(settings.IMAGE_ROOT / '' / filename, 'wb') as file:
                file.write(img.getbuffer())
        except FileNotFoundError:
            pass
        
    def create(self, validated_data):
        owner = validated_data['owner']
        img = getattr(validated_data['img'], 'file')
        content_type = getattr(validated_data['img'], 'content_type')
        filename = self.__generate_filename(content_type)
        self.__save_image(img, filename)
        return Image.objects.create(owner=owner, name=filename)


class ImageDetailSerializer(serializers.Serializer):
    size = serializers.IntegerField(min_value=0, required=False, allow_null=False)

    def __get_image_object(self, filename):
        try:
            return Image.objects.get(name=filename)
        except Image.DoesNotExist:
            raise Http404
    
    def __check_size_exist(self, image, size):
        try:
            Size.objects.get(
                account_type=image.owner.account_type,
                height=size
            )
        except Size.DoesNotExist:
            raise Http404
    
    def validate_size(self, value):
        """
        Check if there is empty `size` parameter in query.
        """
        if 'size' in self.initial_data.keys() and not value:
            raise serializers.ValidationError({'size': ['Empty size query.']})
        return value

    def create(self, filename):
        """
        Create response image.
        """
        image_record = self.__get_image_object(filename)
        size = int(self.initial_data['size']) if self.initial_data else 0
        self.__check_size_exist(
            image_record, size
        )
        with PImage.open(settings.IMAGE_ROOT / '' / filename) as img:
            response_img = img
            file_format = response_img.format
            if size:
                widht, height = response_img.size
                aspect_ratio = widht / height
                new_width = int(aspect_ratio * size)
                response_img = response_img.resize((new_width, size))
            return response_img.copy(), file_format