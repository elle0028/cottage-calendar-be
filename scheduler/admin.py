from django.contrib import admin

from .models import Date
from .models import Note

admin.site.register(Date)
admin.site.register(Note)
