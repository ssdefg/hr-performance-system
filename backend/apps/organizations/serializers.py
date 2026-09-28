from rest_framework import serializers

from apps.authentication.models import User
from apps.organizations.models import Team


class TeamSerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(
        source='manager',
        queryset=User.objects.filter(role='MANAGER'),
        required=False,
        allow_null=True,
    )
    manager_name = serializers.CharField(source='manager.name', read_only=True, allow_null=True)
    member_count = serializers.IntegerField(source='members.count', read_only=True)

    class Meta:
        model = Team
        fields = ('id', 'name', 'manager_id', 'manager_name', 'member_count', 'bonus_score', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_bonus_score(self, value):
        if not 0 <= value <= 10:
            raise serializers.ValidationError('팀 보너스는 0~10점 범위여야 합니다.')
        return value

    def validate(self, attrs):
        manager = attrs.get('manager', getattr(self.instance, 'manager', None))
        if manager and Team.objects.filter(manager=manager).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError({'manager_id': '매니저는 한 팀만 담당할 수 있습니다.'})
        return attrs

    def create(self, validated_data):
        team = super().create(validated_data)
        self._sync_manager_team(team, None)
        return team

    def update(self, instance, validated_data):
        previous_manager = instance.manager
        team = super().update(instance, validated_data)
        self._sync_manager_team(team, previous_manager)
        return team

    @staticmethod
    def _sync_manager_team(team, previous_manager):
        if previous_manager and previous_manager.team_id == team.pk and previous_manager != team.manager:
            previous_manager.team = None
            previous_manager.save(update_fields=['team'])
        if team.manager and team.manager.team_id != team.pk:
            old_team = team.manager.team
            if old_team and old_team.manager_id == team.manager_id:
                old_team.manager = None
                old_team.save(update_fields=['manager'])
            team.manager.team = team
            team.manager.save(update_fields=['team'])