
from django.contrib import admin
from django.urls import path
from myapp import views  # Ensure 'myapp' is your actual app name
from django.conf import settings
from django.conf.urls.static import static
from myapp.views import jobseeker_view_jobs
from myapp import views
from django.urls import path
# from django.urls import path
# from . import views



urlpatterns = [
    # ✅ Admin Panel
    path('admin/', admin.site.urls),

    # ✅ Home Page & Authentication
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),  # Fixed function name
    path('logout/', views.logout_view, name='logout'),
    path('admin/recruiters/', views.recruiter_details, name='recuiter-details'),

    # ✅ Admin Dashboard & Approvals
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-recruiter/<int:user_id>/', views.approve_recruiter, name='approve_recruiter'),

    # ✅ Recruiter Dashboard & Job Posting
    path('recruiter-dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),

    # ✅ Job Seeker Dashboard & Job Viewing
    path("post-job/", views.post_job, name="post_job"),
    path("delete-job/<int:job_id>/", views.delete_job, name="delete_job"),

    path('viewjobs/', views.jobseeker_view_jobs, name='view_jobs'),
    path('apply-jobs/<int:job_id>/', views.apply_job, name='apply_jobsss'),

    path('jobseeker-dashboard/', views.jobseeker_dashboard, name='jobseeker_dashboard'),

    path('recruiter/applications/', views.recruiter_view_applications, name='recruiter_view_applications'),

    path('view-applicants/', views.view_applicants, name='view_applicants'),

    path('admin/recruiters/', views.recruiter_details, name='recruiter_details'),
    path('admin/jobseekers/', views.jobseeker_details, name='jobseeker_details'),

   path('logout/', views.logout_view, name='logout'),



    path('delete-recruiter/<int:recruiter_id>/', views.delete_recruiter, name='delete_recruiter'),

    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    
    path('delete-application/<int:app_id>/', views.delete_application, name='delete_application'),


    # path('admin-dashboard/view-jobs/', views.view_jobs, name='view_jobs'),
    # # other paths

]


    






urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
