# Generated by Django 4.0.4 on 2022-05-23 14:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('iris_messages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iris_messages.channel'),
        ),
        migrations.AddField(
            model_name='channel',
            name='users',
            field=models.ManyToManyField(related_name='channel_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='groupchannel',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='admins', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='groupchannel',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL),
        ),
    ]