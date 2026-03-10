from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from quiz.models import Assignment, Course, CourseMembership, Quiz


class TeacherWorkflowViewTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.teacher = User.objects.create_user(username='teacher_a', password='pass123', role='teacher')
		self.student = User.objects.create_user(username='student_a', password='pass123', role='student')

		self.teacher_course = Course.objects.create(title='Teacher Course')
		self.other_course = Course.objects.create(title='Other Course')

		CourseMembership.objects.create(
			course=self.teacher_course,
			user=self.teacher,
			role=CourseMembership.MembershipRole.TEACHER,
			is_active=True,
		)
		CourseMembership.objects.create(
			course=self.teacher_course,
			user=self.student,
			role=CourseMembership.MembershipRole.STUDENT,
			is_active=True,
		)

		quiz = Quiz.objects.create(
			course=self.teacher_course,
			title='Teacher Quiz',
			description='Quiz desc',
			number_of_questions=1,
			end_time=timezone.now() + timedelta(days=1),
		)
		Assignment.objects.create(
			course=self.teacher_course,
			title='Teacher Assignment',
			type=Assignment.AssignmentType.QUIZ,
			quiz=quiz,
			published=True,
		)

	def test_teacher_sees_own_courses_on_quiz_dashboard(self):
		self.client.login(username='teacher_a', password='pass123')
		response = self.client.get(reverse('dashboard_quizzes'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Teacher Course')

	def test_teacher_can_open_assigned_course_detail(self):
		self.client.login(username='teacher_a', password='pass123')
		response = self.client.get(reverse('dashboard_teacher_course_detail', args=[self.teacher_course.id]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Teacher Assignment')

	def test_teacher_cannot_open_unassigned_course_detail(self):
		self.client.login(username='teacher_a', password='pass123')
		response = self.client.get(reverse('dashboard_teacher_course_detail', args=[self.other_course.id]))
		self.assertEqual(response.status_code, 404)

	def test_student_cannot_open_teacher_course_detail(self):
		self.client.login(username='student_a', password='pass123')
		response = self.client.get(reverse('dashboard_teacher_course_detail', args=[self.teacher_course.id]))
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse('home'))
