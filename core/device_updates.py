from core.models import Controller, Device, DeviceBattery, DeviceDescription, Sensor, SensorValue, Actuator, ActuatorValue

import datetime
import pytz


def full_update(user, controllers):
    for controller in controllers:
        try:
            controller_model = Controller.objects.get(apiUser=user, name=controller['name'])
        except Controller.DoesNotExist:
            controller_model = Controller.objects.create(apiUser=user, name=controller['name'])
        devices = controller['devices']
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
                if sensor.get('deviceType', '') == 'sensor':
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

                    if sensor.get('value'):
                        SensorValue.objects.create(sensor=device_sensor, value=sensor.get('value'),
                            updated=datetime.datetime.fromtimestamp(sensor.get('lastUpdate'), tz=pytz.UTC))

                elif sensor.get('deviceType', '') == 'actuator':
                    try:
                        device_actuator = Actuator.objects.get(device=device_model, actuatorId=sensor.get('key'),
                                                           commandClass=sensor.get('commandClass'))
                        device_actuator.type = sensor.get('type', '')
                        device_actuator.name = sensor.get('name', '')
                        device_actuator.title = sensor.get('title', '')
                        device_actuator.icon = sensor.get('icon', '')
                        device_actuator.tags = sensor.get('tags', '')
                        device_actuator.scale = sensor.get('scale', '')
                        device_actuator.valueType = sensor.get('valueType', '')
                        device_actuator.save()
                    except Actuator.DoesNotExist:
                        device_actuator = Actuator.objects.create(device=device_model, actuatorId=sensor.get('key'),
                                                              commandClass=sensor.get('commandClass', ''),
                                                              type=sensor.get('type', ''),
                                                              name=sensor.get('name', ''),
                                                              title=sensor.get('title', ''),
                                                              icon=sensor.get('icon', ''),
                                                              tags=sensor.get('tags', ''),
                                                              scale=sensor.get('scale', ''),
                                                              valueType=sensor.get('valueType', ''))

                    ActuatorValue.objects.create(actuator=device_actuator, value=sensor.get('value'),
                                           updated=datetime.datetime.fromtimestamp(sensor.get('lastUpdate'),
                                                                                   tz=pytz.UTC))


def incremental_update(user, controllers):
    for controller in controllers:
        controller_model = Controller.objects.get(apiUser=user, name=controller['name'])
        for sensor in controller['sensors']:
            device_model = Device.objects.get(controller=controller_model, deviceId=sensor['deviceId'])
            if sensor['sensor']['deviceType'] == 'sensor':
                device_sensor = Sensor.objects.get(device=device_model, sensorId=sensor['sensor']['key'],
                                                   commandClass=sensor['sensor']['commandClass'])
                SensorValue.objects.create(sensor=device_sensor, value=sensor['sensor']['value'],
                                           updated=datetime.datetime.fromtimestamp(
                                               sensor['sensor']['lastUpdate'],
                                               tz=pytz.UTC))
            elif sensor['sensor']['deviceType'] == 'actuator':
                device_actuator = Actuator.objects.get(device=device_model, actuatorId=sensor['sensor']['key'],
                                                   commandClass=sensor['sensor']['commandClass'])
                ActuatorValue.objects.create(actuator=device_actuator, value=sensor['sensor']['value'],
                                           updated=datetime.datetime.fromtimestamp(
                                               sensor['sensor']['lastUpdate'],
                                               tz=pytz.UTC))
