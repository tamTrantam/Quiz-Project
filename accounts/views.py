# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from .models import CustomUser
from .forms import LoginForm


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
    context = _dashboard_context(
        request,
        active_section='quizzes',
        breadcrumb_parts=['English Course', 'Quizzes', 'Overview'],
    )
    template = 'teacher_dashboard.html' if _can_view_teacher_dashboard(request.user) else 'student_dashboard.html'
    return render(request, template, context)


@login_required
def dashboard_documents_view(request):
    context = _dashboard_context(
        request,
        active_section='documents',
        breadcrumb_parts=['English Course', 'Documents', 'Library'],
    )
    template = 'teacher_dashboard.html' if _can_view_teacher_dashboard(request.user) else 'student_dashboard.html'
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