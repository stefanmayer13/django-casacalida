from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, logout as auth_logout
from django.http import JsonResponse
from core.models import Controller, Device, Message, Language, ApiUser
from django.contrib.auth import get_user_model
from django.utils.decorators import available_attrs
from core.serializers import serializeDevice
from datetime import datetime, timedelta
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers

import jwt

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

def jwt_authenticated(function=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            auth = request.META.get('HTTP_AUTHORIZATION', False)
            if auth:
                try:
                    payload = jwt.decode(auth[6:], JWT_SECRET, algorithms=[JWT_ALGORITHM])
                    userid = payload.get('user', False)
                    return view_func(userid, request, *args, **kwargs)
                except jwt.ExpiredSignatureError:
                    pass
            return HttpResponse(status=401)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator

@ensure_csrf_cookie
def csrf(request):
    return HttpResponse(status=200)

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        nexturl = request.POST.get('next', False)
        if not (username and password):
            errormessage = "Please enter username and password."
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    payload = {
                        'user': user.id,
                        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                    }
                    jwt_token = jwt.encode(payload, 'secret', algorithm=JWT_ALGORITHM)
                    return JsonResponse({
                        'token': jwt_token.decode('utf-8'),
                        'next': nexturl
                    })
                else:
                    errormessage = "This user account ist not active."
            else:
                errormessage = "Username or password wrong."
        return JsonResponse({
            'error': errormessage,
            'next': nexturl
        }, status=401)
    else:
        response = HttpResponse(status=404)
        response['csrf_token'] = csrf.get_token()
        return response

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('core:index'))


@jwt_authenticated
def device_list(userid, request):
    user = get_user_model().objects.filter(id=userid)
    apiUser = ApiUser.objects.get(user=user)
    controllers = Controller.objects.filter(apiUser=apiUser)
    devices = Device.objects.filter(controller__in=controllers).values('id', 'name', 'deviceType', 'vendor')
    return JsonResponse({"devices": list(devices)})

@jwt_authenticated
def device_detail(userid, request, deviceid):
    if request.method == 'GET':
        device = get_object_or_404(Device, id=deviceid)
        return JsonResponse(serializeDevice(device))
    elif request.method == 'POST':
        print(request.POST)

        return 'TODO'

def messages(request, language):
    if request.method == 'GET':
        try:
            language_id = Language.objects.get(abbreviation=language)
        except Language.DoesNotExist:
            return HttpResponse(status=404)
        languages = list(Language.objects.all().values('abbreviation', 'language'))
        message_list = list(Message.objects.filter(language=language_id).values('key', 'text'))
        message_dict = {}
        for message in message_list:
            key = message.pop('key')
            message_dict[key] = message['text']
        return JsonResponse({"languages": languages, "language": language, "messages": message_dict})
    else:
        return HttpResponse(status=404)