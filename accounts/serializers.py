from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from django.contrib.auth.password_validation import validate_password
import uuid
# from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'uid', 'created', 'updated')
        read_only_fields = ('id', 'uid', 'created', 'updated')

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.uid = str(uuid.uuid4())
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'})
class ReactivateAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    admin_id = serializers.CharField()
    admin_password = serializers.CharField(style={'input_type': 'password'})
    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError('User does not exist')
        return value
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'}, required=True)
    new_password = serializers.CharField(style={'input_type': 'password'}, required=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "新しいパスワードと確認用パスワードが一致しません。"})
        return data
class CompletelyDeleteAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("The two password fields didn't match.")
        validate_password(data['new_password'])
        return data