from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static

from accounts.models import CustomUser
from .models import Assignment, Course, CourseDocument, CourseMembership

# Create your views here.
def quiz_home(request):
    return render(request, 'Quiz_view.html')


def _can_view_student_dashboard(user):
    return user.is_superuser or user.role == CustomUser.Roles.STUDENT


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


def _dashboard_context(request, active_section, breadcrumb_parts):
    profile_image_url = static('img/default-avatar.svg')
    if getattr(request.user, 'profile_image', None):
        profile_image_url = request.user.profile_image.url

    role_label = 'Superuser' if request.user.is_superuser else CustomUser.Roles(request.user.role).label
    return {
        'display_name': request.user.get_full_name() or request.user.username,
        'role_label': role_label,
        'profile_image_url': profile_image_url,
        'active_section': active_section,
        'breadcrumb_parts': breadcrumb_parts,
    }


@login_required
def student_assignment_detail_view(request, assignment_id):
    if not _can_view_student_dashboard(request.user):
        return redirect('home')

    assignment = get_object_or_404(
        Assignment.objects.select_related('course', 'quiz', 'document'),
        id=assignment_id,
        course_id__in=_student_course_ids(request.user),
        published=True,
    )
    context = _dashboard_context(
        request,
        active_section='quizzes',
        breadcrumb_parts=['English Course', assignment.course.title, 'Assignment'],
    )
    context['assignment'] = assignment
    return render(request, 'quiz/student_assignment_detail.html', context)


@login_required
def student_document_open_view(request, document_id):
    if not _can_view_student_dashboard(request.user):
        return redirect('home')

    document = get_object_or_404(
        CourseDocument,
        id=document_id,
        course_id__in=_student_course_ids(request.user),
    )

    if document.kind == CourseDocument.DocumentKind.FILE and document.file:
        return redirect(document.file.url)

    if document.kind == CourseDocument.DocumentKind.LINK and document.external_url:
        return redirect(document.external_url)

    return redirect('dashboard_documents')