from django.db import models 
from django.contrib.auth.models import AbstractUser

#setting up custom user model for teacher and student roles
class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False) # flag to identify if user is a teacher
    is_student = models.BooleanField(default=False) # flag to identify if user is a student

    role_choices = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=role_choices, blank=True, null=True)

    def __str__(self):
        return self.username
    
    
# Model to store additional information for teachers
class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    subject = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):  
        return f"{self.user.username} - Teacher"

