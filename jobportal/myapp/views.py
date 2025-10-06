
from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'salary']


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import login
from .forms import RegisterForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # ✅ Admin approval for recruiters
            if user.user_type == 'recruiter':
                user.is_approved = False
                messages.success(request, "Registration successful! Your account is pending admin approval.")
            else:
                user.is_approved = True
                messages.success(request, "Registration successful! Please log in.")

            user.save()
            return redirect('login1')  # Redirect to login page after successful registration
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})