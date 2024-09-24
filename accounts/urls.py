from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpAPIView.as_view(), name='signup'),  #新規アカウント作成
    path('signin/', views.SignInAPIView.as_view(), name='signin'),  #既存アカウントにログイン
    path('signout/', views.SignOutAPIView.as_view(), name='signout'),   #ログアウト
    path('profile/', views.ViewProfileAPIView.as_view(), name='profile'),   #ログイン中のユーザープロフィール
    path('resetpass/', views.ResetPasswordAPIView.as_view(), name='resetpass'), #パスワードリセットメール送信。パスワードを忘れましたか？
    path('changepass/', views.ChangePasswordAPIView.as_view(), name='changepass'),  #パスワードを変更する
    path('delete/', views.DeleteAccountAPIView.as_view(), name='delete'),   #アカウント削除。でも実は非アクティブ化
    path('comp-delete/', views.CompletelyDeleteAccountAPIView.as_view(), name='comp-delete'),   #非アクティブ化されたアカウントの完全削除
    path('reactivate/', views.ReactivateAccountAPIView.as_view(), name='reactivate'),   #アカウントの 再アクティベート
    path('password/reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm_api'),
    #http://localhost:8000/accounts/password/reset/key/7-cdv8ud-9f76c0e7882da17a26a46e2a6b846d2d/
    #この場合、uidb64 = 7, token =  cdv8ud-9f76c0e7882da17a26a46e2a6b846d2dとなる
    # よってurlはhttp://localhost:8000/api/password/reset/confirm/7/cdv8ud-9f76c0e7882da17a26a46e2a6b846d2d/というようになる

]