from django.db import models

from projects.models import Project
from django.contrib.auth.models import User
from django.db.models import Q
# Create your models here.


class Task(models.Model):
    title = models.CharField(max_length=200)
    project = models.ForeignKey(
        Project,
        on_delete=models    .CASCADE,
    )

    is_completed = models.BooleanField(default=False)

    assigned_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    completed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="completed_tasks"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(is_completed=True,completed_by__isnull=False,completed_at__isnull=False)
                    |
                    Q(is_completed=False,completed_by__isnull=True,completed_at__isnull=True)
                ),
                name="task_completion_audit_consistency",
            ),
        ]

    

  

