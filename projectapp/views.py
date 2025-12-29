

from django.shortcuts import redirect


def home(request):
    if request.user.is_authenticated:
       return  redirect("list_projects")
    return redirect("login.html")