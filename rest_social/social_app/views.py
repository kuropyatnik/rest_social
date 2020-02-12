from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.contrib.auth.hashers import make_password
from rest_framework.views import status
from .serializers import UserSerializer
from .models import User, Post


# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny, ])
def register_user_view(request):
    try:
        serialized = UserSerializer(data=request.data, context={'request': request})
        if serialized.is_valid():
            User.objects.create(username=serialized.validated_data['username'],
                                password=make_password(serialized.validated_data['password']),
                                email=serialized.validated_data['email'])
            data = {"Result": "User {0} was successfully added".format(serialized.data['username'])}
            status_code = status.HTTP_201_CREATED
        else:
            data = {key: str(value[0]) for key, value in serialized.errors.items()}
            status_code = status.HTTP_400_BAD_REQUEST
    except Exception as e:
        data = {'Error': 'Ensure in the username, password and email existence \n' + str(e)}
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(data=data, status=status_code)
