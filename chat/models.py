from django.db import models
from accounts.models import Account

import shortuuid


class Chat(models.Model):
    CHAT_TYPE_CHOICES = [
        ('PR', 'Private'),
        ('PB', 'Public'),
        ('OO', 'OneToOne'),
    ]
    
    owner = models.ForeignKey(Account, related_name='chat', null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=150)
    username = models.CharField(max_length=25, unique=True, default=shortuuid.uuid)
    avatar = models.ImageField(upload_to='images/chat/avatar/', null=True, blank=True)
    members = models.ManyToManyField(Account, blank=True, related_name='chat_members')
    online_members = models.ManyToManyField(Account, blank=True, related_name='chat_online_members')
    type = models.CharField(choices=CHAT_TYPE_CHOICES, max_length=2, default='PR')
    
    created = models.DateTimeField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{ self.name } : { self.username }'
    
    def get_last_message(self):
        return self.message.last()
    

class SingleChatMessage(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='message')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='message')
    message = models.TextField()
    files = models.FileField(upload_to='files/chat/', blank=True, null=True)
    
    created = models.DateTimeField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    
