from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project,ProjectMembership
from tasks.models import Task

# Create your tests here.

class DeleteProjectTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="testuser",
            password="password123"
        )

        self.member = User.objects.create_user(
            username="testmember",
            password="password321"
        )

        self.project = Project.objects.create(
            name="Test Project",
            owner=self.owner
        )

        ProjectMembership.objects.create(
            user=self.member,
            project=self.project
        )

        self.delete_url = reverse('delete_project',args=[self.project.pk])


    def test_owner_can_delete_project(self):
        self.client.login(username="testuser",password="password123")

        response = self.client.post(self.delete_url)

        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(response.status_code,302)

    def test_memebers_cannot_delete_project(self):
        self.client.login(username="testmember",password="password321")

        response = self.client.post(self.delete_url)

        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(response.status_code,403)

    def test_anonymous_member_cannot_delete_project(self):
        response = self.client.post(self.delete_url)

        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(response.status_code,302)



class ProjectMemberManagementTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="pass123"
        )

        self.member = User.objects.create_user(
            username="member",
            password="pass123"
        )

        self.other = User.objects.create_user(
            username="other_member",
            password="pass123"
        )

        self.project = Project.objects.create(
            name="Test Project",
            owner = self.owner
        )

        self.add_url = reverse('add_project_member',args=[self.project.pk,self.member.pk])


    
    def test_owner_can_add_member(self):
        self.client.login(username="owner",password="pass123")

        response = self.client.post(self.add_url)

        self.assertTrue(ProjectMembership.objects.filter(
            project = self.project,
            user = self.member
        ).exists())

        self.assertEqual(response.status_code,302)

    
    def test_non_owner_cannot_add_member(self):
        self.client.login(username="member",password="pass123")

        response = self.client.post(self.add_url)

        self.assertFalse(ProjectMembership.objects.filter(
            project=self.project,
            user=self.member
        ).exists())

        self.assertEqual(response.status_code,403)

    def test_cannot_add_duplicate_member(self):
        ProjectMembership.objects.create(
            project = self.project,
            user = self.member
        )

        self.client.login(username="owner",password="pass123")

        self.assertEqual(ProjectMembership.objects.filter(
            project=self.project,
            user=self.member
        ).count(),1)

    def test_owner_cannot_be_deleted(self):
        self.client.login(username="owner",password="pass123")

        url = reverse("remove_project_member",args=[self.project.pk,self.owner.pk])

        response = self.client.post(url)


        self.assertEqual(response.status_code,403)


class TestProjectOwnership(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner",password="pass123")
        self.member = User.objects.create_user(username="member",password="pass123")
        self.other = User.objects.create_user(username="other",password="pass123")

        self.project = Project.objects.create(
            name="Test Project",
            owner = self.owner
        )

        ProjectMembership.objects.create(
            project=self.project,
            user=self.member
        )

        self.transfer_url = reverse('transfer_project_ownership',args=[self.project.pk,self.member.pk])


    
    def test_owner_can_transfer_ownership(self):
        self.client.login(username="owner",password="pass123")
        
        response = self.client.post(self.transfer_url)

        self.project.refresh_from_db()

        self.assertEqual(self.project.owner,self.member)

        self.assertTrue(ProjectMembership.objects.filter(
            project=self.project,
            user=self.owner
        ).exists())

        self.assertEqual(response.status_code,302)


    def test_member_cannot_transfer_ownership(self):
        self.client.login(username="member",password="pass123")

        response = self.client.post(self.transfer_url)

        self.project.refresh_from_db()

        self.assertEqual(self.project.owner,self.owner)
        self.assertFalse(ProjectMembership.objects.filter(
            project=self.project,
            user=self.owner
        ).exists())
        self.assertEqual(response.status_code,403)

    def test_cannot_transfer_to_non_member(self):
        url = reverse('transfer_project_ownership',args=[self.project.pk,self.other.pk])

        self.client.login(username="owner",password="pass123")

        response = self.client.post(url)

        self.project.refresh_from_db()

        self.assertEqual(self.project.owner,self.owner)
        self.assertEqual(response.status_code,403)

    def test_anonymous_cannot_transfer(self):
        response = self.client.post(self.transfer_url)
        self.project.refresh_from_db()

        self.assertEqual(self.project.owner,self.owner)
        self.assertEqual(response.status_code,302)

        




