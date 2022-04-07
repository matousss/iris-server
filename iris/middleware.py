import knox
from asgiref.sync import sync_to_async
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from knox.auth import TokenAuthentication

# https://gist.github.com/rluts/22e05ed8f53f97bdd02eafdf38f3d60a
# channels.auth.AuthMiddlewareStack
from rest_framework.exceptions import AuthenticationFailed


class ChannelsTokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    knoxAuth = TokenAuthentication();

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            try:
                token_name, token_key = headers[b'authorization'].split()
                if token_name == b'Token':
                    user, auth_token = await sync_to_async(self.knoxAuth.authenticate_credentials)(token_key)
                    scope['user'] = user
                    close_old_connections()
            except AuthenticationFailed:
                scope['user'] = AnonymousUser()
        return await self.inner(scope, receive, send)


def ChannelsAuthMiddleware(inner):
    return ChannelsTokenAuthMiddleware(AuthMiddlewareStack(inner))
