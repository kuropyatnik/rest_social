from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.contrib.auth.hashers import make_password
from django.db.models import Value, IntegerField
from rest_framework.views import status
from rest_social.settings import SECRET_KEY
from .serializers import UserSerializer, LoginSerializer, PostSerializer, PostsOutputSerializer, PostOutputSerializer, MarkSerializer
from .models import User, Post
from .authentication import TokenAuthentication
from .pagination import CustomPagination
import jwt, json


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


@api_view(['POST'])
@permission_classes([AllowAny, ])
def login_view(request):
    try:
        serialized = LoginSerializer(data=request.data, many=False)
        if serialized.is_valid():
            user = User.objects.get(username=serialized.validated_data['username'])
            if not user.check_password(serialized.validated_data['password']):
                raise User.DoesNotExist
            payload = {
                'id': user.id,
                'username': user.username
            }
            jwt_token = {'token': jwt.encode(payload, SECRET_KEY).decode('utf-8')}
            data = jwt_token
            status_code = status.HTTP_200_OK
        else:
            data = {key: str(value[0]) for key, value in serialized.errors.items()}
            status_code = status.HTTP_400_BAD_REQUEST
    except User.DoesNotExist:
        data = {'Error': 'Wrong user credentials!'}
        status_code = status.HTTP_400_BAD_REQUEST
    except ParseError:
        data = {'Error': 'Bad request'}
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(data=data, status=status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def add_post_view(request):
    authentication_classes(TokenAuthentication, )
    user_data = jwt.decode(bytes(request.headers.get('token'), 'utf-8'), SECRET_KEY, ['HS256'])
    user = User.objects.get(username=user_data['username'])
    try:
        serialized_post = PostSerializer(data=request.data, context={'request': request})
        if serialized_post.is_valid():
            title = str(serialized_post.initial_data['title'])
            content = str(serialized_post.initial_data['content'])
            if title.strip() == '' or content.strip() == '':
                data = {'Error': 'At least one required field is empty'}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                Post.objects.create(creator=user, title=title, content=content)
                data = {"Result": "Post was added"}
                status_code = status.HTTP_200_OK
        else:
            data = {key: str(value[0]) for key, value in serialized_post.errors.items()}
            status_code = status.HTTP_400_BAD_REQUEST
    except Exception as e:
        data = {'Error': 'Bad request ' + str(e)}
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(data=data, status=status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_all_posts_view(request):
    authentication_classes(TokenAuthentication, )
    user_data = jwt.decode(bytes(request.headers.get('token'), 'utf-8'), SECRET_KEY, ['HS256'])
    user = User.objects.get(username=user_data['username'])
    paginator = CustomPagination()
    posts = Post.objects.all()
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostsOutputSerializer(result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_post_view(request, pk):
    authentication_classes(TokenAuthentication, )
    user_data = jwt.decode(bytes(request.headers.get('token'), 'utf-8'), SECRET_KEY, ['HS256'])
    user = User.objects.get(username=user_data['username'])
    try:
        if Post.objects.get(id=pk) is not None:
            post = Post.objects.get(id=pk)
            like_value = 1 if user in post.likes.all() else 0
            serializer = PostOutputSerializer(post, many=False, context={'request': request})
            data = serializer.data
            data['like'] = like_value
            status_code = status.HTTP_200_OK

        else:
            data = {'Error': 'Post with id "{0}" does not exist'.format(pk)}
            status_code = status.HTTP_400_BAD_REQUEST
    except Exception as e:
        data = {'Error': 'Bad request ' + str(e)}
        status_code = status.HTTP_400_BAD_REQUEST

    return Response(data=data, status=status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def set_mark_view(request):
    authentication_classes(TokenAuthentication, )
    user_data = jwt.decode(bytes(request.headers.get('token'), 'utf-8'), SECRET_KEY, ['HS256'])
    user = User.objects.get(username=user_data['username'])

    try:
        serialized = MarkSerializer(data=request.data, context={'request': request})
        if serialized.is_valid():

            mark_data = serialized.data

            post_id = int(mark_data['post_id'])
            like = int(mark_data['like'])
            unlike = int(mark_data['unlike'])

            post = Post.objects.get(id=post_id)

            if like > unlike:
                post.likes.add(user)

            else:
                if user in post.likes.all():
                    post.likes.remove(user)

            data = {"Result": "Mark was successfully changed"}
            status_code = status.HTTP_201_CREATED
        else:
            data = {key: str(value[0]) for key, value in serialized.errors.items()}
            status_code = status.HTTP_400_BAD_REQUEST
    except Exception as e:
        data = {'Error': 'Bad request \n' + str(e)}
        status_code = status.HTTP_400_BAD_REQUEST
    return Response(data=data, status=status_code)
