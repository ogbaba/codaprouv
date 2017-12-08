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
        cursor.execute("select codillon_id, count(*) from codaprouv_avis group by codillon_id having codillon_id not in ( select ca.id from codaprouv_avis ca left join codaprouv_codillon cc on cc.id = "+str(request.user.id)+")")
        codillons_id = cursor.fetchone()
    if request.method == 'POST':
        form = FormAvis(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            avis_bon=request.POST.get("bon")
            avis_note= 1 if avis_bon else  -1           
            avis = Avis(commentaire=form.cleaned_data['commentaire'],
                        auteur=request.user,
                        avis=avis_note,
                        codillon=codillons_id,)
            codillon.save()
            return redirect(index)
    form = FormAvis()
    return render(request, 'valider.html', {'form':form})

    
def codiller(request):
    if request.method == 'POST':
        form = FormCodillon(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            codillon = Codillon(donnees=form.cleaned_data['code'],
                                createur=request.user,
                                date_publi=datetime.datetime.utcnow())
            codillon.save()
            return redirect(index)
    form = FormCodillon()
    return render(request, 'codiller.html', {'form':form})

