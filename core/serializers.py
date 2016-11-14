def serializeDevice(device):
    return {
        'id': device.id,
        'name': device.name,
        'deviceType': device.deviceType,
        'isAwake': device.isAwake,
        'vendor': device.vendor,
        'brand': device.brand,
        'product': device.product,
        'image': device.image
    }

def serializeSensor(sensor):
    return {
        'id': sensor.id,
        'sensorId': sensor.sensorId,
        'type': sensor.type,
        'name': sensor.name,
        'title': sensor.title,
        'icon': sensor.icon,
        'tags': sensor.tags,
        'scale': sensor.scale,
        'valueType': sensor.valueType
    }

def serializeSensorValue(sensorvalue):
    return {
        'value': sensorvalue.value,
        'updated': sensorvalue.updated
    }
