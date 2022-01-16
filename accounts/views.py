from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import User, Wallet
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import requests
from decouple import config
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
        return obj.type == 'Elite'


class Register(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    wallet_serializer_class = WalletSerializer

    def post(self, request):
        user_data = {
            'email': request.data.get('email'),
            'username': request.data.get('username'),
            'password': request.data.get('password'),
            "type": request.data.get('type'),
        }
        user_serializer = self.serializer_class(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        user = User.objects.get(email=user_data.get('email'))
        if not user.type == 'Admin':
            wallet_data = {
                'currency': request.data.get('currency').upper(),
                'balance': request.data.get('balance'),
                'user_id': user.id,
            }
            wallet_serializer = self.wallet_serializer_class(data=wallet_data)
            if not wallet_serializer.is_valid():
                return Response({'error': 'Wallet creation failed'}, status=status.HTTP_400_BAD_REQUEST)
            wallet_serializer.save()
            data = {
                'wallet': wallet_serializer.data
            }
            return Response(data)
        return Response(user_serializer.data)


class PromoteDemoteUser(APIView):
    permission_classes = [IsAdminOnlyOrPost]

    def put(self, request, pk):
        auth_user = User.objects.get(email=request.user)
        if self.check_object_permissions(request, auth_user):
            type = 'Noob'
            user = User.objects.get(id=pk)
            if not user:
                return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
            if user.type == 'Noob':
                type = 'Elite'
            if user.type == 'Elite':
                type == 'Noob'
            serializer = UserSerializer(user, {'type': type}, partial=True)
            if not serializer.is_valid():
                return Response({'error': 'User update failed'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)


class Login(APIView):
    def post(self, request, format=None):
        user = authenticate(email=request.data.get('email'), password=request.data.get('password'))
        if user:
            try:
                token = Token.objects.get(user=user)
            except Exception:
                token = Token.objects.create(user=user)
            serializer = UserSerializer(user)
            return Response({'user': serializer.data, 'token': token.key})
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class WalletListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOnlyElite]
    serializer_class = WalletSerializer

    def get(self, request):
        wallets = Wallet.objects.all()
        serializer = self.serializer_class(wallets, many=True)

        return Response(serializer.data)

    def post(self, request):
        auth_email = request.user
        user = User.objects.get(email=auth_email)

        if self.check_object_permissions(request, user):
            return Response({'error': 'User cannot have multiple wallets'}, status=status.HTTP_403_FORBIDDEN)
        try:
            Wallet.objects.get(user_id=user.id, currency=request.data.get("currency"))
            return Response({'error': 'Wallet already exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            pass
        request_data = {
            "currency": request.data.get('currency'),
            "balance": request.data.get('balance'),
            "user_id": user.id
        }
        serializer = self.serializer_class(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TransactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    def get_valid_currency(self, default, to, amount):
        if default == to:
            return amount
        fixer_api_key = config('FIXER_API_KEY')

        api_url = f"http://data.fixer.io/api/latest?access_key={fixer_api_key}"
        try:
            results = requests.get(api_url)
            data = results.json()
            rates = data.get('rates')
            request_value = rates.get(to)
            default_value = rates.get(default)

            final_value = amount * default_value / request_value
            return final_value
        except Exception:
            return Response({'error': "Error occurred"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk = request.data.get('id', '')
        auth_email = request.user
        user = User.objects.get(email=auth_email)
        wallet = Wallet.objects.get(id=pk)
        result = 0
        amount = request.data.get('balance')
        if not user.type == 'Admin':
            wallet = Wallet.objects.get(id=pk, user_id=user.id)
        if not wallet:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.data.get('action') == 'withdraw':
            if user.type == 'Admin':
                return Response({'error': "User cannot withdraw from any wallet"}, status=status.HTTP_403_FORBIDDEN)
            if wallet.balance < amount:
                return Response({'error': "Insufficient funds"}, status=status.HTTP_403_FORBIDDEN)
            result = wallet.balance - amount
        if request.data.get('action') == 'fund':
            result = wallet.balance + amount
        serializer = self.serializer_class(wallet, {'balance': result}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangeDefaultWalletView(APIView):
    serializer_class = WalletSerializer

    def put(self, request):
        pk = request.data.get('id', '')
        wallet = Wallet.objects.filter(user_id=pk).first()
        serializer = self.serializer_class(wallet, {'currency': request.data.get('currency')}, partial=True)
        if not serializer.is_valid():
            return Response({'error': 'Wallet update failed'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)
