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

class Device(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deviceId = models.PositiveIntegerField()
    name = models.CharField(max_length=255, blank=True, default='')
    xml = models.TextField(blank=True, default='')
    deviceType = models.CharField(max_length=255, blank=True, default='')
    isAwake = models.BooleanField(default=False)
    vendor = models.CharField(max_length=255, blank=True, default='')
    brand = models.CharField(max_length=255, blank=True, default='')
    product = models.CharField(max_length=255, blank=True, default='')
    image = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'devices'

    def __str__(self):
        return self.name