from django.db import models
from django.contrib.auth.models import User

class codillon (models.Model):
    createur = models.ForeignKey(User, on_delete=models.CASCADE)
    donnees = models.CharField(max_length=500)
