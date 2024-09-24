from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout,get_user_model,update_session_auth_hash,authenticate
from allauth.account import app_settings
from allauth.account.utils import complete_signup
from allauth.account.forms import ResetPasswordForm
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from .serializers import SignupSerializer, LoginSerializer, UserSerializer, DeleteAccountSerializer,ChangePasswordSerializer
from .serializers import PasswordResetConfirmSerializer,ReactivateAccountSerializer,CompletelyDeleteAccountSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

# アカウントを新規作成するView
class SignUpAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save(request)
            token, _ = Token.objects.get_or_create(user=user)
            complete_signup(request, user, app_settings.EMAIL_VERIFICATION, None)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 既に存在するアカウントでログインするapi
class SignInAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        # ユーザーが既にログインしているかチェック
        if request.user.is_authenticated:
            return Response({
                "error": "User is already logged in.",
                "user": UserSerializer(request.user).data
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # アカウントが無効化されていないかチェック
            if not user.is_active:
                return Response({
                    "error": "This account has been disabled."
                }, status=status.HTTP_403_FORBIDDEN)

            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })
        
        # バリデーションエラーの詳細を返す
        return Response({
            "error": "Invalid credentials.",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response({
                "error": "CSRF verification failed. Please refresh the page and try again."
            }, status=status.HTTP_403_FORBIDDEN)

        return super().handle_exception(exc)

# ログイン中のユーザーをサインアウト/ログアウトする API View
class SignOutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if request.auth:
            request.auth.delete()
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

# ログイン中のユーザー情報を返す
class ViewProfileAPIView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if email:
            form = ResetPasswordForm(data={'email': email})
            if form.is_valid():
                form.save(request)
                return Response({"detail": "パスワードリセットメールを送信しました。"}, status=status.HTTP_200_OK)
        return Response({"detail": "無効なメールアドレスです。"}, status=status.HTTP_400_BAD_REQUEST)

# ログイン中のアカウントのパスワードを変更する View
class ChangePasswordAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.validated_data['current_password']):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)  # セッションを更新して、ログアウトを防ぐ
                return Response({"detail": "パスワードが正常に変更されました。"}, status=status.HTTP_200_OK)
            return Response({"current_password": ["現在のパスワードが正しくありません。"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ログイン中のアカウントを削除するAPIView
class DeleteAccountAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteAccountSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.validated_data['password']):
                user.is_active = False
                user.save()
                logout(request)
                return Response({"detail": "アカウントが正常に削除されました。"}, status=status.HTTP_200_OK)
            return Response({"detail": "パスワードが正しくありません。"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ReactivateAccountAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ReactivateAccountSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            admin_id = serializer.validated_data['admin_id']
            admin_password = serializer.validated_data['admin_password']

            # 管理者の認証
            admin_user = authenticate(username=admin_id, password=admin_password)
            if not admin_user or not admin_user.is_staff:
                return Response({"detail": "管理者認証に失敗しました。"}, status=status.HTTP_403_FORBIDDEN)

            try:
                user = User.objects.get(email=email, is_active=False)
                user.is_active = True
                user.deactivated_at = None  # deactivated_at フィールドをクリア
                user.save()
                return Response({
                    "detail": "アカウントが再アクティベートされました。",
                    "user": {
                        "email": user.email,
                        "username": user.username,
                        "is_active": user.is_active,
                        "last_login": user.last_login
                    }
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"detail": "非アクティブなアカウントが見つかりません。"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # 管理者認証
        admin_id = request.query_params.get('admin_id')
        admin_password = request.query_params.get('admin_password')
        admin_user = authenticate(username=admin_id, password=admin_password)
        if not admin_user or not admin_user.is_staff:
            return Response({"detail": "管理者認証に失敗しました。"}, status=status.HTTP_403_FORBIDDEN)

        # 非アクティブなアカウントのリストを返す
        inactive_accounts = User.objects.filter(is_active=False).values('email', 'username', 'deactivated_at')
        return Response({
            "inactive_accounts": list(inactive_accounts),
            "total_count": inactive_accounts.count()
        })

class CompletelyDeleteAccountAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = CompletelyDeleteAccountSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email, is_active=False)
                
                # 非アクティブ化から7日以上経過しているか確認
                if user.deactivated_at and (timezone.now() - user.deactivated_at) >= timedelta(days=7):
                    user.delete()
                    return Response({"detail": "アカウントが完全に削除されました。"}, status=status.HTTP_200_OK)
                else:
                    days_left = 7 - (timezone.now() - user.deactivated_at).days
                    return Response({"detail": f"アカウントの完全削除まであと{days_left}日必要です。"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"detail": "指定された非アクティブアカウントが見つかりません。"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # 削除可能なアカウントのリストを返す
        deletion_threshold = timezone.now() - timedelta(days=7)
        deletable_accounts = User.objects.filter(
            is_active=False,
            deactivated_at__lte=deletion_threshold
        ).values('email', 'deactivated_at')
        
        return Response({
            "deletable_accounts": list(deletable_accounts),
            "total_count": deletable_accounts.count()
        })
class PasswordResetConfirmAPIView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            return Response({"detail": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()
                return Response({"detail": "Password has been reset successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)