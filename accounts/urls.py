from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpAPIView.as_view(), name='signup'),
    path('login/', views.SignInAPIView.as_view(), name='login'),
    path('logout/', views.SignOutAPIView.as_view(), name='logout'),
    path('profile/', views.ViewProfileAPIView.as_view(), name='profile'),
]