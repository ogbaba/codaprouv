from django.db import models
from django.contrib.auth.models import User

BON_AVIS = 1;
MAUV_AVIS = -1;

class Codillon (models.Model):
    createur = models.ForeignKey(User, on_delete=models.CASCADE)
    donnees = models.CharField(max_length=2000)
    date_publi = models.DateField()
    nom = models.CharField(max_length=30)

class Avis (models.Model):
    codillon = models.ForeignKey('Codillon', on_delete=models.CASCADE)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    avis = models.IntegerField()
    commentaire = models.CharField(max_length=200)
