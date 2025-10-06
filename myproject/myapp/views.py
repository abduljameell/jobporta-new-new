from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import CustomUser, Job
from .models import Job
from .models import JobApplication
from .models import CustomUser, Job, JobApplication 




# ✅ Home View
@never_cache
def index(request):
    return render(request, 'index.html')

# ✅ Registration View
@never_cache
def register_view(request):
    if request.method == 'POST':
        firstname=request.POST['first_name']
        lastname=request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['confirm_password']
        user_type = request.POST['user_type']

        if password1 == password2:
            if not CustomUser.objects.filter(username=username).exists():
                user = CustomUser.objects.create_user(
                    first_name=firstname,
                    last_name=lastname,
                    username=username,
                    email=email,
                    password=password1,  # ✅ FIXED
                    user_type=user_type
                )
                if user_type == 'recruiter':
                    user.is_approved = False
                    messages.success(request, 'Registration successful. Please wait for admin approval.')
                else:
                    user.is_approved = True
                    messages.success(request, 'Registration successful. You can now log in.')
                user.save()
                return redirect('login')
            else:
                messages.error(request, 'Username already exists.')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'register.html')

# ✅ Login View
# @never_cache
# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             if user.is_active:
#                 if user.user_type == 'recruiter' and not user.is_approved:
#                     messages.error(request, 'Please wait for admin approval.')
#                     return redirect('login')

#                 login(request, user)

#                 if user.user_type == 'job_seeker':
#                     return redirect('home')  # ✅ FIXED (Redirect Job Seekers correctly)
#                 elif user.user_type == 'recruiter':
#                     return redirect('recruiter_dashboard')
#                 elif user.is_superuser:
#                     return redirect('admin_dashboard')
#             else:
#                 messages.error(request, 'Account is inactive.')
#         else:
#             messages.error(request, 'Invalid username or password.')

#     return render(request, 'login.html')

@never_cache
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                if user.user_type == 'recruiter' and not user.is_approved:
                    messages.error(request, 'Please wait for admin approval.')
                    return redirect('login')

                # ✅ Clear any existing session before login
                request.session.flush()

                # ✅ Log in user
                login(request, user)

                # ✅ Store session data
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['user_type'] = user.user_type
                request.session.set_expiry(0)  # Expires when browser closes

                # ✅ Redirect based on user type
                if user.user_type == 'job_seeker':
                    return redirect('home')
                elif user.user_type == 'recruiter':
                    return redirect('recruiter_dashboard')
                elif user.is_superuser:
                    return redirect('admin_dashboard')
            else:
                messages.error(request, 'Account is inactive.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# ✅ Logout View
def logout_view(request):
    logout(request)
    request.session.flush()  # ✅ Clears all session data
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# ✅ Admin Dashboard View
@login_required
@never_cache
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')

    job_seekers = CustomUser.objects.filter(user_type='job_seeker')
    recruiters = CustomUser.objects.filter(user_type='recruiter')
    jobs = Job.objects.all().order_by('-created_at')  # Get all jobs
    context = {
        'username': request.user.username,
        'job_seeker_count': job_seekers.count(),
        'recruiter_count': recruiters.count(),
        'job_seekers': job_seekers,        # ✅ Needed for Job Seeker section
        'recruiters': recruiters, 
        'pending_recruiters': recruiters.filter(is_approved=False),
        'jobs': jobs,
        
    }
    return render(request, 'admindash.html', context)


def recruiter_details(request):
    recruiters = User.objects.filter(user_type='recruiter')  # Assuming 'user_type' field
    return render(request, 'admindash.html', {'recruiters': recruiters})

def jobseeker_details(request):
    jobseekers = User.objects.filter(user_type='jobseeker')
    return render(request, 'admindash.html', {'jobseekers':jobseekers})



# ✅ Approve Recruiter View
@login_required
@never_cache  # ✅ FIXED
def approve_recruiter(request, user_id):
    if not request.user.is_superuser:
        return redirect('login')

    recruiter = get_object_or_404(CustomUser, id=user_id)
    recruiter.is_approved = True
    recruiter.save()
    
    messages.success(request, f'{recruiter.username} has been approved.')
    return redirect('admin_dashboard')


# ✅ Recruiter Dashboard View
@login_required
@never_cache
def recruiter_dashboard(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, "Access Denied")
        return redirect("login")  # Redirect non-recruiters

    # Fetch jobs posted by the logged-in recruiter
    jobs = Job.objects.filter(recruiter=request.user)

    return render(request, "recruiterdash.html", {"jobs": jobs})
# ✅ Post Job View (for Recruiters)

@login_required

def post_job(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, "Access Denied")
        return redirect("recruiter_dashboard")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location")
        salary = request.POST.get("salary")
        company = request.POST.get("company")
        company_logo = request.FILES.get("company_logo")
        skill = request.POST.get("skill")
        
        print(f"Title: {title}, Description: {description}, Location: {location}, Salary: {salary}, Company: {company}, Logo: {company_logo}, skill: {skill}")
        if title and description and location:
            job=Job.objects.create(
                title=title,
                description=description,
                location=location,
                salary=salary,
                company=company,
                company_logo=company_logo,
                skill = skill, 
                recruiter=request.user,
            )
            print(f"Job Created: {job}")
            messages.success(request, "Job posted successfully!")
        else:
            messages.error(request, "All fields except salary are required.")

    return redirect("recruiter_dashboard")


@login_required
def delete_job(request, job_id):
    if request.user.user_type != 'recruiter':
        messages.error(request, "Access Denied")
        return redirect("recruiter_dashboard")

    job = Job.objects.filter(id=job_id, recruiter=request.user).first()
    if job:
        job.delete()
        messages.success(request, "Job deleted successfully!")
    else:
        messages.error(request, "Job not found or not authorized.")

    return redirect("recruiter_dashboard")
    

# ✅ Recruiter Dashboard View
@login_required
@never_cache
def recruiter_dashboard(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, "Access Denied")
        return redirect("login")  # Redirect non-recruiters

    # Fetch jobs posted by the logged-in recruiter
    jobs = Job.objects.filter(recruiter=request.user)

    return render(request, "recruiterdash.html", {"jobs": jobs})
# ✅ Post Job View (for Recruiters)

@login_required
@never_cache
def recruiter_details(request):
    if not request.user.is_superuser:
        return redirect('login')

    recruiters = CustomUser.objects.filter(user_type='recruiter')
    print("Recruiters Data:", recruiters)
    return render(request, 'admindash.html', {'recruiters': recruiters})

@login_required
@never_cache
def jobseeker_view_jobs(request):
    if request.user.user_type != 'job_seeker':
        messages.error(request, "Access Denied")
        return redirect("login")

    jobs = Job.objects.all().order_by('-created_at')
    print(jobs)
    return render(request, 'index.html', {'jobs': jobs, 'show_jobs': True})

# def apply_job(request, job_id):
#     job = get_object_or_404(Job, pk=job_id)
#     if request.method == 'POST':
#         form = ApplicationForm(request.POST, request.FILES)
#         if form.is_valid():
#             application = form.save(commit=False)
#             applicatdion.job = job
#             application.job_seeker = request.user
#             application.save()
#             return redirect('job_list')  # or a success page
#     else:
#         form = ApplicationForm()
#     return render(request, 'jobseeker/apply_form.html', {'form': form,'job':job})

# @login_required
# def apply_job(request, job_id):
#     job = get_object_or_404(Job, pk=job_id)

#     if request.method == 'POST':
#         form = ApplicationForm(request.POST, request.FILES)
#         if form.is_valid():
#             application = form.save(commit=False)
#             application.job = job
#             application.job_seeker = request.user
#             application.save()
#             messages.success(request, "Application submitted successfully!")
#             return redirect('jobseeker_view_jobs')  # or any page you want after apply
#     else:
#         form = ApplicationForm()

#     return render(request, 'apply_job.html', {'form': form,'job':job})


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        resume = request.FILES.get('resume')
        skill = skill.POST.get('skill')

        if name and email and phone and resume:
            JobApplication.objects.create(
                job=job,
                job_seeker=request.user,
                name=name,
                email=email,
                phone=phone,
                resume=resume,
                skill=skill,
            )
            messages.success(request, "Application submitted successfully!")
            return redirect('jobseeker_view_jobs')
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'apply_job.html',{'job':job})

def jobseeker_dashboard(request):
    return render(request, 'jobseeker_dashboard.html')


@login_required
@never_cache
def recruiter_view_applications(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, "Access Denied")
        return redirect("login")

    # Fetch only the applications for the recruiter's own jobs
    jobs = Job.objects.filter(recruiter=request.user)
    applications = JobApplication.objects.filter(job__in=jobs).select_related('job', 'job_seeker')
    
    return render(request, 'recruiter_view_applications.html', {'applications': applications})

from django.contrib import messages

def apply_job(request, job_id):
    if request.method == 'POST':
        
        ...
        messages.success(request, 'Job applied successfully!')
        return redirect('job_seeker_dashboard')  


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        skills = request.POST.get('skill')
        phone = request.POST.get('phone')
        resume = request.FILES.get('resume')

        JobApplication.objects.create(
            job=job,
            job_seeker=request.user,
            name=name,
            email=email,
            skill=skills,
            phone=phone,
            resume=resume
        )

        messages.success(request, 'Job applied successfully!')
        return redirect('apply_jobsss',job_id=job.id)  # update this redirect as needed

    return render(request, 'apply_job.html', {'job': job})

from django.contrib.auth.decorators import login_required
from .models import JobApplication

@login_required
def view_applicants(request):
    if request.user.user_type != 'recruiter':
        return redirect('login')  # Block job seekers

    # Get all applications for jobs posted by this recruiter
    applications = JobApplication.objects.filter(job__recruiter=request.user).order_by('-applied_at')
    
    return render(request, 'view_applicants.html', {'applications':applications})

from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # make sure 'login' is the name of your login URL

from django.shortcuts import get_object_or_404, redirect
from .models import CustomUser, Job  # replace Job with your actual Job model

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@login_required
@never_cache
def delete_recruiter(request, id):
    if not request.user.is_superuser:
        return redirect('login')

    recruiter = get_object_or_404(CustomUser, id=id, user_type='recruiter')

    # Delete job posts by this recruiter
    Job.objects.filter(recruiter=recruiter).delete()

    # Delete the recruiter
    recruiter.delete()

    return redirect('admin_dashboard')

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser

@login_required
def delete_recruiter(request, recruiter_id):
    if request.user.is_superuser:
        recruiter = get_object_or_404(CustomUser, id=recruiter_id)
        recruiter.delete()
    return redirect('admin_dashboard')  # Adjust based on your URL name

# from .models import JobApplication
# @login_required
# def admin_applied_jobs(request):
#     if request.user.user_type != 'admin':
#         return redirect('login')

#     applications = JobApplication.objects.select_related('job', 'seeker').all()
#     return render(request, 'admin_applied_jobs.html', {'applications':applications})


from .models import JobApplication, Job

from django.shortcuts import render
from .models import JobPost  # assuming this is your model

# def view_jobs(request):
#     # jobs = Job.objects.all()
#     # return render(request, 'admindash.html', {'jobs': jobs})
#     jobs = Job.objects.all().order_by('-created_at')
#     print(jobs)
#     return render(request, 'admindash.html', {'jobs': jobs, 'show_jobs': True})


# def view_jobs(request, recruiter_id):
#     recruiter = get_object_or_404(CustomUser, id=recruiter_id)
#     jobs = Job.objects.filter(recruiter=recruiter).order_by('-created_at')
#     return render(request, 'admindash.html', {'jobs': jobs, 'recruiter': recruiter, 'show_jobs': True})


def view_jobs(request, recruiter_id=None):
    if recruiter_id:
        recruiter = get_object_or_404(CustomUser, id=recruiter_id)
        jobs = Job.objects.filter(recruiter=recruiter).order_by('-created_at')
    else:
        jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'admindash.html', {'jobs': jobs, 'show_jobs': True})

from django.shortcuts import redirect, get_object_or_404
from .models import Job
from django.contrib import messages

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully.')
    return redirect('admin_dashboard')  # Name of your URL pattern

def delete_application(request, app_id):
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, id=app_id)
        application.delete()
        messages.success(request, "Application deleted successfully.")
    return redirect('view_applicants')  # Replace with your actual view name