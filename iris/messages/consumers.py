from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from knox.auth import TokenAuthentication

knoxAuth = TokenAuthentication()


class MessageConsumer(WebsocketConsumer):
    def connect(self):
        # print(self.scope)
        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_id + '_cinema',
        #     self.channel_name
        # )

        # user, auth_token = knoxAuth.authenticate_credentials()
        # self.scope['user'] = user
        self.accept()
