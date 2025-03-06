from django.shortcuts import render

# Create your views here.

# Temporal Home Page View
def home(request):
    return render(request, 'home.html')