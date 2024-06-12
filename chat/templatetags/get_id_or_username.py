from django import template


register = template.Library()


@register.filter
def get_id_or_username(chat, user_id):
    if chat.type == 'OO':
        return chat.members.exclude(pk=user_id).first()
    return chat.name
