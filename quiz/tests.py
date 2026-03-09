from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Assignment, Course, CourseDocument, CourseMembership, Quiz


class StudentWorkflowViewTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.student = User.objects.create_user(username='student1', password='pass123', role='student')
		self.other_student = User.objects.create_user(username='student2', password='pass123', role='student')
		self.teacher = User.objects.create_user(username='teacher1', password='pass123', role='teacher')

		self.student_course = Course.objects.create(title='Student Course')
		self.other_course = Course.objects.create(title='Other Course')

		CourseMembership.objects.create(
			course=self.student_course,
			user=self.student,
			role=CourseMembership.MembershipRole.STUDENT,
			is_active=True,
		)
		CourseMembership.objects.create(
			course=self.other_course,
			user=self.other_student,
			role=CourseMembership.MembershipRole.STUDENT,
			is_active=True,
		)

		self.quiz = Quiz.objects.create(
			course=self.student_course,
			title='Quiz 1',
			description='Quiz description',
			number_of_questions=1,
			end_time=timezone.now() + timedelta(days=1),
		)
		self.assignment = Assignment.objects.create(
			course=self.student_course,
			title='Assignment 1',
			type=Assignment.AssignmentType.QUIZ,
			quiz=self.quiz,
			published=True,
			due_at=timezone.now() + timedelta(days=2),
		)
		self.hidden_assignment = Assignment.objects.create(
			course=self.other_course,
			title='Hidden Assignment',
			type=Assignment.AssignmentType.HOMEWORK,
			published=True,
		)
		self.document = CourseDocument.objects.create(
			course=self.student_course,
			title='Resource Link',
			kind=CourseDocument.DocumentKind.LINK,
			external_url='https://example.com/resource',
		)

	def test_student_can_open_own_assignment_detail(self):
		self.client.login(username='student1', password='pass123')
		response = self.client.get(reverse('student_assignment_detail', args=[self.assignment.id]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Assignment 1')

	def test_student_cannot_open_other_course_assignment_detail(self):
		self.client.login(username='student1', password='pass123')
		response = self.client.get(reverse('student_assignment_detail', args=[self.hidden_assignment.id]))
		self.assertEqual(response.status_code, 404)

	def test_teacher_redirected_from_student_assignment_detail(self):
		self.client.login(username='teacher1', password='pass123')
		response = self.client.get(reverse('student_assignment_detail', args=[self.assignment.id]))
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse('home'))

	def test_student_document_open_redirects_to_external_url(self):
		self.client.login(username='student1', password='pass123')
		response = self.client.get(reverse('student_document_open', args=[self.document.id]))
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, 'https://example.com/resource')
