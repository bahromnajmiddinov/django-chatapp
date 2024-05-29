from django import template


register = template.Library()


@register.filter
def get_users_chats(user):
    chats = user.chat_members.all()
    
    return chats
