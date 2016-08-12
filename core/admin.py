from django.contrib import admin
from core.models import Controller, Device, ApiUser, DeviceBattery, DeviceDescription, Sensor, SensorValue, JobData

def sensor_name(obj):
    return obj.sensor.__str__()

def value_with_scale(obj):
    return "%s %s" % (obj.value, obj.sensor.scale)
value_with_scale.short_description = 'Value'

class SensorInline(admin.TabularInline):
    model = Sensor

class DeviceAdmin(admin.ModelAdmin):
    inlines = [
        SensorInline,
    ]

class DeviceInline(admin.TabularInline):
    model = Device

class ControllerAdmin(admin.ModelAdmin):
    inlines = [
        DeviceInline,
    ]

class SensorValueAdmin(admin.ModelAdmin):
    list_display = (sensor_name, value_with_scale, 'updated')
    ordering = ('-updated',)

# Register your models here.
admin.site.register(Controller, ControllerAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(ApiUser)
admin.site.register(DeviceBattery)
admin.site.register(DeviceDescription)
admin.site.register(Sensor)
admin.site.register(SensorValue, SensorValueAdmin)
admin.site.register(JobData)