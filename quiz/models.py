from django.db import models

# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    number_of_questions = models.IntegerField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('FB', 'Fill in the Blank'),
        ('READ', 'Reading Passage'),
    ]
    text = models.TextField()
    type = models.CharField(max_length=10, choices=QUESTION_TYPES)


class MultipleChoice(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    options = models.JSONField()
    correct_answer = models.CharField(max_length=255)


class TrueFalse(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    correct_answer = models.BooleanField()