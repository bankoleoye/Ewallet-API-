from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token


from accounts.serializers import RegisterSerializer, UserSerializer

class Register(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({ 'error': 'Registration failed' }, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    def post(self, request, format=None):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if user:
            login(request, user)
            token = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({"user": serializer.data, "token": token.key})
        return Response({ "error": "User does not exist" }, status=status.HTTP_404_NOT_FOUND)