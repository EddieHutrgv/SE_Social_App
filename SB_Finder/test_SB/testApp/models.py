from django.db import models
from django.contrib.auth.models import User

class StudySession(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    course = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    max_students = models.IntegerField(default=5)
    members = models.ManyToManyField(User, related_name='joined_sessions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course} - {self.subject}"

    def is_full(self):
        return self.members.count() >= self.max_students

    def spots_left(self):
        return self.max_students - self.members.count()
