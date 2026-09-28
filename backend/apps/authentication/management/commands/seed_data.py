from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.organizations.models import Team
from apps.evaluations.models import EvaluationCriteria, EvaluationReview, EvaluationItemScore
from apps.evaluations.services import calculate_final_score, calculate_raw_score

class Command(BaseCommand):
    help = 'Seeds initial test users, teams, evaluation criteria, and sample review data.'

    def handle(self, *args, **options):
        User = get_user_model()
        self.stdout.write('--- Starting Data Seeding ---')

        # 1. Admin Account
        admin, created = User.objects.get_or_create(
            employee_id='ADMIN',
            defaults={
                'name': '관리자',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin.set_password('admin1234!')
        admin.role = 'ADMIN'
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        self.stdout.write(f"Admin account: ADMIN / admin1234! ({'created' if created else 'updated'})")

        # 2. Evaluation Criteria (50% / 30% / 20% = 100%)
        criteria_defs = [
            {'name': '직무 전문성 및 성과', 'description': '업무 수행 전문성 및 분기 목표 달성도', 'weight': 50, 'order': 1},
            {'name': '협업 및 커뮤니케이션', 'description': '팀워크, 부서 간 협업 및 소통 역량', 'weight': 30, 'order': 2},
            {'name': '도전 및 문제해결력', 'description': '문제 해결 태도 및 창의적 혁신 역량', 'weight': 20, 'order': 3},
        ]
        created_criteria = []
        for cdef in criteria_defs:
            crit, _ = EvaluationCriteria.objects.update_or_create(
                name=cdef['name'],
                defaults={
                    'description': cdef['description'],
                    'weight': cdef['weight'],
                    'order': cdef['order'],
                    'is_active': True,
                }
            )
            created_criteria.append(crit)
        self.stdout.write(f"Criteria: {len(created_criteria)} items created/verified (Total weight: 100%)")

        # 3. Managers
        m1, _ = User.objects.get_or_create(
            employee_id='M1',
            defaults={'name': '김개발', 'role': 'MANAGER'}
        )
        m1.set_password('test1234!')
        m1.role = 'MANAGER'
        m1.save()

        m2, _ = User.objects.get_or_create(
            employee_id='M2',
            defaults={'name': '최영업', 'role': 'MANAGER'}
        )
        m2.set_password('test1234!')
        m2.role = 'MANAGER'
        m2.save()

        # 4. Teams
        team_dev, _ = Team.objects.update_or_create(
            name='개발팀',
            defaults={'manager': m1, 'bonus_score': 5.0}
        )
        team_sales, _ = Team.objects.update_or_create(
            name='영업팀',
            defaults={'manager': m2, 'bonus_score': 0.0}
        )
        m1.team = team_dev
        m1.save(update_fields=['team'])
        m2.team = team_sales
        m2.save(update_fields=['team'])

        # 5. Employees
        employees_data = [
            ('E1', '이개발', team_dev),
            ('E2', '박개발', team_dev),
            ('E3', '정영업', team_sales),
            ('E4', '강영업', team_sales),
        ]
        created_emps = {}
        for emp_id, name, team in employees_data:
            emp, _ = User.objects.get_or_create(
                employee_id=emp_id,
                defaults={'name': name, 'role': 'EMPLOYEE', 'team': team}
            )
            emp.set_password('test1234!')
            emp.role = 'EMPLOYEE'
            emp.team = team
            emp.save()
            created_emps[emp_id] = emp

        # 6. Seed Sample Review for E1 (Submitted by M1)
        e1 = created_emps['E1']
        raw_score = calculate_raw_score([
            (4, 50), # 40.0
            (5, 30), # 30.0
            (3, 20), # 12.0
        ]) # total 82.0
        final_score, is_capped = calculate_final_score(raw_score, team_dev.bonus_score) # 82 + 5 = 87.0

        rev, _ = EvaluationReview.objects.update_or_create(
            employee=e1,
            evaluator=m1,
            defaults={
                'status': 'SUBMITTED',
                'raw_score': raw_score,
                'final_score': final_score,
                'is_capped': is_capped,
                'strengths': ['문제 해결력', '높은 책임감', '빠른 일정 준수'],
                'improvements': ['문서화 보완', '협업 확대'],
                'comment': '이번 분기 핵심 프로젝트를 성공적으로 완수해 주어 대단히 감사합니다.\n다음 분기에는 타 부서와의 협업 및 문서화 품질을 보완하면 더욱 뛰어난 성과(A등급 달성)를 이룰 수 있을 것으로 기대합니다.',
                'submitted_at': timezone.now(),
            }
        )

        scores_map = {1: 4, 2: 5, 3: 3}
        for crit in created_criteria:
            EvaluationItemScore.objects.update_or_create(
                review=rev,
                criteria=crit,
                defaults={'score': scores_map.get(crit.order, 4)}
            )

        self.stdout.write(self.style.SUCCESS('--- Seed Data Finished Successfully! ---'))

