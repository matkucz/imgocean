from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ImageUploadView, SignupView, ImageDetailView
urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('images/', ImageUploadView.as_view()),
    path('images/<str:filename>', ImageDetailView.as_view()),
    
]