from rest_framework import filters
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import BasePermission
from rest_framework.viewsets import ModelViewSet

from apps.authentication.models import User
from apps.authentication.serializers import CurrentUserSerializer
from apps.authentication.user_serializers import ManagedUserSerializer


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')


class CurrentUserView(RetrieveAPIView):
    serializer_class = CurrentUserSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(ModelViewSet):
    queryset = User.objects.select_related('team').all()
    serializer_class = ManagedUserSerializer
    permission_classes = (IsAdminRole,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('employee_id', 'name')
    ordering_fields = ('employee_id', 'name', 'role')
    ordering = ('employee_id',)

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        team_id = self.request.query_params.get('team_id')
        if role:
            queryset = queryset.filter(role=role)
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        return queryset