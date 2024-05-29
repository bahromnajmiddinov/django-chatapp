# Generated by Django 5.0.6 on 2024-05-24 08:57

import django.db.models.deletion
import shortuuid.main
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('username', models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=25, unique=True)),
                ('chat_type', models.CharField(choices=[('PR', 'Private'), ('PB', 'Public'), ('OO', 'OneToOne')], default='PR', max_length=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('time', models.TimeField(auto_now_add=True)),
                ('members', models.ManyToManyField(blank=True, related_name='chat_members', to=settings.AUTH_USER_MODEL)),
                ('online_members', models.ManyToManyField(blank=True, related_name='chat_online_members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SingleChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('time', models.TimeField(auto_now_add=True)),
                ('seen', models.BooleanField(default=False)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message', to='chat.chat')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
