from rest_framework import serializers
from .models import User, Wallet


class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'type', 'password']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=70, min_length=7, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'type', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class WalletSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Wallet
        fields = ['id', 'currency', 'balance']
