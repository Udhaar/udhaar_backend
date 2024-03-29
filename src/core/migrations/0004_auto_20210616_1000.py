# Generated by Django 3.2.4 on 2021-06-16 10:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='message',
        ),
        migrations.AddField(
            model_name='notification',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='core.transaction'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('NEW_RECEIVED_TRANSACTION', 'NEW_RECEIVED_TRANSACTION'), ('NEW_SENT_TRANSACTION', 'NEW_SENT_TRANSACTION'), ('ACCEPTED_TRANSACTION', 'ACCEPTED_TRANSACTION'), ('DECLINED_TRANSACTION', 'DECLINED_TRANSACTION')], max_length=255),
        ),
        migrations.AlterField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]
