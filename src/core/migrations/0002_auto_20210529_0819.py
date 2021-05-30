# Generated by Django 3.2.3 on 2021-05-29 08:19

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='created_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='user',
            name='external_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name='user',
            name='last_modified_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 29, 8, 19, 54, 904232)),
        ),
    ]