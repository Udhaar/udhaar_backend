# Generated by Django 3.2.3 on 2021-06-03 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='declined_comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]