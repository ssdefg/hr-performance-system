from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.authentication.views import CurrentUserView
from apps.authentication.serializers import EmployeeTokenObtainPairSerializer

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(serializer_class=EmployeeTokenObtainPairSerializer), name='auth-login'),
    path('me/', CurrentUserView.as_view(), name='auth-me'),
]
