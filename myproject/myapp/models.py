from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ]
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    resume = models.FileField(upload_to='resumes/%Y/%m/%d/', blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)  # Admin approval for recruiters

    def str(self):
        return self.username

# ✅ Updated Job Model to Link with CustomUser
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    company = models.CharField(max_length=255,null=True)
    company_logo = models.ImageField(upload_to='uploads/', blank=True, null=True) 
    recruiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'recruiter'})  
    created_at = models.DateTimeField(auto_now_add=True)
    skill = models.TextField(blank=True, null=True)
    recruiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def str(self):
        return self.title
    
class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    job_seeker = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    skill = models.CharField(max_length=200,default=True,null=True)
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)    

    def __str__(self):
        return f'{self.name} applied for {self.job.title}'  


from django.db import models

class JobPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=100)
    skill = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    def __str__(self):
        return self.title



