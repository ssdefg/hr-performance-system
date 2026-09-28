from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.evaluations.views import (
	EvaluationCriteriaViewSet,
	manager_review,
	my_review,
	save_draft,
	submit_review,
	team_members,
)

router = DefaultRouter()
router.register('criteria', EvaluationCriteriaViewSet, basename='criteria')

urlpatterns = [
	path('team-members/', team_members, name='evaluation-team-members'),
	path('reviews/<str:employee_id>/', manager_review, name='evaluation-manager-review'),
	path('reviews/<str:employee_id>/draft/', save_draft, name='evaluation-save-draft'),
	path('reviews/<str:employee_id>/submit/', submit_review, name='evaluation-submit'),
	path('my-review/', my_review, name='evaluation-my-review'),
	*router.urls,
]
