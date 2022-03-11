from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User

# User is just AbstractUser

class Date(models.Model):
    date = models.CharField(primary_key=True,
                            unique=True,
                            max_length=10,
                            validators=[
                                # Needs validation before insert to remove invalid dates
                                RegexValidator(r'^20[2-9][0-9]-[0-1][0-9]-[0-3][0-9]$',
                                                message='Date must be YYYY-MM-DD, after 2020.'
                                )
                            ])
    users = models.ManyToManyField(User)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.ForeignKey(Date, related_name='notes', on_delete=models.CASCADE)
    message = models.CharField(max_length=256)

    def __str__(self):
        return str(self.date) + ' -> ' + '"' + str(self.message) + '"' 