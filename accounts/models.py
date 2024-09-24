from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
class CustomUser(AbstractUser):
    class Meta(AbstractUser.Meta):
        db_table = 'custom_user'
    
    id = models.BigAutoField(primary_key=True)
    uid = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created = models.DateTimeField('登録日時', auto_now_add=True)
    updated = models.DateTimeField('更新日時', auto_now=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    def deactivate(self):
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save()
    def __str__(self):
        return self.email