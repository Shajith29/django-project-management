from django.utils import timezone
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from projects.models import Project,ProjectMembership
from projects.permissions import can_edit_taks, is_project_member,can_toggle_task,can_assign_task,can_transfer_ownership
from tasks.models import Task
from django.http import HttpResponseBadRequest
# Create your views here.

@login_required
def create_task(request,project_id):
    project = get_object_or_404(Project,pk=project_id)

    if not is_project_member(request.user,project):
        raise PermissionDenied
    
    title = request.POST.get("title")

    if not title:
        raise ValueError("Task Title is Required")
    
    Task.objects.create(
        title=title,
        project=project
    )

    return redirect("/")


@login_required
def edit_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id)

    if not can_edit_taks(request.user,task):
        raise PermissionDenied
    
    new_title = request.POST.get("title")

    if not new_title:
        raise ValueError("Title is Required")
    
    task.title = new_title
    task.save()

    return redirect('/')

@login_required
def complete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id)

    if not can_toggle_task(request.user,task):
        raise PermissionDenied
    

    if task.is_completed:
        return HttpResponseBadRequest("The Task is Already Completed")
    
    task.is_completed = True
    task.completed_by =  request.user
    task.completed_at = timezone.now()
    task.save()

    return redirect("/")


@login_required
def assign_task(request,task_id,user_id):
    task = get_object_or_404(Task,pk=task_id)
    user =  get_object_or_404(User,pk=user_id)

    if not can_assign_task(request.user,task,user):
        raise PermissionDenied
    
    task.assigned_to = user
    task.save()

    return redirect("/")


    

