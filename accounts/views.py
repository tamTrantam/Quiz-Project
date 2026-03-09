# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.utils import timezone
from .models import CustomUser
from .forms import LoginForm
from quiz.models import Assignment, Course, CourseDocument, CourseMembership


def _can_view_teacher_dashboard(user):
    return user.is_superuser or user.role == CustomUser.Roles.TEACHER


def _can_view_student_dashboard(user):
    return user.is_superuser or user.role == CustomUser.Roles.STUDENT


def home_view(request):
    # Redirect logged-in users away
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('teacher_dashboard')
        if request.user.role == CustomUser.Roles.TEACHER:
            return redirect('teacher_dashboard')
        return redirect('student_dashboard')
    
    # Render home page for guests
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid(): # Check form validity
        user = form.get_user() # Get authenticated user
        login(request, user)
        if user.is_superuser:
            return redirect('teacher_dashboard')
        if getattr(user, 'role', None) == CustomUser.Roles.TEACHER:
            return redirect('teacher_dashboard')
        return redirect('student_dashboard')

    return render(request, 'login.html', {'form': form})

def signup_view(request):
    return render(request, 'signup.html', {'signup_available': False})


def _role_label(user):
    if user.is_superuser:
        return 'Superuser'
    return CustomUser.Roles(user.role).label


def _dashboard_context(request, active_section, breadcrumb_parts):
    profile_image_url = static('img/default-avatar.svg')
    if getattr(request.user, 'profile_image', None):
        profile_image_url = request.user.profile_image.url

    return {
        'display_name': request.user.get_full_name() or request.user.username,
        'role_label': _role_label(request.user),
        'profile_image_url': profile_image_url,
        'active_section': active_section,
        'breadcrumb_parts': breadcrumb_parts,
    }


def _student_course_ids(user):
    if user.is_superuser:
        return list(Course.objects.filter(is_active=True).values_list('id', flat=True))

    return list(
        CourseMembership.objects.filter(
            user=user,
            role=CourseMembership.MembershipRole.STUDENT,
            is_active=True,
            course__is_active=True,
        ).values_list('course_id', flat=True)
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def teacher_dashboard_view(request):
    if not _can_view_teacher_dashboard(request.user):
        return redirect('home')
    context = _dashboard_context(
        request,
        active_section='quizzes',
        breadcrumb_parts=['English Course', 'Quizzes', 'Teacher Dashboard'],
    )
    return render(request, 'teacher_dashboard.html', context)


@login_required
def student_dashboard_view(request):
    if not _can_view_student_dashboard(request.user):
        return redirect('home')
    context = _dashboard_context(
        request,
        active_section='quizzes',
        breadcrumb_parts=['English Course', 'Quizzes', 'Student Dashboard'],
    )
    return render(request, 'student_dashboard.html', context)


@login_required
def dashboard_quizzes_view(request):
    if not (_can_view_teacher_dashboard(request.user) or _can_view_student_dashboard(request.user)):
        return redirect('home')

    context = _dashboard_context(
        request,
        active_section='quizzes',
        breadcrumb_parts=['English Course', 'Quizzes', 'Overview'],
    )

    if _can_view_teacher_dashboard(request.user) and not _can_view_student_dashboard(request.user):
        return render(request, 'teacher_dashboard.html', context)

    course_ids = _student_course_ids(request.user)
    assignments = Assignment.objects.filter(
        course_id__in=course_ids,
        published=True,
    ).select_related('course', 'quiz', 'document')
    now = timezone.now()

    context.update(
        {
            'course_count': len(course_ids),
            'upcoming_assignments': assignments.filter(due_at__gte=now).order_by('due_at', 'title')[:8],
            'undated_assignments': assignments.filter(due_at__isnull=True).order_by('title')[:8],
            'recent_quiz_assignments': assignments.filter(
                type=Assignment.AssignmentType.QUIZ,
                quiz__isnull=False,
            ).order_by('-created_at')[:8],
        }
    )
    template = 'quiz/student_assignments.html'
    return render(request, template, context)


@login_required
def dashboard_documents_view(request):
    if not (_can_view_teacher_dashboard(request.user) or _can_view_student_dashboard(request.user)):
        return redirect('home')

    context = _dashboard_context(
        request,
        active_section='documents',
        breadcrumb_parts=['English Course', 'Documents', 'Library'],
    )

    if _can_view_teacher_dashboard(request.user) and not _can_view_student_dashboard(request.user):
        return render(request, 'teacher_dashboard.html', context)

    course_ids = _student_course_ids(request.user)
    context.update(
        {
            'course_count': len(course_ids),
            'folder_roots': CourseDocument.objects.filter(
                course_id__in=course_ids,
                kind=CourseDocument.DocumentKind.FOLDER,
                parent__isnull=True,
            ).select_related('course').prefetch_related('children')[:30],
            'recent_resources': CourseDocument.objects.filter(
                course_id__in=course_ids,
                kind__in=[CourseDocument.DocumentKind.FILE, CourseDocument.DocumentKind.LINK],
            ).select_related('course').order_by('-updated_at')[:12],
        }
    )
    template = 'quiz/student_documents.html'
    return render(request, template, context)


@login_required
def dashboard_settings_view(request):
    context = _dashboard_context(
        request,
        active_section='settings',
        breadcrumb_parts=['English Course', 'Settings'],
    )
    template = 'teacher_dashboard.html' if _can_view_teacher_dashboard(request.user) else 'student_dashboard.html'
    return render(request, template, context)