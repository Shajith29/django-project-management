from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect
from .models import Project,ProjectMembership
from tasks.models import Task
from django.contrib.auth.models import User
from .permissions import can_transfer_ownership, is_project_owner,is_project_member,can_edit_taks
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .forms import ProjectForm


# Create your views here.

@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect("list_projects")
    else:
        form = ProjectForm()

    return render(request,"create_project.html",{"form": form})


@login_required 
def list_projects(request):
    projects = Project.objects.filter(
        Q(owner = request.user) |
        Q(members__pk = request.user.pk)
    ).distinct()

    project_data = []

    for project in projects:
        can_create_task = (
            project.owner == request.user or 
            project.members.filter(pk=request.user.pk).exists()
        )

        project_data.append({
            "project" : project,
            "can_create_task": can_create_task
        })

    context = {
        "project_data": project_data
    }

    return render(request,"project_list.html",context)


@login_required
def delete_project(request,project_id):
    project = get_object_or_404(Project,id=project_id)

    if not is_project_owner(request.user,project):
        raise PermissionDenied
    
    project.delete()
    return redirect("/")


@login_required
def add_project_member(request,user_id,project_id):
    project = get_object_or_404(Project,pk=project_id)

    if not is_project_owner(request.user,project):
        raise PermissionDenied
    
    user = get_object_or_404(User,pk=user_id)

    if user == project.owner:
        raise PermissionDenied
    
    ProjectMembership.objects.create(
        project = project,
        user=user,
    )

    return redirect("/")

@login_required
def remove_project_member(request,project_id,user_id):
    project = get_object_or_404(Project,pk=project_id)

    if not is_project_member(request.user,project):
        raise PermissionDenied
    
    user = get_object_or_404(User,pk=user_id)

    if user == project.owner:
        raise PermissionDenied

    ProjectMembership.objects.filter(
        project=project,
        user=user
    ).delete()

    return redirect("/")


@login_required
def transfer_ownership(request,project_id,user_id):
    project = get_object_or_404(Project,pk=project_id)
    new_owner = get_object_or_404(User,pk=user_id)

    if not can_transfer_ownership(request.user,project,new_owner):
        raise PermissionDenied
    
    old_owner = project.owner

    project.owner = new_owner
    project.save()

    ProjectMembership.objects.filter(
        project=project,
        user=new_owner
    ).delete()

    ProjectMembership.objects.get_or_create(
        project=project,
        user=old_owner
    )

    return redirect("/")

    
    






