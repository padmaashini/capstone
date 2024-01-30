from django.shortcuts import render
from django.http import JsonResponse

def home(request):
    return render(request, "pages/home.html", {})

def requests_for_practitioner(request, id):
    print('id', id)
    data = []
    
    return JsonResponse({ "status": "Success", "data": data })