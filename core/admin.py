from django.contrib import admin
from core.models import Controller, Device, ApiUser, DeviceBattery, DeviceDescription, Sensor, SensorValue, Actuator,\
    ActuatorValue, Language, Message

def sensor_name(obj):
    return obj.sensor.__str__()

def value_with_scale(obj):
    return "%s %s" % (obj.value, obj.sensor.scale)
value_with_scale.short_description = 'Value'

class SensorInline(admin.TabularInline):
    model = Sensor

def device_name(obj):
    return obj.name or obj.deviceType
device_name.short_description = 'Name'

def device_user(obj):
    return obj.controller.apiUser.user.__str__()
device_user.short_description = 'User'

class DeviceAdmin(admin.ModelAdmin):
    list_display = (device_name, device_user)
    inlines = [
        SensorInline,
    ]

class DeviceInline(admin.TabularInline):
    model = Device

def controller_user(obj):
    return obj.apiUser.user.__str__()
controller_user.short_description = 'User'

class ControllerAdmin(admin.ModelAdmin):
    list_display = ('name', controller_user)
    inlines = [
        DeviceInline,
    ]

class SensorValueAdmin(admin.ModelAdmin):
    list_display = (sensor_name, value_with_scale, 'updated')
    ordering = ('-updated',)

class ControllerInline(admin.TabularInline):
    model = Controller

class ApiUserAdmin(admin.ModelAdmin):
    inlines = [
        ControllerInline,
    ]

def actuator_name(obj):
    return obj.actuator.__str__()

def actuator_value_with_scale(obj):
    return "%s %s" % (obj.value, obj.actuator.scale)
actuator_value_with_scale.short_description = 'Value'

class ActuatorValueAdmin(admin.ModelAdmin):
    list_display = (actuator_name, actuator_value_with_scale, 'updated')
    ordering = ('-updated',)

# Register your models here.
admin.site.register(Controller, ControllerAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(ApiUser, ApiUserAdmin)
admin.site.register(DeviceBattery)
admin.site.register(DeviceDescription)
admin.site.register(Sensor)
admin.site.register(SensorValue, SensorValueAdmin)
admin.site.register(Actuator)
admin.site.register(ActuatorValue, ActuatorValueAdmin)
admin.site.register(Language)
admin.site.register(Message)
