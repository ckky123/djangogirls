from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Train(models.Model):
    DepLoc = models.CharField(max_length=200)
    Arrive = models.CharField(max_length=200)
    Dep_time = models.DateTimeField(
            default=timezone.now)
    Arrive_time = models.DateTimeField(
            default=timezone.now)