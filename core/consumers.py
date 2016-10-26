from channels.sessions import enforce_ordering, channel_session
from core.models import ApiUser
from django.contrib.auth import get_user_model
from core.device_updates import full_update, incremental_update

import json
import sys
import traceback

data_handler = {
    'fullupdate': full_update,
    'update': incremental_update
}

# Connected to websocket.connect
@enforce_ordering(slight=True)
@channel_session
def ws_connect(message):
    message.channel_session['user'] = False

# Connected to websocket.receive
@enforce_ordering(slight=True)
@channel_session
def ws_message(message):
    data = json.loads(message.content['text'])
    if not message.channel_session['user'] and data['type'] == 'login':
        try:
            user = ApiUser.objects.get(token=data['token'])
            message.channel_session['user'] = user.id
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
            user = ApiUser.objects.get(pk=message.channel_session['user'])
            handler = data_handler.get(data['type'], lambda: "nothing")
            try:
                handler(user, data['data'])
            except:
                print(traceback.format_exc())
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
@enforce_ordering(slight=True)
@channel_session
def ws_disconnect(message):
    userModel = get_user_model()
    try:
        user = ApiUser.objects.get(pk=message.channel_session['user'])
    except (AttributeError, userModel.DoesNotExist):
        user = 'Anonymuous user'
    print("%s disconnected" % user)
