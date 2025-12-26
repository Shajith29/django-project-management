from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_projects"
    )

    members = models.ManyToManyField(
        User,
        through="ProjectMembership",
        related_name="projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class ProjectMembership(models.Model):
    MEMBER = "member"
    ROLE_CHOICES = [
        (MEMBER,"Member"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_memberships"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=MEMBER
    )

    joined_at =models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user","project"]

    def __str__(self):
        return f"{self.user} works in  ${self.project}"
    
