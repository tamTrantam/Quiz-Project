from django.contrib import admin
from . import models
from .forms import QuestionAdminForm


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
	list_display = ('title', 'course', 'number_of_questions', 'end_time')
	list_filter = ('course',)
	search_fields = ('title', 'description', 'course__title')


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
	form = QuestionAdminForm
	list_display = ('id', 'quiz', 'type', 'short_text')
	list_filter = ('type', 'quiz__course')
	search_fields = ('text', 'quiz__title', 'quiz__course__title')
	autocomplete_fields = ('quiz',)

	@admin.display(description='Question Text')
	def short_text(self, obj):
		trimmed = (obj.text or '').strip().replace('\n', ' ')
		return f"{trimmed[:80]}..." if len(trimmed) > 80 else trimmed


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ('title', 'parent', 'is_active', 'created_at')
	list_filter = ('is_active',)
	search_fields = ('title', 'description')
	autocomplete_fields = ('parent',)


@admin.register(models.CourseMembership)
class CourseMembershipAdmin(admin.ModelAdmin):
	list_display = ('course', 'user', 'role', 'is_active', 'admitted_at')
	list_filter = ('role', 'is_active', 'course')
	search_fields = ('course__title', 'user__username', 'user__email')
	autocomplete_fields = ('course', 'user')


@admin.register(models.CourseDocument)
class CourseDocumentAdmin(admin.ModelAdmin):
	list_display = ('title', 'course', 'kind', 'parent', 'updated_at')
	list_filter = ('kind', 'course')
	search_fields = ('title', 'description', 'course__title')
	autocomplete_fields = ('course', 'parent', 'created_by')


@admin.register(models.Assignment)
class AssignmentAdmin(admin.ModelAdmin):
	list_display = ('title', 'course', 'type', 'published', 'due_at', 'updated_at')
	list_filter = ('type', 'published', 'course')
	search_fields = ('title', 'description', 'course__title')
	autocomplete_fields = ('course', 'quiz', 'document', 'created_by')
