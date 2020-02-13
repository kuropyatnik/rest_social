from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_social.settings import SECRET_KEY
from .models import User
import jwt


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if request.headers.get('token'):
            payload = jwt.decode(bytes(request.headers.get('token'), 'utf-8'), SECRET_KEY)
            try:
                user_id = payload['id']
                username = payload['username']
                user = User.objects.get(username=username, id=user_id)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed()
        else:
            raise exceptions.NotAuthenticated()

        return (user, None)