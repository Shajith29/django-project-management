from django.utils import timezone
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from projects.models import Project,ProjectMembership
from projects.permissions import can_edit_taks, is_project_member,can_toggle_task,can_assign_task,can_transfer_ownership
from tasks.forms import TaskForm,AssignTaskForm
from tasks.models import Task
from django.http import HttpResponseBadRequest,HttpResponseForbidden
from django.core.paginator import Paginator
# Create your views here.

@login_required
def create_task(request,project_id):
    project = get_object_or_404(Project,pk=project_id)

    if not (
        project.owner == request.user or 
        project.members.filter(pk=request.user.pk).exists()
    ):
        return HttpResponseForbidden
    
    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid()  :
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect("list_projects")

    else:
        form = TaskForm()

    return render(request,"create_task.html",{"form": form,"project": project})


@login_required

def list_tasks(request,project_id):

    project = get_object_or_404(Project,pk=project_id)

    if not (request.user == project.owner or project.members.filter(pk=request.user.pk).exists()):
        return HttpResponseForbidden
    
    status = request.GET.get("status","pending")
    order = request.GET.get("order","newest")

    ordering = "-created_at"

    if(order == 'oldest'):
        ordering = "created_at"


    
    base_qs = Task.objects.filter(project=project).order_by(ordering)

    total_count = base_qs.count()
 
    pending_count = base_qs.filter(is_completed=False).count()
    completed_count = base_qs.filter(is_completed=True).count()

    tasks = base_qs
    
    if status == "pending":
        tasks = base_qs.filter(is_completed=False)
    elif status == "completed":
        tasks = base_qs.filter(is_completed=True)
    else:
        tasks = base_qs
    

    paginator = Paginator(tasks,3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    


    context = {
        "tasks" : page_obj,
        "project": project,
        "status":status,
        "total_count":total_count,
        "completed_count":completed_count,
        "pending_count":pending_count,
        "page_obj": page_obj,
        "order":order,
    }

    return render(request,"list_task.html",context)


@login_required
def edit_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id)

    project = task.project

    if not (
        request.user == project.owner or project.members.filter(pk=request.user.pk).exists()
    ):
        return HttpResponseForbidden
    
    if request.method == "POST":
        form = TaskForm(request.POST,instance=task)

        if form.is_valid():
            form.save()
            return redirect('list_tasks',project_id=project.pk)

    else:
        form = TaskForm(instance=task)

    return render(
        request,
        "edit_task.html",
        {
            "form" : form,
            "task":task,
            "project":project
        }

        )

@login_required
def complete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id)
    project = task.project

    if not can_toggle_task(request.user,task):
        raise PermissionDenied
    

    if task.is_completed:
        return HttpResponseBadRequest("The Task is Already Completed")
    
    task.is_completed = True
    task.completed_by =  request.user
    task.completed_at = timezone.now()
    task.save()

    return redirect("list_tasks",project_id=project.pk)


@login_required
def assign_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id)
  

    project = task.project


    if request.user != project.owner:
        return HttpResponseForbidden()
    
    if request.method == "POST":
        form = AssignTaskForm(request.POST,instance=task,project=project)
        if form.is_valid():
            form.save()
            return redirect('list_tasks',project_id=project.pk)
    else:
        form = AssignTaskForm(instance=task,project=project)

    return render(
        request,
        "assign_task.html",
        {
            "form": form,
            "task":task,
            "project":project
        }
    )


@login_required
def delete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id)
    print(task)

    project = task.project

    if not request.user == project.owner:
        return HttpResponseForbidden()
    
    if request.method == "POST":
        task.delete()
        
    return redirect("list_tasks",project_id=project.pk)

