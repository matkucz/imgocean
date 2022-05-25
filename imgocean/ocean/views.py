from django.http import Http404, FileResponse, HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .const import EXTENSION_MAPPER
from .models import Image, Size
from .serializers import (
    ImageDetailSerializer, ImageUploadSerializer, SignupSerializer
)

class SignupView(APIView):
    """
    API endpoint that allows to create users accounts.
    """
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def __get_image_urls(self, image, user):
        sizes = Size.objects.filter(account_type=user.account_type)
        urls = {}
        for size in sizes:
            link = f"/api/images/{image.name}"
            if size.height != 0:
                urls[f'th_{size.height}_px'] = f"{link}?size={size.height}"
            else:
                urls[f'original'] = link
        return urls


    def get(self, request, format=None):
        images = Image.objects.filter(owner=request.user)
        sizes = Size.objects.filter(account_type=request.user.account_type)
        images_list = [
            self.__get_image_urls(image, request.user)
            for image in images
        ]   
        return Response(images_list, status=status.HTTP_200_OK)
        
    def post(self, request, format=None):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.save(owner=request.user)
            images = self.__get_image_urls(image, request.user)
            return Response(images, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ImageDetailView(APIView):    
    def get(self, request, filename, format=None):
        query_serializer = ImageDetailSerializer(data=request.query_params)
        if query_serializer.is_valid():
            query_serializer.validate_size(query_serializer.data)
            response_img, file_format = query_serializer.create(filename)
            response = HttpResponse(content_type=EXTENSION_MAPPER[file_format.lower()])
            response_img.save(response, file_format)  
            return response
        return Response(query_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
