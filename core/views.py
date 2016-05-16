from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from core.models import Device
from core.serializers import DeviceSerializer

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
    return render(request, 'core/dashboard.html')

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def device_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = Device.objects.all()
        serializer = DeviceSerializer(snippets, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = DeviceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def device_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        device = Device.objects.get(pk=pk)
    except Device.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = DeviceSerializer(device)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = DeviceSerializer(device, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        device.delete()
        return HttpResponse(status=204)