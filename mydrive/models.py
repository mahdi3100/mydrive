from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Content(models.Model):
    owner = models.ForeignKey("User" , on_delete=models.CASCADE,related_name="ownecontent")
    path = models.CharField(max_length=255,default="")
    file = models.CharField(max_length=255,blank=True,null=True)#by default it create dir media and save it there (media dir is in settings)
    privercy = models.CharField(max_length=50,default="private")

class Settingsuser(models.Model):
    ownerSettings = models.ForeignKey("User" , on_delete=models.CASCADE,related_name="ownesettings")
    allowdownload = models.BooleanField(default=True)
    allowusername = models.BooleanField(default=True)
