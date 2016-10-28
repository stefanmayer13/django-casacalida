from channels.routing import route
from core.consumers import ws_connect, ws_message, ws_disconnect, msg_actuator_action

channel_routing = [
    route("websocket.connect", ws_connect),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect),
    route("actuator_action", msg_actuator_action),
]
