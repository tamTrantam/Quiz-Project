from django.urls import path

from . import views

urlpatterns = [
	path('', views.quiz_home, name='quiz_home'),
	path('student/assignments/<int:assignment_id>/', views.student_assignment_detail_view, name='student_assignment_detail'),
	path('student/documents/<int:document_id>/open/', views.student_document_open_view, name='student_document_open'),
]
