from django.db import models
from django.conf import settings


class ApiUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    token = models.CharField(max_length=40, blank=False)

    def __str__(self):
        return self.token


class Controller(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'controllers'

    def __str__(self):
        return self.name


class Device(models.Model):
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deviceId = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    xml = models.TextField(blank=True, default='')
    deviceType = models.CharField(max_length=255, blank=True, default='')
    isAwake = models.BooleanField(default=False)
    vendor = models.CharField(max_length=255, blank=True, default='')
    brand = models.CharField(max_length=255, blank=True, default='')
    product = models.CharField(max_length=255, blank=True, default='')
    image = models.TextField(blank=True, default='')
    batteryType = models.CharField(max_length=255, blank=True, default='')
    batteryCount = models.PositiveIntegerField(blank=True, default=0)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'devices'

    def __str__(self):
        return self.name


class DeviceBattery(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    value = models.PositiveIntegerField()

    def __str__(self):
        return str(self.value) + '%' + ' ' + self.device.__str__()

class DeviceDescription(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    language = models.CharField(max_length=5, blank=False)
    description = models.TextField(blank=False)

    class Meta:
        ordering = ('language',)
        verbose_name_plural = 'descriptions'

    def __str__(self):
        return self.language + ': ' + self.description


class Sensor(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sensorId = models.CharField(max_length=255, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    commandClass = models.CharField(max_length=25, blank=True, default='')
    type = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    title = models.CharField(max_length=255, blank=True, default='')
    icon = models.CharField(max_length=255, blank=True, default='')
    tags = models.CharField(max_length=255, blank=True, default='')
    scale = models.CharField(max_length=100, blank=True, default='')
    valueType = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ('sensorId',)
        verbose_name_plural = 'sensors'

    def __str__(self):
        return self.title


class SensorValue(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, blank=True, default='')
    updated = models.DateTimeField()

    class Meta:
        ordering = ('-updated',)
        verbose_name_plural = 'sensorvalues'


class JobData(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device = models.CharField(max_length=255, blank=False)
    type = models.CharField(max_length=255, blank=False)
    value = models.CharField(max_length=255, blank=True, default='')
    done = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
