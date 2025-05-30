from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)

def certificate_upload_to(instance, filename):
    return f"certificates/{instance.user.username}/{filename}"

class Medium(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TeachingMode(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class AcademicProfile(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='academic_profile')
    institution = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    results = models.TextField(blank=True)
    certificates = models.FileField(upload_to=certificate_upload_to, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Academic Profile"

class TeacherProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='teacher_profile')
    bio = models.TextField(blank=True)
    subject = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    medium = models.ManyToManyField(Medium, blank=True, related_name='teacher_profiles')
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('any', 'Any'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    teaching_mode = models.ManyToManyField(TeachingMode, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_profiles')
    preferred_distance = models.PositiveIntegerField(default=0, help_text="Preferred distance for teaching in kilometers")

    def __str__(self):
        return f"{self.user.username}'s Teacher Profile"