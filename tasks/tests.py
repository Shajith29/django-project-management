from django.test import TestCase
from django.urls import reverse

from projects.models import Project, ProjectMembership
from tasks.models import Task

from django.contrib.auth.models import User
from django.utils import timezone

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

        self.assign_url = reverse('assign_task',args=[self.task.pk,self.member.pk])


    
    def test_owner_can_assign_task(self):
        self.client.login(username="owner",password="pass123")

        response = self.client.post(self.assign_url)

        self.task.refresh_from_db()

        self.assertEqual(self.task.assigned_to,self.member)
        self.assertEqual(response.status_code,302)

    def test_owner_cannot_assign_non_member(self):

        url = reverse("assign_task",args=[self.task.pk,self.other.pk])

        self.client.login(username="owner",password="pass123")
        response = self.client.post(url)

        self.task.refresh_from_db()

        self.assertIsNone(self.task.assigned_to)
        self.assertEqual(response.status_code,403)

    def member_cannot_assign_task(self):
        self.client.login(username="member",password="pass123")

        response = self.client.post(self.assign_url)

        self.task.refresh_from_db()

        self.assertIsNone(self.task.assigned_to)
        self.assertEqual(response.status_code,403)

    def anonymous_user_cannot_assign_task(self):
        response = self.client.post(self.assign_url)

        self.task.refresh_from_db()
        self.assertIsNone(self.task.assigned_to)
        self.assertEqual(response.status_code,302)

    


    


    





