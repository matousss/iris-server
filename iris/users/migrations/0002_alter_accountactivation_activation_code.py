# Generated by Django 4.0.3 on 2022-04-09 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iris_users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountactivation',
            name='activation_code',
            field=models.CharField(max_length=256),
        ),
    ]