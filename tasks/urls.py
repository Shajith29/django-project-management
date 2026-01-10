from  django.urls import path
from . import views

urlpatterns = [
     #Create Task

    path('projects/<int:project_id>/tasks/create/',views.TaskCreateView.as_view(),name="create_task"),

    #list Task
    path('project/<int:project_id>/tasks/',views.TaskListView.as_view(),name = "list_tasks"),

    #Edit Task

    path('<int:pk>/edit/',views.TaskUpdateView.as_view(),name="edit_task"),

    #Toggle Task Completion

    path('<int:task_id>/complete/',views.complete_task,name="complete_task"),

    #Assign task

    path('<int:task_id>/assign/',views.assign_task,name = "assign_task"),

    #Delete Task
    path("<int:pk>/delete",views.TaskDeleteView.as_view(),name= "delete_task")

    


]