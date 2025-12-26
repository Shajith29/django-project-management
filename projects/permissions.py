


def is_project_owner(user,project):
    return project.owner == user


def is_project_member(user,project):
    return project.members.filter(pk=user.pk).exists()

def can_edit_taks(user,task):
    return (task.project.owner == user) or (task.assigned_to == user)


def can_toggle_task(user,task):
    return (task.assigned_to == user or  user == task.project.owner)


def can_assign_task(user,task,assignee):
    if task.project.owner != user:
        return False
    
    return task.project.members.filter(pk=assignee.pk).exists()

def can_transfer_ownership(curr_user,project,new_owner):
    if project.owner != curr_user:
        return False
    
    return project.members.filter(pk=new_owner.pk).exists()

