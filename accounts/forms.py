# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import get_user_model
# from allauth.account.forms import ResetPasswordForm as AllauthResetPasswordForm

# CustomUser = get_user_model()


# class SignupForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         fields = ('username', 'email', 'password')

# class CustomResetPasswordForm(AllauthResetPasswordForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # 不要なフィールドを削除
#         if 'username' in self.fields:
#             del self.fields['username']

#     def save(self, request, **kwargs):
#         # 元のsaveメソッドを呼び出す
#         return super().save(request, **kwargs)