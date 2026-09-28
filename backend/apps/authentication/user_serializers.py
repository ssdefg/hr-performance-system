from rest_framework import serializers

from apps.authentication.models import User
from apps.organizations.models import Team


class ManagedUserSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField()
    team_id = serializers.PrimaryKeyRelatedField(
        source='team',
        queryset=Team.objects.all(),
        required=False,
        allow_null=True,
    )
    team_name = serializers.CharField(source='team.name', read_only=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, min_length=4)

    class Meta:
        model = User
        fields = ('id', 'employee_id', 'name', 'password', 'role', 'team_id', 'team_name', 'is_active')
        read_only_fields = ('id',)

    def validate_employee_id(self, value):
        queryset = User.objects.filter(employee_id=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('이미 사용 중인 사번입니다.')
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': '초기 비밀번호를 입력해 주세요.'})
        role = attrs.get('role', getattr(self.instance, 'role', None))
        team = attrs.get('team', getattr(self.instance, 'team', None))
        if self.instance and self.instance.role == 'MANAGER' and role != 'MANAGER':
            if Team.objects.filter(manager=self.instance).exists():
                raise serializers.ValidationError({'role': '담당 팀을 해제한 뒤 역할을 변경할 수 있습니다.'})
        if role == 'MANAGER' and team:
            if team.manager_id and team.manager_id != getattr(self.instance, 'pk', None):
                raise serializers.ValidationError({'team_id': '이미 다른 매니저가 담당 중인 팀입니다.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if user.role == 'MANAGER' and user.team_id:
            user.team.manager = user
            user.team.save(update_fields=['manager'])
        return user

    def update(self, instance, validated_data):
        previous_team = instance.team
        password = validated_data.pop('password', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        if previous_team and previous_team.manager_id == instance.pk and (
            instance.role != 'MANAGER' or previous_team.pk != instance.team_id
        ):
            previous_team.manager = None
            previous_team.save(update_fields=['manager'])
        if instance.role == 'MANAGER' and instance.team_id:
            instance.team.manager = instance
            instance.team.save(update_fields=['manager'])
        elif instance.role != 'MANAGER' and instance.team_id:
            Team.objects.filter(manager=instance).update(manager=None)
        return instance