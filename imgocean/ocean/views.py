from django.http import Http404, FileResponse, HttpResponse
from django.conf import settings
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .const import EXTENSION_MAPPER
from .models import Image, Size
from .serializers import ImageUploadSerializer, SignupSerializer

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

    def get(self, request, format=None):
        images = Image.objects.filter(owner=request.user)
        sizes = Size.objects.filter(account_type=request.user.account_type)
        images_list = []
        for image in images:
            for size in sizes:
                link = f"/api/images/{image.name}"
                # original image have height 0
                if size.height != 0:
                    link = f"{link}?size={size.height}"
                images_list.append(link)
        return Response(images_list, status=status.HTTP_200_OK)
        
    def post(self, request, format=None):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response({"message": "ok"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ImageDetailView(APIView):
    # permission_classes = []

    def get_object(self, filename):
        try:
            return Image.objects.get(name=filename)
        except Image.DoesNotExist:
            raise Http404
    
    def get_size_object(self, image, size):
        try:
            Size.objects.get(
                account_type=image.owner.account_type,
                height=size
            )
        except Size.DoesNotExist:
            raise Http404
    
    def get(self, request, filename, format=None):
        image = self.get_object(filename)
        size = request.query_params.get('size')
        if size is None:
            size = 0
        size = int(size)
        self.get_size_object(
            image, size
        )
        with PILImage.open(settings.IMAGE_ROOT / '' / filename) as img:
            response_img = img
            file_format = response_img.format
            if size != 0:
                widht, height = response_img.size
                aspect_ratio = widht / height
                new_width = int(aspect_ratio * size)
                response_img = response_img.resize((new_width, size))
            response = HttpResponse(content_type=EXTENSION_MAPPER[file_format.lower()])
            response_img.save(response, file_format)
            return response
