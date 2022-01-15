from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .models import User, Wallet
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token


from accounts.serializers import RegisterSerializer, UserSerializer, WalletSerializer

class IsAdminOnlyOrPost(permissions.BasePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST' or request.method in permissions.SAFE_METHODS:
            return True
        return obj.type == 'Admin'

class IsOnlyElite(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT' or request.method in permissions.SAFE_METHODS:
            return True
        return not obj.type == 'Noob' or obj.type == 'Admin'

class Register(APIView):
    serializer_class = RegisterSerializer
    wallet_serializer_class = WalletSerializer

    def post(self, request):
        user_data = {
            'email': request.data.get('email'),
            'username': request.data.get('username'),
            'password': request.data.get('password')
        }
        user_serializer = self.serializer_class(data=user_data)
        if not user_serializer.is_valid():
            return Response({ 'error': 'Registration failed' }, status=status.HTTP_400_BAD_REQUEST)
        user_serializer.save()
        user = user_serializer.data
        if not user.type == 'Admin':
            wallet_data = {
                'currency': request.data.get('currency').upper(),
                'value': request.data.get('value'),
                'user_id': user.id,
            }
            wallet_serializer = self.wallet_serializer_class(data=wallet_data)
            if not wallet_serializer.is_valid():
                return Response({ 'error': 'Wallet creation failed' }, status=status.HTTP_400_BAD_REQUEST)
            data = {
                'user': user,
                'wallet': wallet_serializer.data
            }
            return Response(data)
        return Response(user)

class PromoteDemoteUser(APIView):
    permission_classes=[IsAdminOnlyOrPost]
    def put(self, request, pk):
        auth_user = User.objects.get(email=request.user)
        if self.check_object_permissions(request, auth_user):
            type = 'Noob'
            user = User.objects.get(id=pk)
            if not user:
                return Response({ "error": "User does not exist" }, status=status.HTTP_404_NOT_FOUND)
            if user.type == 'Noob':
                type = 'Elite'
            if user.type == 'Elite':
                type == 'Noob'
            serializer = UserSerializer(user, { 'type': type }, partial=True)
            if not serializer.is_valid():
                return Response({ 'error': 'User update failed' }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)


class Login(APIView):
    def post(self, request, format=None):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if user:
            login(request, user)
            token = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({"user": serializer.data, "token": token.key})
        return Response({ "error": "User does not exist" }, status=status.HTTP_404_NOT_FOUND)

class WalletListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOnlyElite]
    serializer_class = WalletSerializer

    def post(self, request):
        auth_email = request.user
        user = User.objects.get(email=auth_email)

        if not self.check_object_permissions(request, user):
            return Response({ "error": "User cannot have multiple wallets" }, status=status.HTTP_403_FORBIDDEN)
        wallet = Wallet.objects.get(user_id=user.id, currency=request.data.get("currency"))
        if wallet:
            return Response({ "error": "Wallet already exist" }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({ 'error': 'Wallet creation failed' }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

class TransactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer
    def put(self, request, pk):
        auth_email = request.user
        user = User.objects.get(email=auth_email)
        wallet = Wallet.objects.get(id=pk)
        result = 0
        amount = request.data.get('amount')
        if not user.type == 'Admin':
            wallet = Wallet.objects.get(id=pk, user_id=user.id)
        if not wallet:
            return Response({ 'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.data.get('action') == 'withdraw':
            if user.type == 'Admin':
                return Response({ "error": "User cannot withdraw from any wallet" }, status=status.HTTP_403_FORBIDDEN)
            if wallet.balance < amount:
                return Response({ "error": "Insufficient funds" }, status=status.HTTP_403_FORBIDDEN)
            result = wallet.balance - amount
        if request.data.get('action') == 'fund':
            result = wallet.balance + amount
        serializer = self.serializer_class(wallet, { 'balance': result  }, partial=True)
        if not serializer.is_valid():
            return Response({ 'error': 'Transaction failed' }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

class ChangeDefaultWalletView(APIView):
    serializer_class = WalletSerializer

    def put(self, request, pk):
        wallet = Wallet.objects.filter(user_id=pk).first()
        serializer = self.serializer_class(wallet, { 'currency': request.data.get('currency') }, partial=True)
        if not serializer.is_valid():
            return Response({ 'error': 'Wallet update failed' }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)
            

        

