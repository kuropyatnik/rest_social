from rest_framework import serializers
from .models import User
from django.core.exceptions import ValidationError
import django.contrib.auth.password_validation as validators
from rest_social.settings import EMAIL_HUNTER_API_KEY
import requests


class UserSerializer(serializers.ModelSerializer):
    def validate(self, data):

        # define custom exception
        class EmailVerificationError(Exception):
            pass

        user = User(**data)
        password = data.get('password')
        email = data.get('email')
        errors = dict()

        # Password validation
        try:
            validators.validate_password(password=password, user=User)

        # the exception raised here is different than serializers.ValidationError
        except ValidationError as e:
            errors['password'] = list(e.messages)

        # Email verification at emailhunter.co
        try:
            response = requests.get('https://api.hunter.io/v1/verify',
                                    params={'email': email, 'api_key': EMAIL_HUNTER_API_KEY}).json()

            if (response['status'] == 'error') or (
                    response['status'] == 'success' and response['result'] == 'undeliverable'):
                raise EmailVerificationError
        # the exception raised here is custom
        except EmailVerificationError as e:
            errors['email'] = 'Email is undeliverable'

        # Email existing check
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")

        if errors:
            raise ValidationError(errors)

        return super(UserSerializer, self).validate(data)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
