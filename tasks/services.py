from django.db.models import Q

def get_tasks_preferences(request):
    VALID_STATUS = ["all","completed","pending"]
    VALID_ORDERING = ["newest","oldest"]

    status = request.GET.get("status")
    order = request.GET.get("order")

    if status in VALID_STATUS:
        request.session["tasks_status"] = status

    if order in VALID_ORDERING:
        request.session["tasks_order"] = order
    
    status = request.session.get("tasks_status","pending")
    order = request.session.get("tasks_order","newest")

    return status,order

def get_ordering(status):
    return "created_at" if status == "oldest" else "-created_at"


def filter_tasks(base_qs,status):
    if status == "pending":
        return base_qs.filter(is_completed=False)
    elif status == "completed":
        return base_qs.filter(is_completed=True)
    else:
        return base_qs
    

def search_tasks(queryset,search_query):
    if not search_query:
        return queryset
    
    return queryset.filter(
        Q(title__icontains=search_query) | 
        Q(assigned_to__username__icontains=search_query)
    )

