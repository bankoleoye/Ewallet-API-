from rest_framework import fields, serializers
from .models import User, Ewallet
from rest_framework.authtoken.models import Token


class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'types', 'password']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=70, min_length=7, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'types', 'password']
    def validate(self, attrs):
        attrs.get('email', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError('The username should be alphanumeric characters')
        return attrs
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


