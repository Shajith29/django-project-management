from django.urls import path
from . import views


urlpatterns =[

    #Create Project

    path("create/",views.create_project,name="create_project"),

    #list project

    path("",views.list_projects,name= "list_projects"),
    #Delete Project
    path('<int:project_id>/delete',views.delete_project,name='delete_project'),

    #Add Member

    path('<int:project_id>/members/add/<int:user_id>',views.add_project_member,name="add_project_member"),
    path('<int:project_id>/members/remove/<int:user_id>',views.remove_project_member,name="remove_project_member"),

    #Transfer Ownership
    #projects/1/tansfer-ownership/2

    path('<int:project_id>/transfer-ownership/<int:user_id>',views.transfer_ownership,name="transfer_project_ownership")
]