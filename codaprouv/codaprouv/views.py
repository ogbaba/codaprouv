from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import connection
from django import forms
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
import datetime
from .models import *

def index(request):
    return render(request, 'index.html')

def inscription(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('connexion')
    else:
        form = UserCreationForm()
    return render(request, 'inscription.html', {'form':form})

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    return render(request, 'connexion.html')    

def deconnexion(request):
    logout(request)
    return redirect('index')

class FormCodillon(forms.Form):
    nom = forms.CharField(max_length=30)
    code = forms.CharField(widget=forms.Textarea,
                           max_length=2000)

class FormAvis(forms.Form):
    commentaire = forms.CharField(widget=forms.Textarea,
                                  max_length=100)

def valider(request):
    codillons = None
    codillon = None
    if request.user.is_authenticated:
        cursor = connection.cursor()
        cursor.execute("select codaprouv_codillon.id from codaprouv_codillon where codaprouv_codillon.id not in (select codillon_id from codaprouv_avis ca join codaprouv_codillon cc on cc.id = ca.codillon_id where cc.createur_id="+ str(request.user.id) + " or ca.auteur_id="+str(request.user.id) +") order by RANDOM() limit 1")
        cod_el = cursor.fetchone()
        if cod_el is None:
            return redirect(index)
        codillon_id = int(cod_el[0])
        codillon = Codillon.objects.get(pk=codillon_id)
    if request.method == 'POST':
        form = FormAvis(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            avis_bon=request.POST.get("bon")
            avis_note= 1 if avis_bon else  -1           
            Avis.objects.create(commentaire=form.cleaned_data['commentaire'],
                        auteur=request.user,
                        avis=avis_note,
                        codillon=codillon,)
            return redirect(valider)
    form = FormAvis()
    return render(request, 'valider.html', {'form':form, 'codillon':codillon})

    
def codiller(request):
    if request.method == 'POST':
        form = FormCodillon(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            Codillon.objects.create(donnees=form.cleaned_data['code'],
                                    nom=form.cleaned_data['nom'],
                                createur=request.user,
                                date_publi=datetime.datetime.utcnow())
            return redirect(index)
    form = FormCodillon()
    return render(request, 'codiller.html', {'form':form})

def moncode(request):
    codillons = Codillon.objects.filter(createur_id=request.user.id)
    return render(request, 'moncode.html', {'codillons':codillons})

def codillon(request, id):
    codillon = get_object_or_404(Codillon, pk=id)
    liste_avis = Avis.objects.all().filter(codillon_id=id)
    note_totale = liste_avis.aggregate(Sum('avis'))['avis__sum']
    contexte = {
        'liste_avis': liste_avis,
        'codillon': codillon,
        'note_totale': note_totale,
    }
    return render(request, 'codillon.html', contexte);
