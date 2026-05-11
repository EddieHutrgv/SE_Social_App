"""Database models for the Study Buddy Finder application.

This module defines the user profile extensions, study sessions,
memberships, and notification models used by the app.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

YEAR_CHOICES = [
    ('Freshman', 'Freshman'),
    ('Sophomore', 'Sophomore'),
    ('Junior', 'Junior'),
    ('Senior', 'Senior'),
    ('Other', 'Other'),
]

TIME_CHOICES = [
    ('8:00 AM - 12:00 PM', '8:00 AM - 12:00 PM'),
    ('12:00 PM - 4:00 PM', '12:00 PM - 4:00 PM'),
    ('4:00 PM - 8:00 PM', '4:00 PM - 8:00 PM'),
    ('8:00 PM - 12:00 AM', '8:00 PM - 12:00 AM'),
]

class UserProfile(models.Model):
    """Extended user profile with academic and availability information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    major = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True, null=True)
    interests = models.TextField(help_text="Comma-separated list of interests", blank=True, null=True)
    availability_morning = models.BooleanField(default=True)  # 8 AM - 12 PM
    availability_afternoon = models.BooleanField(default=True)  # 12 PM - 4 PM
    availability_evening = models.BooleanField(default=True)  # 4 PM - 8 PM
    availability_night = models.BooleanField(default=False)  # 8 PM - 12 AM
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class StudySession(models.Model):
    """Study session created by users"""
    LOCATION_CHOICES = [
        ('Library', 'Library'),
        ('Student Center', 'Student Center'),
        ('Cafe', 'Cafe'),
        ('Dormitory', 'Dormitory'),
        ('Classroom', 'Classroom'),
        ('Online', 'Online'),
        ('Other', 'Other'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    course_name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES)
    other_location = models.CharField(max_length=200, blank=True, null=True, help_text="Specify if location is 'Other'")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_capacity = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(100)])
    current_members = models.ManyToManyField(User, through='SessionMembership', related_name='joined_sessions')
    subject_tags = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course_name} - {self.date} at {self.start_time}"

    def get_member_count(self):
        return self.current_members.count()

    def is_full(self):
        return self.get_member_count() >= self.max_capacity


class SessionMembership(models.Model):
    """Track which users are members of which sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('left', 'Left'), ('removed', 'Removed')],
        default='active'
    )

    class Meta:
        unique_together = ('user', 'session')

    def __str__(self):
        return f"{self.user.username} in {self.session.course_name}"


class Notification(models.Model):
    """Notifications for users"""
    NOTIFICATION_TYPES = [
        ('session_join', 'Someone Joined Your Session'),
        ('session_created', 'New Study Session'),
        ('session_canceled', 'Session Canceled'),
        ('session_starting', 'Session Starting Soon'),
        ('session_reminder', 'Study Session Reminder'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
