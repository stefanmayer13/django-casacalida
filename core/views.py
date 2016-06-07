from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.models import Device
from core.serializers import serializeDevice
import json

def index(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    return render(request, 'core/index.html', {
        'user': user
    })

def login(request):
    if request.user.is_authenticated():
        next = request.GET.get('next', '')
        redirect = next if next else reverse('core:dashboard')
        return HttpResponseRedirect(redirect)
    elif request.method == 'GET':
        return render(request, 'core/login.html', {
            'next': request.GET.get('next', '')
        })
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
                    next = request.POST.get('next', False)
                    redirect = next if next else reverse('core:dashboard')
                    return HttpResponseRedirect(redirect)
                else:
                    errorMessage = "This user account ist not active."
            else:
                errorMessage = "Username or password wrong."
        return render(request, 'core/login.html', {
            'error_message': errorMessage,
            'next': request.GET.get('next', ''),
        })

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('core:index'))

@login_required
def dashboard(request):
    devices = Device.objects.all()
    return render(request, 'core/dashboard.html', {
        'devices': devices
    })

def device_list(request):
    if request.user.is_authenticated():
        return JsonResponse(dict(devices=list(Device.objects.values('id', 'name'))))
    else:
        return HttpResponse(status=401)

@login_required
def device_detail(request, id):
    if request.method == 'GET':
        device = get_object_or_404(Device, id=id)
        return JsonResponse(serializeDevice(device))
    elif request.method == 'POST':
        deviceId = request.POST['deviceId']
        sensors = request.POST['sensors']
        return 'TODO'
