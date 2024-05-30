from django.urls import path

from . import views


urlpatterns = [
    path('', views.chatapp_home, name='chatapp-home'),
    path('search/chats/', views.search_chats, name='search-chats'),
    path('private/single-chat/<user_id>', views.single_chat, name='single-chat'),
    path('public/group-chat/<group_username>', views.public_group_chat, name='public-chat'),
    path('private/group-chat/<group_username>', views.private_group_chat, name='private-chat'),
    path('group-chat/edit/<group_username>', views.edit_group, name='edit-group'),
    path('group-chat/create/', views.create_group, name='create-group'),
    path('group-chat/create/public/', views.create_public_group, name='create-public-group'),
    path('group-chat/create/private/', views.create_private_group, name='create-private-group'),
]

