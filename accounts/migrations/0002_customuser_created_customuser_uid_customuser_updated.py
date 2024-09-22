# Generated by Django 5.1.1 on 2024-09-22 04:28

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='登録日時'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customuser',
            name='uid',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='更新日時'),
        ),
    ]
