from django.shortcuts import render
from registrations.models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User

@api_view(['GET'])
def index(request):
	return Response({'user':unicode(request.user)})


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((BasicAuthentication,))
def user_login(request, format=None):
    
	username = request.POST['username']
	password = request.POST['password']

	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			content = {
        'user': unicode(request.user),  # `django.contrib.auth.User` instance.
        'auth': unicode(request.auth),  # None
    }
		else:
			content = {'Error': 'Inactive'}

	else:
		content = {'Error':'Invalid credentials'}

	return Response(content)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_logout(request):
	logout(request)

	return HttpResponseRedirect('/api')

@api_view(['POST', 'GET'])
@permission_classes((AllowAny, ))
def create_user(request):

	print request.data
	user_serializer = UserSerializer(data=request.data)
	if user_serializer.is_valid():
		user_serializer.save()
		new_user = authenticate(username=request.data['username'],
                                    password=request.data['password'],
                                    )
		login(request, new_user)

		return Response(user_serializer.data, status=status.HTTP_201_CREATED)

	else:
		
		return Response(user_serializer._errors, status=status.HTTP_400_BAD_REQUEST)