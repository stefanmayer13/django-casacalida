from channels import Group
from channels.sessions import enforce_ordering
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http

# Connected to websocket.connect
@enforce_ordering(slight=True)
@channel_session_user_from_http
def ws_connect(message):
    print(message.user)
    Group("chat").add(message.reply_channel)

# Connected to websocket.receive
@enforce_ordering(slight=True)
@channel_session_user
def ws_message(message):
    print(message.user)
    Group("chat").send({
        "text": "%s %s" % (message.user.username, message.content['text']),
    })

# Connected to websocket.disconnect
@enforce_ordering(slight=True)
@channel_session_user
def ws_disconnect(message):
    Group("chat").discard(message.reply_channel)
