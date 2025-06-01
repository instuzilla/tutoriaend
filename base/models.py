from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
 

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Comma separated values: lat,lon,accuracy (e.g., '23.4567,90.1234,10')"
    )

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
    
class Grade(models.Model):
    medium = models.ManyToManyField(Medium, blank=True, related_name='subjects')
    name = models.CharField(max_length=50, unique=True, help_text="The name of the grade (e.g., '10th Grade', '12th Grade')")
    sequence = models.PositiveIntegerField(unique=True, help_text="The sequence number of the grade (e.g., 10 for '10th Grade', 12 for '12th Grade')")

    def __str__(self):
        return self.name
    
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True, help_text="A brief description of the subject.")
    subject_code = models.CharField(max_length=20, unique=True, help_text="A unique code for the subject (e.g., 'MATH101', 'PHY202')", blank=True, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='subjects', blank=True, null=True, help_text="The grade level for which this subject is applicable.")
    def __str__(self):
        return self.name

class AcademicProfile(models.Model):
    teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE, related_name='academic_profile')
    institution = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    results = models.TextField(blank=True)
    certificates = models.FileField(upload_to=certificate_upload_to, blank=True, null=True)

    def __str__(self):
        return f"{self.teacher.user.username}'s Academic Profile"
    
class Qualification(models.Model):
    teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE, related_name='qualifications')
    organization = models.CharField(max_length=255, blank=True)
    skill = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    results = models.TextField(blank=True,null=True)
    certificates = models.FileField(upload_to=certificate_upload_to, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Academic Profile"

class TeacherProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='teacher_profile')
    bio = models.TextField(blank=True, null=True, help_text="A brief biography of the teacher.")
    subject_list = models.ManyToManyField(
        Subject,
        related_name='tutors', # Allows accessing tutors from a subject object (e.g., subject.tutors.all())
        blank=True, # Tutors are not required to have subjects initially
        help_text="The subjects this tutor can teach."
    )
    experience_years = models.PositiveIntegerField(default=0)
    medium = models.ManyToManyField(Medium, blank=True, related_name='teacher_profiles')
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('any', 'Any'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    teaching_mode = models.ManyToManyField(TeachingMode,blank=True, related_name='teacher_profiles')
    preferred_distance = models.PositiveIntegerField(default=0, help_text="Preferred distance for teaching in kilometers")

    def __str__(self):
        return f"{self.user.username}'s Teacher Profile"

    def clean(self):
        # Ensure the associated user has a location set
        if not self.user.location:
            raise ValidationError(
            {'user': _('User must update their location before creating a teacher profile.')}
            )


class Availability(models.Model):
    """
    Represents a specific time slot a tutor is available on a given day.
    A tutor can have multiple availability slots on the same day.
    """
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    tutor = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE, # If a tutor is deleted, their availabilities are also deleted.
        related_name='availabilities', # Allows accessing availabilities from a tutor object (e.g., tutor.availabilities.all())
        help_text="The tutor associated with this availability slot."
    )
    day_of_week = models.CharField(
        max_length=3,
        choices=DAY_CHOICES,
        help_text="The day of the week for this availability slot."
    )
    start_time = models.TimeField(help_text="The start time of the availability slot.")
    end_time = models.TimeField(help_text="The end time of the availability slot.")

    class Meta:
        verbose_name = "Availability Slot"
        verbose_name_plural = "Availability Slots"
        # Ensure that a tutor cannot have overlapping time slots on the same day.
        # This unique_together constraint helps prevent simple overlaps,
        # but more complex overlap logic might be needed in clean method or forms.
        unique_together = ('tutor', 'day_of_week', 'start_time', 'end_time')
        ordering = ['tutor__user__username', 'day_of_week', 'start_time'] # Order by tutor, then day, then start time.

    def clean(self):
        """
        Custom validation to ensure end_time is after start_time.
        """
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    _('End time must be after start time.'),
                    code='invalid_time_range'
                )

    def __str__(self):
        return f"{self.tutor.user.username} - {self.get_day_of_week_display()} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"
