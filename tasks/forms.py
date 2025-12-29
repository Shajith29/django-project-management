from django import forms
from .models import Task
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title"]



class AssignTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["assigned_to"]

    
    def _init__(self,*args,**kwargs):
        project = kwargs.pop()

        super.__init__(*args,**kwargs)

        self.fields["assigned_to"].querySet = (
                User.objects.filter(
                    project_memberships__project=project
                ) | 
                User.objects.filter(
                    pk=project.owner
                )
        ).distinct()