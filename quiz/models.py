from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from typing import TypedDict, Union


class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = 'MCQ', 'Multiple Choice'
    TRUE_FALSE = 'TF', 'True/False'
    FILL_IN_THE_BLANK = 'FB', 'Fill in the Blank'
    READING_PASSAGE = 'READ', 'Reading Passage'


# TypedDict definitions for payload schemas
class MultipleChoicePayload(TypedDict):
    options: dict[int,str] #id to option text mapping
    correct_answer: str


class TrueFalsePayload(TypedDict):
    correct_answer: bool


class FillInTheBlankPayload(TypedDict):
    correct_answer: str


class SubQuestion(TypedDict):
    text: str
    correct_answer: str


class ReadingPassagePayload(TypedDict):
    passage: str
    sub_questions: list[SubQuestion]


# Union type for all payload types
QuestionPayload = Union[
    MultipleChoicePayload,
    TrueFalsePayload,
    FillInTheBlankPayload,
    ReadingPassagePayload
]

# Mapping question types to their payload TypedDicts for validation
PAYLOAD_SCHEMA = {
    QuestionType.MULTIPLE_CHOICE: MultipleChoicePayload,
    QuestionType.TRUE_FALSE: TrueFalsePayload,
    QuestionType.FILL_IN_THE_BLANK: FillInTheBlankPayload,
    QuestionType.READING_PASSAGE: ReadingPassagePayload,
}


class Quiz(models.Model): 
    """Grouping of questions for assessment purposes."""
    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        related_name='quizzes',
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=200)
    cover_image = models.FileField(upload_to='quiz_app/quiz_covers/', default=None, blank=True, null=True)
    description = models.TextField()
    number_of_questions = models.IntegerField()
    end_time = models.DateTimeField()

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title


class Question(models.Model):
    """Individual question within a quiz.
    
    The `payload` field stores type-specific data as JSON:
    
    - MCQ: {'options': ['A', 'B', 'C', 'D'], 'correct_answer': 'B'}
    - TF: {'correct_answer': True}
    - FB: {'correct_answer': 'answer text'}
    - READ: {'passage': '...', 'sub_questions': [...]}
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    media = models.FileField(upload_to='quiz_app/question_media/', blank=True, null=True)
    text = models.TextField()
    type = models.CharField(max_length=10, choices=QuestionType.choices, default=QuestionType.MULTIPLE_CHOICE)
    payload = models.JSONField(default=dict) # Stores type-specific data

    def __str__(self):
        return f"{self.quiz.title} - Q{self.pk}" # Question identifier within quiz

    def clean(self):
        """Validate payload matches the question type schema."""
        schema = PAYLOAD_SCHEMA.get(QuestionType(self.type)) # Get corresponding schema
        if schema:
            required_keys = list(schema.__annotations__.keys()) # Required keys from TypedDict
            missing = [key for key in required_keys if key not in self.payload]
            if missing:
                raise ValidationError(
                    f"Payload for {QuestionType(self.type).label} must include: {', '.join(missing)}"
                )

    def check_answer(self, user_answer) -> bool:
        """Check if the user's answer is correct."""
        correct = self.payload.get('correct_answer')
        
        if self.type == QuestionType.TRUE_FALSE:
            return bool(user_answer) == bool(correct)
        
        if self.type == QuestionType.MULTIPLE_CHOICE:
            options = self.payload.get("options", {}) #id to option text mapping
            return options.get(str(user_answer)) == correct #user_answer is option id
        
        if self.type == QuestionType.FILL_IN_THE_BLANK:
            return str(user_answer).strip().lower() == str(correct).strip().lower()
        
        return False

    @property
    def options(self):
        """Get MCQ options (convenience property)."""
        return self.payload.get('options', {})

    @property
    def correct_answer(self):
        """Get correct answer (convenience property)."""
        return self.payload.get('correct_answer')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Course(models.Model):
    """Course container that supports simple parent-child hierarchy."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children',
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class CourseMembership(models.Model):
    """Tracks user admission to courses for both teacher and student roles."""

    class MembershipRole(models.TextChoices):
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_memberships')
    role = models.CharField(max_length=20, choices=MembershipRole.choices)
    admitted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('course', 'user', 'role')
        ordering = ['course__title', 'user__username']

    def __str__(self):
        return f"{self.user} - {self.role} in {self.course}"


class CourseDocument(models.Model):
    """Hierarchical course document node: folder, file, or external link."""

    class DocumentKind(models.TextChoices):
        FOLDER = 'folder', 'Folder'
        FILE = 'file', 'File'
        LINK = 'link', 'Link'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documents')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=20, choices=DocumentKind.choices, default=DocumentKind.FOLDER)
    file = models.FileField(upload_to='course_documents/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def clean(self):
        if self.kind == self.DocumentKind.FILE and not self.file:
            raise ValidationError("File is required when document kind is 'file'.")

        if self.kind == self.DocumentKind.LINK and not self.external_url:
            raise ValidationError("External URL is required when document kind is 'link'.")

        if self.kind == self.DocumentKind.FOLDER and (self.file or self.external_url):
            raise ValidationError("Folder kind cannot have file or external URL.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Assignment(models.Model):
    """Course assignment that can point to a quiz or a document."""

    class AssignmentType(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        DOCUMENT = 'document', 'Document'
        HOMEWORK = 'homework', 'Homework'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=AssignmentType.choices, default=AssignmentType.HOMEWORK)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, blank=True, null=True, related_name='assignments')
    document = models.ForeignKey(CourseDocument, on_delete=models.SET_NULL, blank=True, null=True, related_name='assignments')
    due_at = models.DateTimeField(blank=True, null=True)
    published = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def clean(self):
        if self.type == self.AssignmentType.QUIZ and not self.quiz:
            raise ValidationError("Quiz is required when assignment type is 'quiz'.")

        if self.type == self.AssignmentType.DOCUMENT and not self.document:
            raise ValidationError("Document is required when assignment type is 'document'.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)