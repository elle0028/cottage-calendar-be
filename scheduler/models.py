from django.db import models
from django.contrib.auth.models import User

# User is just AbstractUser

class Date(models.Model):
    date = models.DateTimeField()
    users = models.ManyToManyField(User)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.ForeignKey(Date, on_delete=models.CASCADE)
    message = models.CharField(max_length=256)