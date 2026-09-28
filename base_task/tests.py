from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Project, Task

class TaskManagementSystemTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='perdorues1', password='password123')
        self.user2 = User.objects.create_user(username='perdorues2', password='password123')

        self.project1 = Project.objects.create(
            name='Projekti Test',
            description='Përshkrim test',
            owner=self.user1
        )

    def test_login_required(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_user_cannot_access_other_user_project(self):
        self.client.login(username='perdorues2', password='password123')
        response = self.client.get(f'/project/{self.project1.id}/')
        self.assertEqual(response.status_code, 404)

    def test_task_creation(self):
        self.client.login(username='perdorues1', password='password123')
        task = Task.objects.create(
            title='Detyra 1',
            description='Përshkrim',
            project=self.project1,
            created_by=self.user1,
            due_date=timezone.now() + timedelta(days=5)
        )
        self.assertEqual(task.title, 'Detyra 1')
        self.assertEqual(self.project1.tasks.count(), 1)

    def test_overdue_task(self):
        past_due = timezone.now() - timedelta(days=2)
        task = Task.objects.create(
            title='Detyrë e vjetër',
            project=self.project1,
            created_by=self.user1,
            status='TODO',
            due_date=past_due
        )
        self.assertTrue(task.is_overdue)

    def test_project_progress_calculation(self):
        self.assertEqual(self.project1.progress_percentage(), 0)

        Task.objects.create(
            title='Detyra 1', project=self.project1, created_by=self.user1,
            status='DONE', due_date=timezone.now() + timedelta(days=1)
        )
        Task.objects.create(
            title='Detyra 2', project=self.project1, created_by=self.user1,
            status='TODO', due_date=timezone.now() + timedelta(days=1)
        )

        self.assertEqual(self.project1.total_tasks(), 2)
        self.assertEqual(self.project1.completed_tasks(), 1)
        self.assertEqual(self.project1.progress_percentage(), 50.0)