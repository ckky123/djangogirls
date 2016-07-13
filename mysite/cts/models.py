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

class Post(models.Model):


    author = models.ForeignKey(User)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)


    #def publish(self):
     #   self.Dep_time = timezone.now()
      # self.save()
      
    def publish(self):
        self.published_date = timezone.now()
        self.save()

   # def __str__(self):
     #   return self.title
     
    def __str__(self):
        return self.title
