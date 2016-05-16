from django.db import models


class Device(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    deviceId = models.PositiveIntegerField()
    name = models.CharField(max_length=255, blank=True, default='')
    xml = models.CharField(max_length=255, blank=True, default='')
    deviceType = models.CharField(max_length=255, blank=True, default='')
    isAwake = models.BooleanField(default=False)
    vendor = models.CharField(max_length=255, blank=True, default='')
    brand = models.CharField(max_length=255, blank=True, default='')
    product = models.CharField(max_length=255, blank=True, default='')
    image = models.TextField(blank=True)


    class Meta:
        ordering = ('created',)