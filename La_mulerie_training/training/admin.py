from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Horse, TrainingSession

admin.site.register(Horse)
admin.site.register(TrainingSession)