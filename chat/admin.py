from django.contrib import admin

from .models import Chat, SingleChatMessage


class SingleChatMessageInline(admin.TabularInline):
    model = SingleChatMessage
    

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    inlines = [SingleChatMessageInline]
    list_display = ['name', 'owner', 'created', 'time', 'type']
        