from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views import generic
from django.core.urlresolvers import reverse

def index(request):
    return HttpResponse("Hello, world.")

def login(request):
    if request.method == 'GET':
        return render(request, 'core/login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not (username and password):
            return render(request, 'core/login.html', {
                'error_message': "Please enter username and password.",
            })
        return HttpResponseRedirect(reverse('login'))
