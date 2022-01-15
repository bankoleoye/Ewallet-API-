from rest_framework import fields, serializers
from .models import User, Wallet
from rest_framework.authtoken.models import Token


class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'types', 'password']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=70, min_length=7, write_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'types', 'password']
    def validate(self, attrs):
        attrs.get('email', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError('The username should be alphanumeric characters')
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
    def validate(self, attrs):
        if not attrs.get('currency') or not attrs.get('balance'):
            raise serializers.ValidationError('Enter all wallet credentials')
        if not attrs.get('balance').isnumeric():
            raise serializers.ValidationError('Balance must be a number')
        return super().validate(attrs)
