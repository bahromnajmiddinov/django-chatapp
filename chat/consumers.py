from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.files.base import ContentFile

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

import time
import json
import base64

from .models import Chat, SingleChatMessage
from accounts.models import Account


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.other_user = get_object_or_404(Account, pk=self.other_user_id)
        self.user = self.scope['user']
        self.chat_username = None
        
        self.accept()

        
    def receive(self, text_data):
        data = json.loads(text_data)
        
        text_data = data.get('message')
        file_data = data.get('file')
        
        if text_data or file_data:
            file_instance = None
            if file_data:
                file_format, file_object = file_data.split(';base64,')
                decoded_data = base64.b64decode(file_object)
                file_instance = ContentFile(decoded_data, name=f'message_file.{ file_format.split('/')[1] }')
            
            chat = Chat.objects.filter(Q(members__in=[self.user, self.other_user]) & Q(type='OO')).first()
            if chat is None:
                chat = Chat.objects.create(type='OO', owner=self.user, name='single-chat')
                chat.members.add(*[self.user, self.other_user])
            self.chat_username = chat.username
            message = SingleChatMessage.objects.create(chat=chat, sender=self.user, message=text_data, files=file_instance)
            
            data = {
                'type': 'receiver',
                'data_type': 'text',
                'message_id': message.id,
            }
            
            async_to_sync(self.channel_layer.group_add)(chat.username, self.channel_name)
            async_to_sync(self.channel_layer.group_send)(chat.username, data)
    
    def disconnect(self, code):
        if self.chat_username:
            async_to_sync(self.channel_layer.group_discard)(self.chat_username, self.channel_name)
    
    def receiver(self, data):
        message_object = SingleChatMessage.objects.get(data['message_id'])
        message = render_to_string('chat/snippets/single-message.html', context={ 'message': message_object, 'maybe_owner': self.user })
        
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
        if not self.user in self.public_group.online_members.all():
            self.public_group.online_members.add(self.user)
        self.online_status()
            
    def receive(self, text_data):
        data = json.loads(text_data)
        
        text_data = data.get('message')
        file_data = data.get('file')
        
        if text_data or file_data:
            file_instance = None
            if file_data:
                file_format, file_object = file_data.split(';base64,')
                decoded_data = base64.b64decode(file_object)
                file_instance = ContentFile(decoded_data, name=f'message_file.{ file_format.split('/')[1] }')
                
            message = SingleChatMessage.objects.create(chat=self.public_group, message=text_data, sender=self.user, files=file_instance)
            
            data = {
                'type': 'receiver',
                'data_type': 'text',
                'message': message,
            }
        
            async_to_sync(self.channel_layer.group_send)(self.group_username, data)
        
    
    def disconnect(self, code):
        if self.user in self.public_group.online_members.all():
            self.public_group.online_members.remove(self.user)
        self.online_status()
        async_to_sync(self.channel_layer.group_discard)(self.group_username, self.channel_name)
    
    def receiver(self, data):
        message = render_to_string('chat/snippets/single-message.html', context={ 'message': data['message'], 'maybe_owner': self.user })
        
        data['message'] = message
        
        data = json.dumps(data)
        self.send(data)
    
    def online_status(self):
        data = {
            'type': 'online_status_handler',
        }
        
        async_to_sync(self.channel_layer.group_send)(self.group_username, data)
        
    def online_status_handler(self, data):
        data['online_members'] = self.public_group.online_members.count()
        data = json.dumps(data)
        
        self.send(data)


class PrivateGroupChatConsumer(WebsocketConsumer):
    def connect(self):
        self.group_username = self.scope['url_route']['kwargs']['group_username']
        self.user = self.scope['user']
        self.private_group = get_object_or_404(Chat, username=self.group_username, type='PR')
        
        self.accept()
        
        async_to_sync(self.channel_layer.group_add)(self.group_username, self.channel_name)
        self.private_group.online_members.add(self.user)
        self.online_status()
            
    def receive(self, text_data):
        data = json.loads(text_data)
        
        text_data = data.get('message')
        file_data = data.get('file')
        
        if text_data or file_data:
            file_instance = None
            if file_data:
                file_format, file_object = file_data.split(';base64,')
                decoded_data = base64.b64decode(file_object)
                file_instance = ContentFile(decoded_data, name=f'message_file.{ file_format.split('/')[1] }')
                
            message = SingleChatMessage.objects.create(chat=self.private_group, message=text_data, sender=self.user, files=file_instance)
            
            data = {
                'type': 'receiver',
                'data_type': 'text',
                'message': message,
            }
        
            async_to_sync(self.channel_layer.group_send)(self.group_username, data)
        
    
    def disconnect(self, code):
        self.private_group.online_members.remove(self.user)
        self.online_status()
        async_to_sync(self.channel_layer.group_discard)(self.group_username, self.channel_name)
    
    def receiver(self, data):
        message = render_to_string('chat/snippets/single-message.html', context={ 'message': data['message'], 'maybe_owner': self.user })
        
        data['message'] = message
        
        data = json.dumps(data)
        self.send(data)
    
    def online_status(self):
        data = {
            'type': 'online_status_handler',
        }
        
        async_to_sync(self.channel_layer.group_send)(self.group_username, data)
        
    def online_status_handler(self, data):
        data['online_members'] = self.private_group.online_members.count()
        data = json.dumps(data)
        
        self.send(data)
        

class UserStatusConsumer(WebsocketConsumer):
    def connect(self):
        self.abs_user_id = self.scope['url_route']['kwargs']['user_id']
        self.abs_user = get_object_or_404(Account, pk=self.abs_user_id)
        self.user = self.scope['user']
        
        self.accept()
        
        if self.abs_user == self.user:
            self.change_status(online=True)
        async_to_sync(self.channel_layer.group_add)(self.abs_user.username, self.channel_name)
    
    def disconnect(self, code):
        time.sleep(3)
        if self.abs_user == self.user:
            self.change_status(online=False)
        async_to_sync(self.channel_layer.group_discard)(self.abs_user.username, self.channel_name)
    
    def change_status(self, online=False):
        self.user.status = online
        self.user.save()
        
        data = {
            'type': 'user_status_handler',
            'status': online, 
            'userId': self.user.id,
        }
        
        async_to_sync(self.channel_layer.group_send)(self.user.username, data)
        
    def user_status_handler(self, data):
        data = json.dumps(data)
        
        self.send(data)
        