import json
import sys
import traceback

from channels.sessions import channel_session
from channels import Group
from core.models import ApiUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from core.device_updates import full_update, incremental_update
from core.utils import getGroupFromUserId

data_handler = {
    'fullupdate': full_update,
    'update': incremental_update
}

# Connected to websocket.connect
@channel_session
def ws_connect(message):
    message.channel_session['user'] = False
    message.reply_channel.send({"accept": True})

# Connected to websocket.receive
@channel_session
def ws_message(message):
    data = json.loads(message.content['text'])
    if not message.channel_session['user'] and data['type'] == 'login':
        try:
            user = ApiUser.objects.get(token=data['token'])
            message.channel_session['user'] = data['token']
            user_group = getGroupFromUserId(user.user.id)
            Group(user_group).add(message.reply_channel)
            print("%s connected" % user.user.username)
            message.reply_channel.send({
                'text': json.dumps({
                    'type': 'login',
                    'user': user.user.username
                })
            })
            return
        except ApiUser.DoesNotExist:
            pass
    elif message.channel_session['user'] and data['type'] != 'login':
        userModel = get_user_model()
        try:
            user = ApiUser.objects.get(token=message.channel_session['user'])
            handler = data_handler.get(data['type'], lambda: "nothing")
            try:
                handler(user, data['data'])
            except:
                print(traceback.format_exc())
                print("User: " + str(user.id))
                print(data['data'])
                message.reply_channel.send({
                    "text": json.dumps({
                        'error': data['type'],
                    })
                })
            return
        except (AttributeError, userModel.DoesNotExist):
            pass
    message.reply_channel.send({
        "close": 'Wrong authentication'
    })

# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    userModel = get_user_model()
    try:
        user = ApiUser.objects.get(token=message.channel_session['user'])
        user_group = getGroupFromUserId(user.user.id)
        Group(user_group).discard(message.reply_channel)
    except (AttributeError, userModel.DoesNotExist):
        user = 'Anonymuous user'
    print("%s disconnected" % user)

def msg_actuator_action(message):
    user_id = message.content['userId']

    print("New action %s %s %s for user %s" % (message.content['protocol'], message.content['actuatorId'], message.content['value'], user_id))

    user = get_user_model().objects.get(id=user_id)
    protocol = message.content['protocol']
    actuator_id = message.content['actuatorId']
    value = message.content['value']
    user_group = getGroupFromUserId(user.id)
    Group(user_group).send({
        "text": json.dumps({
            'type': 'actuator',
            'id': actuator_id,
            'value': value,
            'protocol': protocol
        })
    })