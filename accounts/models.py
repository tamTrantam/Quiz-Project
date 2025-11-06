from django.db import models 
from django.contrib.auth.models import AbstractUser

#setting up custom user model for teacher and student roles
class CustomUser(AbstractUser):
    """Custom user model extending AbstractUser to include roles for Teacher and Student."""
    class Roles(models.TextChoices):
        """Defines user roles: Teacher / Student."""
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'

    role = models.CharField(max_length=20,
                            choices=Roles.choices, 
                            default=Roles.STUDENT) 
    """this field defines the role of the user, either teacher or student, defaulting to student, and disallows null or blank values."""

    def __str__(self):
        return self.username
    def is_teacher(self):
        return self.role == self.Roles.TEACHER
    def is_student(self):
        return self.role == self.Roles.STUDENT
    
    
# Model to store additional information for teachers
class TeacherProfile(models.Model):
    """Profile model for additional teacher information (User)"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):  
        return f"{self.user.username} - Teacher"

class StudentProfile(models.Model):
    """Profile model for additional student information (User)"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    grade_level = models.FloatField()
    guardian_contact = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Student"