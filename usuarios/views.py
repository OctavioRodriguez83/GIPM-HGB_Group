from django.shortcuts import render

# Create your views here.

# Temporal Home Page View
def login(request):
    return render(request, 'login.html')