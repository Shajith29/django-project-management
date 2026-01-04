from django.test import RequestFactory, TestCase
from django.urls import reverse

from projects.models import Project, ProjectMembership
from tasks.models import Task

from django.contrib.auth.models import User
from django.utils import timezone

from .services import (get_ordering,get_tasks_preferences,filter_tasks,search_tasks)

from tasks.models import Task

# Create your tests here.

class CreateTaskTest(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="pass123"
        )

        self.member = User.objects.create_user(
            username="member",
            password="pass123"
        )

        self.stranger = User.objects.create_user(
            username="stranger",
            password="pass123"
        )

        self.project = Project.objects.create(
            name="Test Project",
            owner = self.owner
        )

        ProjectMembership.objects.create(
            user=self.member,
            project=self.project
        )

        self.create_task_url = reverse('create_task',args=[self.project.pk])

        

    
    def test_member_can_create_task(self):
        self.client.login(username='member',password='pass123')

        response = self.client.post(self.create_task_url,{
            "title" : "My Task"
        })

        self.assertTrue(
            Task.objects.filter(
            project=self.project,
            title="My Task"
        ).exists()
        )

        self.assertEqual(response.status_code,302)

    
    def test_stranger_cannot_create_task(self):
        self.client.login(username='stranger',password="pass123")

        response = self.client.post(self.create_task_url,{
            "title" : "My Task"
        })

        self.assertFalse(
            Task.objects.filter(
                project=self.project,
                title="My Task",

            ).exists()
        )

        self.assertEqual(response.status_code,403)

    
    def test_anonymous_user_cannot_create_task(self):
        response = self.client.post(self.create_task_url,{
            'title': 'My Task'
        })

        self.assertFalse(
            Task.objects.filter(
                project=self.project,
                title='My Task',
            )
        )

        self.assertEqual(response.status_code,302)



class EditTaskTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="pass123"
        )

        self.member = User.objects.create_user(
            username="member",
            password="pass123",
        )

        self.other_member = User.objects.create_user(
            username="other-member",
            password="pass123",
        )

        self.stranger = User.objects.create_user(
            username="stranger",
            password="pass123",
        )

        self.project = Project.objects.create(
            name="Test Project",
            owner=self.owner
        )

        ProjectMembership.objects.create(
            user=self.member,
            project=self.project
        )

        ProjectMembership.objects.create(
            user=self.other_member,
            project=self.project
        )


        self.task = Task.objects.create(
            title = "New Task",
            project=self.project,
            assigned_to = self.member
        )

        self.edit_url = reverse('edit_task',args=[self.task.pk])    

    
    def test_owner_can_edit_task(self):
        self.client.login(username="owner",password="pass123")

        response = self.client.post(self.edit_url,{
            "title" : "New Title"
        })

        self.task.refresh_from_db()

        self.assertTrue(
            Task.objects.filter(
                project=self.project,
                title="New Title"
            ).exists()
        )

        self.assertEqual(response.status_code,302)

    def test_assinged_user_can_edit_task(self):
        self.client.login(username="member",password="pass123")

        response = self.client.post(self.edit_url,{
            "title" : "Member Edit",
        })

        self.task.refresh_from_db()

        self.assertEqual(self.task.title,"Member Edit")

        self.assertEqual(response.status_code,302)

    
    def test_non_assigned_member_cannot_edit(self):
        self.client.login(username='other-member',password="pass123")

        response = self.client.post(self.edit_url,{
            "title": "Other Edit"
        })

        self.task.refresh_from_db()

        self.assertNotEqual(self.task.title,"Other Edit")
        self.assertEqual(response.status_code,403)

    def test_stranger_cannot_edit(self):
        self.client.login(username="stranger",password="pass123")

        response = self.client.post(self.edit_url,{
            "title" : "Stranger Edit"
        })

        self.assertNotEqual(self.task.title,'Stranger Edit')
        self.assertEqual(response.status_code,403)


class CompleteTaskTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner",password="pass123")
        self.member = User.objects.create_user(username="member",password="pass123")
        self.other_member = User.objects.create_user(username="other_member",password="pass123")


        self.project = Project.objects.create(
            name="Test Project",
            owner=self.owner
        )

        ProjectMembership.objects.create(
            user=self.member,
            project=self.project
        )

        ProjectMembership.objects.create(
            user=self.other_member,
            project=self.project
        )

        self.task = Task.objects.create(
            title = "Test Task",
            project = self.project,
            assigned_to=self.member,
            is_completed = False

        )

        self.complete_url = reverse('complete_task',args=[self.task.pk])

    

    def test_assign_user_can_complete_task(self):
        self.client.login(username="member",password="pass123")

        response = self.client.post(self.complete_url)

        self.task.refresh_from_db()

        self.assertTrue(self.task.is_completed)
        self.assertEqual(response.status_code,302)

    
    def test_owner_can_complete_task(self):
        self.client.login(username="owner",password="pass123")

        response = self.client.post(self.complete_url)

        self.task.refresh_from_db()

        self.assertTrue(self.task.is_completed)
        self.assertEqual(response.status_code,302)

    def test_non_assigned_member_cannot_complete_task(self):
        self.client.login(username='other_member',password='pass123')

        response = self.client.post(self.complete_url)
        
        self.task.refresh_from_db()

        self.assertFalse(self.task.is_completed)
        self.assertEqual(response.status_code,403)

    
    def test_anonoymous_member_cannot_complete_task(self):
        response = self.client.post(self.complete_url)
        
        self.task.refresh_from_db()

        self.assertFalse(self.task.is_completed)
        self.assertEqual(response.status_code,302)

    
    def test_task_cannot_complete_twice(self):
        self.task.is_completed = True
        self.task.completed_by = self.member
        self.task.completed_at = timezone.now()
        self.task.save()

        self.client.login(username="member",password="pass123")

        response = self.client.post(self.complete_url)

        self.task.refresh_from_db()

        self.assertTrue(self.task.is_completed)
        self.assertEqual(response.status_code,400)

    def test_completion_records_audit_data(self):
        self.client.login(username="member",password="pass123")

        self.client.post(self.complete_url)

        self.task.refresh_from_db()

        self.assertTrue(self.task.is_completed)
        self.assertEqual(self.member,self.task.completed_by)
        self.assertIsNotNone(self.task.completed_at)

    def test_aduit_data_not_overwritten(self):
        self.task.is_completed = True
        self.task.completed_by  = self.member
        self.task.completed_at = timezone.now()
        self.task.save()


        self.client.login(username="owner",password="pass123")

        response = self.client.post(self.complete_url)

        self.task.refresh_from_db()

        self.assertEqual(response.status_code,400)
        self.assertEqual(self.task.completed_by,self.member)



class TestAssignTask(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner",password="pass123")
        self.member = User.objects.create_user(username="member",password="pass123")
        self.other = User.objects.create_user(username="other",password="pass123")

        self.project = Project.objects.create(
            name="Test Project",
            owner = self.owner
        )

        ProjectMembership.objects.create(
            project= self.project,
            user=self.member
        )

        self.task = Task.objects.create(
            title="Test Task",
            project = self.project,
            assigned_to = None
        )

        self.assign_url = reverse('assign_task',args=[self.task.pk])

    def test_owner_can_assign_task(self):
        self.client.login(username="owner",password="pass123")

        response = self.client.post(self.assign_url,{
            "assigned_to" : self.member.pk
        })

        self.task.refresh_from_db()

        self.assertEqual(self.task.assigned_to,self.member)
        self.assertEqual(response.status_code,302)

    def test_owner_cannot_assign_non_member(self):

        url = reverse("assign_task",args=[self.task.pk])

        self.client.login(username="owner",password="pass123")
        response = self.client.post(url,{
            "assigned_to" : self.other.pk
        })

        self.task.refresh_from_db()

        self.assertIsNone(self.task.assigned_to)
        self.assertEqual(response.status_code,200)

    def test_member_cannot_assign_task(self):
        self.client.login(username="member",password="pass123")

        response = self.client.post(self.assign_url)

        self.task.refresh_from_db()

        self.assertIsNone(self.task.assigned_to)
        self.assertEqual(response.status_code,403)

    def test_anonymous_user_cannot_assign_task(self):
        response = self.client.post(self.assign_url)

        self.task.refresh_from_db()
        self.assertIsNone(self.task.assigned_to)
        self.assertEqual(response.status_code,302)


class GetOrderingTest(TestCase):

    def test_newest_returns_desc(self):
        self.assertEqual(get_ordering('newest'),'-created_at')

    def test_oldest_return_asc(self):
        self.assertEqual(get_ordering("oldest"),"created_at")

    def test_invalid_return_desc(self):
        self.assertEqual(get_ordering("invalid"),"-created_at")

class GetTaskPreferenceTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    
    def test_defaults_when_no_session_no_query(self):
        request = self.factory.get("/tasks")

        request.session = {}

        status,order = get_tasks_preferences(request)

        self.assertEqual(status,"pending")
        self.assertEqual(order,"newest")

    def test_url_params_override_default(self):
        request = self.factory.get("tasks/?status=completed&order=oldest")

        request.session = {}

        status,order = get_tasks_preferences(request)

        self.assertEqual(status,"completed")
        self.assertEqual(order,"oldest")
        self.assertEqual(request.session["tasks_status"],"completed")
        self.assertEqual(request.session["tasks_order"],"oldest")

    
    def test_when_url_is_missing(self):
        request = self.factory.get('/tasks')

        request.session = {
            "tasks_status": "completed",
            "tasks_order":"oldest"
        }

        status,order = get_tasks_preferences(request)

        self.assertEqual(status,"completed")
        self.assertEqual(order,"oldest")

    def test_invalid_url_values(self):
        request = self.factory.get("/tasks/?status=wrong&order=vertical")

        request.session = {
            "status": "pending",
            "order": "newest"
        }

        status,order = get_tasks_preferences(request)

        self.assertEqual(status,"pending")
        self.assertEqual(order,"newest")



class FilterTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            password="pass123"
        )

        self.project = Project.objects.create(
            name="Test Project",
            owner=self.user
        )

        self.pending_task = Task.objects.create(
            title="Test Task",
            project=self.project,
            is_completed=False
        )

        self.completed_task = Task.objects.create(
            title="Apple",
            project=self.project,
            assigned_to=self.user,
            completed_by=self.user,
            completed_at=timezone.now(),
            is_completed=True
        )


        self.base_qs = Task.objects.filter(project=self.project)


    def test_filter_pending(self):
        qs = filter_tasks(self.base_qs,"pending")

        self.assertEqual(qs.count(),1)
        self.assertFalse(qs.first().is_completed)

    def test_filter_completed(self):
        qs = filter_tasks(self.base_qs,"completed")

        self.assertEqual(qs.count(),1)
        self.assertTrue(qs.first().is_completed)



class SearchTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            password="pass123"
        )

        self.assingee = User.objects.create_user(
            username="Alice",
            password="pass123" 
        )

        self.project = Project.objects.create(
            name="Test Project",
            owner=self.user
        )

        self.task1 = Task.objects.create(
            title="Fix login bug",
            project=self.project,
            assigned_to=self.assingee
        )

        self.task2 = Task.objects.create(
            title="Add Search Feature",
            project=self.project
        )

        self.base_qs = Task.objects.filter(project=self.project)

    

    def test_search_returns_matching_tasks(self):
        qs = search_tasks(self.base_qs,"Fix")

        self.assertEqual(qs.count(),1)
        self.assertEqual(qs.first(),self.task1)

    def test_search_returns_match_tasks_case_insensitive(self):
        qs = search_tasks(self.base_qs,"SEARCH")

        self.assertEqual(qs.count(),1)
        self.assertEqual(qs.first(),self.task2)


    def test_empty_search_returns_all(self):
        qs = search_tasks(self.base_qs,"")

        self.assertEqual(qs.count(),2)
      

    def test_query_not_found_returns_nothing(self):
        qs = search_tasks(self.base_qs,"Apple")

        self.assertEqual(qs.count(),0)


    def test_filtes_tasks_in_list_view(self):
        self.client.login(username="user",password="pass123")

        response = self.client.get(
            reverse('list_tasks',args=[self.project.pk]),
            {"search":"Fix Login Bug"}
        )

        self.assertEqual(response.status_code,200)
        self.assertContains(response,"Fix Login Bug")
        self.assertNotContains(response,"Add Search Feature")

    
    def test_search_by_title(self):
        qs = search_tasks(self.base_qs,"login")

        self.assertEqual(qs.count(),1)
        self.assertEqual(qs.first(),self.task1)

    def test_search_by_assigned_user(self):
        qs = search_tasks(self.base_qs,"Alice")

        self.assertEqual(qs.count(),1)
        self.assertEqual(qs.first(),self.task1)



    


    


    





