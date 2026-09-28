from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, employee_id, name, password=None, **extra_fields):
        if not employee_id:
            raise ValueError('사번(Employee ID)은 필수 항목입니다.')
        user = self.model(employee_id=employee_id, name=name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(employee_id, name, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin (관리자)'),
        ('MANAGER', 'Manager (매니저)'),
        ('EMPLOYEE', 'Employee (직원)'),
    )

    username = None
    first_name = None
    last_name = None
    email = models.EmailField(blank=True, null=True, verbose_name='이메일')

    employee_id = models.CharField(max_length=50, unique=True, verbose_name='사번')
    name = models.CharField(max_length=100, verbose_name='성명')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE', verbose_name='역할')
    team = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='소속팀'
    )

    objects = UserManager()

    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'
        ordering = ['employee_id']

    def __str__(self):
        team_name = self.team.name if self.team else '미배정'
        return f"{self.name} ({self.employee_id}) - [{self.role} / {team_name}]"
