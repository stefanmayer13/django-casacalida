from rest_framework import serializers
from core.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('pk', 'deviceId', 'name', 'xml', 'deviceType', 'isAwake', 'vendor', 'brand', 'product', 'image')
