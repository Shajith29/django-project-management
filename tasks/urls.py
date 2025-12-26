from  django.urls import path
from . import views

urlpatterns = [
     #Create Task

    path('<int:project_id>/task/create/',views.create_task,name="create_task"),

    #Edit Task

    path('<int:task_id>/edit/',views.edit_task,name="edit_task"),

    #Toggle Task Completion

    path('<int:task_id>/complete/',views.complete_task,name="complete_task"),

    #Assign task



    path('<int:task_id>/assign/<int:user_id>',views.assign_task,name = "assign_task")


]