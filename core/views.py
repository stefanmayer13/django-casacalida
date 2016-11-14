from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels import Channel
from core.models import Controller, Device, ApiUser, DeviceBattery, DeviceDescription, Sensor, SensorValue, Actuator, ActuatorValue
from core.serializers import serializeDevice
import json
import datetime
import pytz
import time

def index(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    return render(request, 'core/index.html', {
        'user': user
    })


def login(request):
    if request.user.is_authenticated():
        nexturl = request.GET.get('next', '')
        redirect = nexturl if nexturl else reverse('core:dashboard')
        return HttpResponseRedirect(redirect)
    elif request.method == 'GET':
        return render(request, 'core/login.html', {
            'next': request.GET.get('next', '')
        })
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not (username and password):
            errormessage = "Please enter username and password."
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    nexturl = request.POST.get('next', False)
                    redirect = nexturl if nexturl else reverse('core:dashboard')
                    return HttpResponseRedirect(redirect)
                else:
                    errormessage = "This user account ist not active."
            else:
                errormessage = "Username or password wrong."
        return render(request, 'core/login.html', {
            'error_message': errormessage,
            'next': request.GET.get('next', ''),
        })


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('core:index'))


@login_required
def dashboard(request):
    try:
        api_user = ApiUser.objects.get(user=request.user)
        controllers = Controller.objects.filter(apiUser=api_user)
        devices = Device.objects.filter(controller__in=controllers)
        sensors = Sensor.objects.filter(device__in=devices)
        actuators = Actuator.objects.filter(device__in=devices)
        sensorvalues = SensorValue.objects.filter(sensor__in=sensors).order_by('-updated')
        actuatorvalues = ActuatorValue.objects.filter(actuator__in=actuators).order_by('-updated')
        viewdata = {'controllers': []}
        for controller in controllers:
            devicesDict = []
            controllerDevices = devices.filter(controller=controller)
            for device in controllerDevices:
                sensorsDict = []
                deviceSensors = sensors.filter(device=device)
                for sensor in deviceSensors:
                    filtered_sensor_values = sensorvalues.filter(sensor=sensor)
                    if len(filtered_sensor_values) > 0:
                        sensorValue = filtered_sensor_values[0].value
                    else:
                        sensorValue = ''
                    sensorsDict.append({
                        'name': sensor.title or sensor.name,
                        'value': sensorValue + ' ' + sensor.scale,
                    })
                actuatorsDict = []
                deviceActuators = actuators.filter(device=device)
                for actuator in deviceActuators:
                    filtered_actuator_values = actuatorvalues.filter(actuator=actuator)
                    if len(filtered_actuator_values) > 0:
                        actuatorValue = filtered_actuator_values[0].value
                    else:
                        actuatorValue = ''
                    actuatorsDict.append({
                        'name': actuator.title or actuator.name,
                        'value': actuatorValue + ' ' + actuator.scale,
                    })
                devicesDict.append({
                    'name': device.name,
                    'brand': device.brand,
                    'vendor': device.vendor,
                    'sensors': sensorsDict,
                    'actuators': actuatorsDict,
                })
            viewdata['controllers'].append({
                'name': controller.name,
                'devices': devicesDict
            })
    except ApiUser.DoesNotExist:
        viewdata = False
        devices = False
        sensors = False
    return render(request, 'core/dashboard.html', {
        'viewdata': viewdata,
        'devices': devices,
        'sensors': sensors,
    })

# ################################################-API-##############################################################

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
            controllers = json.loads(request.body.decode('utf-8'))
            for controller in controllers:
                try:
                    controller_model = Controller.objects.get(owner=user.user, name=controller['name'])
                except Controller.DoesNotExist:
                    controller_model = Controller.objects.create(owner=user.user, name=controller['name'])
                devices = controller['devices'];
                for device in devices:
                    battery = device.get('battery', None)
                    try:
                        device_model = Device.objects.get(controller=controller_model, deviceId=device['deviceId'])
                        device_model.name = device.get('name', '')
                        device_model.xml = device.get('xml', '')
                        device_model.deviceType = device.get('deviceType', '')
                        device_model.isAwake = device.get('isAwake', False)
                        device_model.vendor = device.get('vendor', '')
                        device_model.brand = device.get('brandName', '')
                        device_model.product = device.get('productName', '')
                        device_model.image = device.get('deviceImage', '')
                        device_model.protocol = device.get('protocol', '')
                    except Device.DoesNotExist:
                        device_model = Device.objects.create(controller=controller_model, deviceId=device['deviceId'],
                                                             name=device.get('name', ''),
                                                             xml=device.get('xml', ''),
                                                             deviceType=device.get('deviceType', ''),
                                                             isAwake=device.get('isAwake', False),
                                                             vendor=device.get('vendor', ''),
                                                             brand=device.get('brandName', ''),
                                                             product=device.get('productName', ''),
                                                             image=device.get('deviceImage', ''),
                                                             protocol=device.get('protocol', ''),
                                                             batteryType=device.get('batteryType', ''),
                                                             batteryCount=device.get('batteryCount', 0))
                    print(battery)
                    if battery is not None and battery.get('type', None) is not None:
                        device_model.batteryType = battery.get('type')
                        device_model.batteryCount = battery.get('count', 0)
                        DeviceBattery.objects.create(device=device_model, value=battery.get('value', 0))
                    device_model.save()

                    descriptions = device.get('description', None)
                    if descriptions is not None:
                        for language, description in descriptions.items():
                            try:
                                device_description = DeviceDescription.objects.get(device=device_model, language=language)
                                device_description.description = description
                            except DeviceDescription.DoesNotExist:
                                DeviceDescription.objects.create(device=device_model, language=language, description=description)

                    sensors = device['sensors']
                    for sensor in sensors:
                        try:
                            device_sensor = Sensor.objects.get(device=device_model, sensorId=sensor.get('key'),
                                                               commandClass=sensor.get('commandClass'))
                            device_sensor.type = sensor.get('type', '')
                            device_sensor.name = sensor.get('name', '')
                            device_sensor.title = sensor.get('title', '')
                            device_sensor.icon = sensor.get('icon', '')
                            device_sensor.tags = sensor.get('tags', '')
                            device_sensor.scale = sensor.get('scale', '')
                            device_sensor.valueType = sensor.get('valueType', '')
                            device_sensor.save()
                        except Sensor.DoesNotExist:
                            device_sensor = Sensor.objects.create(device=device_model, sensorId=sensor.get('key'),
                                                                  commandClass=sensor.get('commandClass', ''),
                                                                  type=sensor.get('type', ''),
                                                                  name=sensor.get('name', ''),
                                                                  title=sensor.get('title', ''),
                                                                  icon=sensor.get('icon', ''),
                                                                  tags=sensor.get('tags', ''),
                                                                  scale=sensor.get('scale', ''),
                                                                  valueType=sensor.get('valueType', ''))

                        SensorValue.objects.create(sensor=device_sensor, value=sensor.get('value'),
                                                   updated=datetime.datetime.fromtimestamp(sensor.get('lastUpdate'), tz=pytz.UTC))

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
            controllers = json.loads(request.body.decode('utf-8'))
            sendJobs = False
            for controller in controllers:
                try:
                    controller_model = Controller.objects.get(owner=user.user, name=controller['name'])
                    for sensor in controller['sensors']:
                        device_model = Device.objects.get(controller=controller_model, deviceId=sensor['deviceId'])
                        device_sensor = Sensor.objects.get(device=device_model, sensorId=sensor['sensor']['key'],
                                                           commandClass=sensor['sensor']['commandClass'])
                        SensorValue.objects.create(sensor=device_sensor, value=sensor['sensor']['value'],
                                                   updated=datetime.datetime.fromtimestamp(
                                                       sensor['sensor']['lastUpdate'],
                                                       tz=pytz.UTC))

                    if controller['name'] == 'iot':
                        sendJobs = True
                except Controller.DoesNotExist:
                    print('Problem with incremental update')
                    return HttpResponse(status=500, content='Problem with incremental update')

                return HttpResponse(status=200)
        except ApiUser.DoesNotExist:
            pass
    return HttpResponse(status=401, content='Authentication failed')


@login_required
def seton(request):
    Channel('actuator_action').send({
        'userId': request.user.id,
        'actuatorId': 'zway_3-0-38',
        'protocol': 'zwave',
        'value': 'on'
    })
    return HttpResponseRedirect(reverse('core:dashboard'))


@login_required
def setoff(request):
    Channel('actuator_action').send({
        'userId': request.user.id,
        'actuatorId': 'zway_3-0-38',
        'protocol': 'zwave',
        'value': 'off'
    })
    return HttpResponseRedirect(reverse('core:dashboard'))
