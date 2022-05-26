from datetime import timedelta
from uuid import uuid4
from PIL import Image as PImage
from django.conf import settings
from django.http import Http404
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import serializers
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
    exp_after = serializers.IntegerField(
        min_value=300,
        max_value=30000,
        required=False
    )
        
    def create(self, validated_data):
        owner = validated_data['owner']
        img = validated_data['img']
        exp_after = validated_data.get('exp_after', None)
        if exp_after and not owner.account_type.can_generate_exp_links:
            raise serializers.ValidationError({'exp_after': ['You dont\'t have permissions to create expiring links.']})
        exp_after = timezone.now() + timedelta(seconds=exp_after) if exp_after else None
        image = Image(owner=owner, img=img, exp_after=exp_after)
        image.full_clean()
        image.save()
        return image


class ImageDetailSerializer(serializers.Serializer):
    size = serializers.IntegerField(min_value=0, required=False)

    def __get_image_object(self, filename):
        try:
            return Image.objects.get(img=filename)
        except Image.DoesNotExist:
            raise Http404('Image doesn\'t exist')
    
    def __check_size_exist(self, image, size):
        try:
            Size.objects.get(
                account_type=image.owner.account_type,
                height=size
            )
        except Size.DoesNotExist:
            raise Http404('Image doesn\'t exist')

    def __check_expired_permissions(self, image, user):
        if image.exp_after is None \
            or image.exp_after >= timezone.now() \
                or (not user.is_anonymous and image.owner == user):
            return True
        raise Http404('Link expired')

    def validate_size(self, value):
        """
        Check if there is empty `size` parameter in query.
        """
        if 'size' in self.initial_data.keys() and not value:
            raise serializers.ValidationError({'size': ['Empty size query.']})
        return value

    def create(self, filename, user):
        """
        Create response image.
        """
        image_record = self.__get_image_object(filename)
        size = int(self.initial_data['size']) if self.initial_data else 0
        self.__check_size_exist(
            image_record, size
        )
        self.__check_expired_permissions(image_record, user)
        with PImage.open(image_record.img) as img:
            response_img = img
            file_format = response_img.format
            if size:
                widht, height = response_img.size
                aspect_ratio = widht / height
                new_width = int(aspect_ratio * size)
                response_img = response_img.resize((new_width, size))
            return response_img.copy(), file_format