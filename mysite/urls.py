
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('accounts/',include('accounts.urls')),
    path('accounts/', include('allauth.urls')),  # 追加
    path('admin/', admin.site.urls),
]
