from rest_framework import serializers

from apps.evaluations.models import EvaluationCriteria, EvaluationItemScore, EvaluationReview


class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriteria
        fields = ('id', 'name', 'description', 'weight', 'order', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_weight(self, value):
        if not 1 <= value <= 100:
            raise serializers.ValidationError('가중치는 1~100 사이여야 합니다.')
        return value


class EvaluationItemScoreSerializer(serializers.ModelSerializer):
    criteria_id = serializers.IntegerField(source='criteria.id', read_only=True)
    name = serializers.CharField(source='criteria.name', read_only=True)
    description = serializers.CharField(source='criteria.description', read_only=True)
    weight = serializers.IntegerField(source='criteria.weight', read_only=True)
    earned_score = serializers.SerializerMethodField()

    class Meta:
        model = EvaluationItemScore
        fields = ('criteria_id', 'name', 'description', 'weight', 'score', 'earned_score')

    def get_earned_score(self, obj):
        return round(obj.score / 5 * obj.criteria.weight, 2)


class EvaluationReviewSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    team_name = serializers.CharField(source='employee.team.name', read_only=True, allow_null=True)
    scores = EvaluationItemScoreSerializer(many=True, read_only=True)

    class Meta:
        model = EvaluationReview
        fields = (
            'id', 'employee_id', 'employee_name', 'team_name', 'status', 'scores',
            'raw_score', 'final_score', 'is_capped', 'submitted_at', 'updated_at',
        )


class ScoreInputSerializer(serializers.Serializer):
    criteria_id = serializers.IntegerField(min_value=1)
    score = serializers.IntegerField(min_value=1, max_value=5)


class ReviewScoresInputSerializer(serializers.Serializer):
    scores = ScoreInputSerializer(many=True)

    def validate_scores(self, scores):
        criteria_ids = [item['criteria_id'] for item in scores]
        if len(criteria_ids) != len(set(criteria_ids)):
            raise serializers.ValidationError('평가 항목은 중복 입력할 수 없습니다.')
        criteria = EvaluationCriteria.objects.filter(id__in=criteria_ids, is_active=True)
        if criteria.count() != len(criteria_ids):
            raise serializers.ValidationError('유효하지 않거나 비활성화된 평가 항목이 포함되어 있습니다.')
        return scores