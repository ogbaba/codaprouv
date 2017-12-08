from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import connection
from django import forms
from django.db.models import Count
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
    code = forms.CharField(widget=forms.Textarea,
                           max_length=500)

class FormAvis(forms.Form):
    commentaire = forms.CharField(widget=forms.Textarea,
                                  max_length=100)

def valider(request):
    codillons = None
    if request.user.is_authenticated():
        cursor = connection.cursor()
        cursor.execute("select id from codaprouv_codillon where id not in (select codillon_id from codaprouv_avis where codillon_id=" + str(request.user.id) + ") order by RANDOM() limit 1")
        codillon_id = int(cursor.fetchone()[0])
        codillon = Codillon.objects.get(pk=codillon_id)
        print("LE CODILLON !!!" + str(codillon))
        #codillon = Codillon.objects.get(pk=codillon_id)
    if request.method == 'POST':
        form = FormAvis(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            avis_bon=request.POST.get("bon")
            avis_note= 1 if avis_bon else  -1           
            Avis.objects.create(commentaire=form.cleaned_data['commentaire'],
                        auteur=request.user,
                        avis=avis_note,
                        codillon=codillon,)
            return redirect(index)
    form = FormAvis()
    return render(request, 'valider.html', {'form':form, 'codillon':codillon})

    
def codiller(request):
    if request.method == 'POST':
        form = FormCodillon(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            Codillon.objects.create(donnees=form.cleaned_data['code'],
                                createur=request.user,
                                date_publi=datetime.datetime.utcnow())
            return redirect(index)
    form = FormCodillon()
    return render(request, 'codiller.html', {'form':form})

