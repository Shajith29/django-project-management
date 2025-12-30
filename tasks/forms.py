from django import forms
from .models import Task
from django.contrib.auth.models import User
from django.db.models import Q

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title"]



class AssignTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["assigned_to"]

    
    def __init__(self,*args,**kwargs):
        project = kwargs.pop("project",None)

        if project is None:
            raise ValueError("AssignTaskForm requires a project")
       

        super().__init__(*args,**kwargs)

        self.fields["assigned_to"].queryset = User.objects.filter(
            Q(project_memberships__project=project) | 
            Q(pk=project.owner.pk)
        ).distinct()