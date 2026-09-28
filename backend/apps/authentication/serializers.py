from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.authentication.models import User


def serialize_user(user):
    return {
        'employee_id': user.employee_id,
        'name': user.name,
        'role': user.role,
        'team_id': user.team_id,
        'team_name': user.team.name if user.team_id else None,
    }


class EmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = serialize_user(self.user)
        return data


class CurrentUserSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField(read_only=True, allow_null=True)
    team_name = serializers.CharField(source='team.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ('employee_id', 'name', 'role', 'team_id', 'team_name')