from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.models import Device, ApiUser
from core.serializers import serializeDevice
from django.views.decorators.csrf import csrf_exempt
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

# ################################################-API-##############################################################


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
        print(request.POST)

        return 'TODO'


def api_check(request):
    token = request.META.get('HTTP_TOKEN', None)
    if request.method == 'GET' and token is not None:
        try:
            ApiUser.objects.get(token=token)
            return HttpResponse(status=200)
        except ApiUser.DoesNotExist:
            pass
    return HttpResponse(status=401, content='Authentication failed')

@csrf_exempt
def api_full_update(request):
    token = request.META.get('HTTP_TOKEN', None)
    if request.method == 'POST' and token is not None:
        try:
            user = ApiUser.objects.get(token=token)
            devices = json.loads(request.body.decode('utf-8'))
            for device in devices:
                try:
                    device_model = Device.objects.get(owner=user.user, deviceId=device['deviceId'])
                    device_model.name = device.get('name', '')
                    device_model.xml = device.get('xml', '')
                    device_model.deviceType = device.get('deviceType', '')
                    device_model.isAwake = device.get('isAwake', False)
                    device_model.vendor = device.get('vendor', '')
                    device_model.brand = device.get('brandName', '')
                    device_model.product = device.get('productName', '')
                    device_model.image = device.get('deviceImage', '')
                    device_model.save()
                except:
                    Device.objects.create(owner=user.user, deviceId=device['deviceId'], name=device.get('name', ''),
                                          xml=device.get('xml', ''), deviceType=device.get('deviceType', ''),
                                          isAwake=device.get('isAwake', False), vendor=device.get('vendor', ''),
                                          brand=device.get('brandName', ''), product=device.get('productName', ''),
                                          image=device.get('deviceImage', ''))

            return HttpResponse(status=200)
        except ApiUser.DoesNotExist:
            pass
    return HttpResponse(status=401, content='Authentication failed')


@csrf_exempt
def api_incremental_update(request):
    token = request.META.get('HTTP_TOKEN', None)
    if request.method == 'POST' and token is not None:
        try:
            user = ApiUser.objects.get(token=token)
            devices = json.loads(request.body.decode('utf-8'))
            for device in devices:
                try:
                    device_model = Device.objects.get(owner=user.user, deviceId=device['deviceId'])
                    device_model.save()
                except:
                    Device.objects.create(owner=user.user, deviceId=device['deviceId'], name=device.get('name', ''),
                                          xml=device.get('xml', ''), deviceType=device.get('deviceType', ''),
                                          isAwake=device.get('isAwake', False), vendor=device.get('vendor', ''),
                                          brand=device.get('brandName', ''), product=device.get('productName', ''),
                                          image=device.get('deviceImage', ''))

            return HttpResponse(status=200)
        except ApiUser.DoesNotExist:
            pass
    return HttpResponse(status=401, content='Authentication failed')
