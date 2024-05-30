from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

import json
from .models import Chat, SingleChatMessage
from accounts.models import Account


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.other_user = get_object_or_404(Account, pk=self.other_user_id)
        self.user = self.scope['user']
        self.chat_name = None
        
        self.accept()

        
    def receive(self, text_data):
        text_data = json.loads(text_data)['message']
        
        chat = Chat.objects.filter(Q(members__in=[self.user, self.other_user]) & Q(type='OO')).first()
        self.chat_name = chat.username
        if chat is None:
            chat = Chat.objects.create(type='OO', owner=self.user, name='single-chat')
            chat.members.add(*[self.user, self.other_user])
        
        SingleChatMessage.objects.create(chat=chat, sender=self.user, message=text_data)
        
        data = {
            'type': 'receiver',
            'data_type': 'text',
            'message': text_data,
            'sender_id': self.user.id,
        }
        async_to_sync(self.channel_layer.group_add)(chat.username, self.channel_name)
        async_to_sync(self.channel_layer.group_send)(chat.username, data)
    
    def disconnect(self, code):
        if self.chat_name:
            async_to_sync(self.channel_layer.group_discard)(self.chat_name, self.channel_name)
    
    def receiver(self, data):
        chat_user = get_object_or_404(Account, pk=data.get('sender_id'))
        
        message = render_to_string('chat/snippets/single-message.html', context={ 'message_owner': chat_user, 'message': data['message'], 'maybe_owner': self.user })
        
        data['message'] = message
        
        data = json.dumps(data)
        self.send(data)
    

class PublicGroupChatConsumer(WebsocketConsumer):
    def connect(self):
        self.group_username = self.scope['url_route']['kwargs']['group_username']
        self.user = self.scope['user']
        self.public_group = get_object_or_404(Chat, username=self.group_username, type='PB')
        
        self.accept()
        
        async_to_sync(self.channel_layer.group_add)(self.group_username, self.channel_name)
        self.public_group.online_members.add(self.user)
        self.online_status(self.public_group.online_members.count())
            
    def receive(self, text_data):
        text_data = json.loads(text_data)['message']
        
        message = SingleChatMessage.objects.create(chat=self.public_group, message=text_data, sender=self.user)
        
        data = {
            'type': 'receiver',
            'data_type': 'text',
            'message': text_data,
            'sender_id': self.user.id,
        }
    
        async_to_sync(self.channel_layer.group_send)(self.group_username, data)
        
    
    def disconnect(self, code):
        self.public_group.online_members.remove(self.user)
        self.online_status(self.public_group.online_members.count())
        async_to_sync(self.channel_layer.group_discard)(self.group_username, self.channel_name)
    
    def receiver(self, data):
        chat_user = get_object_or_404(Account, pk=data.get('sender_id'))
        message = render_to_string('chat/snippets/single-message.html', context={ 'message_owner': chat_user, 'message': data['message'], 'maybe_owner': self.user })
        
        data['message'] = message
        
        data = json.dumps(data)
        self.send(data)
    
    def online_status(self, online_members):
        data = {
            'type': 'online_status_handler',
            'online_members': online_members,
        }
        
        async_to_sync(self.channel_layer.group_send)(self.group_username, data)
        
    def online_status_handler(self, data):
        data = json.dumps(data)
        
        self.send(data)


class PrivateGroupChatConsumer(WebsocketConsumer):
    def connect(self):
        self.group_username = self.scope['url_route']['kwargs']['group_username']
        self.user = self.scope['user']
        self.public_group = get_object_or_404(Chat, username=self.group_username, type='PR')
        
        self.accept()
        
        async_to_sync(self.channel_layer.group_add)(self.group_username, self.channel_name)
        self.public_group.online_members.add(self.user)
        self.online_status(self.public_group.online_members.count())
            
    def receive(self, text_data):
        text_data = json.loads(text_data)['message']
        
        message = SingleChatMessage.objects.create(chat=self.public_group, message=text_data, sender=self.user)
        
        data = {
            'type': 'receiver',
            'data_type': 'text',
            'message': text_data,
            'sender_id': self.user.id,
        }
    
        async_to_sync(self.channel_layer.group_send)(self.group_username, data)
        
    
    def disconnect(self, code):
        self.public_group.online_members.remove(self.user)
        self.online_status(self.public_group.online_members.count())
        async_to_sync(self.channel_layer.group_discard)(self.group_username, self.channel_name)
    
    def receiver(self, data):
        chat_user = get_object_or_404(Account, pk=data.get('sender_id'))
        message = render_to_string('chat/snippets/single-message.html', context={ 'message_owner': chat_user, 'message': data['message'], 'maybe_owner': self.user })
        
        data['message'] = message
        
        data = json.dumps(data)
        self.send(data)
    
    def online_status(self, online_members):
        data = {
            'type': 'online_status_handler',
            'online_members': online_members,
        }
        
        async_to_sync(self.channel_layer.group_send)(self.group_username, data)
        
    def online_status_handler(self, data):
        data = json.dumps(data)
        
        self.send(data)
