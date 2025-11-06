# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import CustomUser
from .forms import LoginForm
def login_view(request):
    # Redirect logged-in users away
    if request.user.is_authenticated:
        if request.user.role == CustomUser.Roles.TEACHER:
            return redirect('html/teacher_dashboard.html')
        return redirect('html/student_dashboard.html')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        if getattr(user, 'role', None) == CustomUser.Roles.TEACHER:
            return redirect('teacher_dashboard.html')
        return redirect('student_dashboard.html')

    return render(request, 'login.html', {'form': form})
