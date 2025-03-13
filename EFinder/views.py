from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

# Temporal Home Page View
#@login_required
def home(request):
    return render(request, 'home.html')

def inv_eu(request):
    return render(request, 'EFinder/inv_eu.html')