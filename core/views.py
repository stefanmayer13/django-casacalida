from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

def index(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    return render(request, 'core/index.html', {
        'user': user
    })

def login(request):
    if request.method == 'GET':
        return render(request, 'core/login.html')
    elif request.method == 'POST':
        errorMessage = None
        username = request.POST['username']
        password = request.POST['password']
        if not (username and password):
            errorMessage = "Please enter username and password."
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return HttpResponseRedirect(reverse('core:index'))
                else:
                    errorMessage = "This user account ist not active."
            else:
                errorMessage = "Username or password wrong."
        return render(request, 'core/login.html', {
            'error_message': errorMessage,
        })

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('core:index'))
