from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from mysite.settings import SESSION_COOKIE_AGE
User = get_user_model()

class CustomSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        user = getattr(request._request, 'user', None)
        if not user or not user.is_authenticated:
            return None

        last_login = user.last_login
        if last_login and (timezone.now() - last_login).total_seconds() > SESSION_COOKIE_AGE:
            # セッションが1時間を超えている場合、認証失敗
            raise AuthenticationFailed('Session has expired. Please log in again.')

        return (user, None)