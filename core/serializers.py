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

def serializeJob(job):
    return {
        'device': job.device,
        'type': job.type,
        'value': job.value
    }
