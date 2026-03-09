from django.contrib import admin
from . import models
# Register your models here.
# they will appear in the admin interface, allowing you to manage quizzes, questions, courses, and course memberships through the Django admin panel.
admin.site.register(models.Quiz)
admin.site.register(models.Question)
admin.site.register(models.Course)
admin.site.register(models.CourseMembership)
