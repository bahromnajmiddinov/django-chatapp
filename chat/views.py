from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from accounts.models import Account
from .models import Chat
from .forms import PublicGroupForm, PrivateGroupForm


def _image_filter(obj, counts=12):
    return obj.message.filter(Q(files__endswith='.jpg') | Q(files__endswith='.png') | Q(files__endswith='.gif')| Q(files__endswith='.jpeg'))[:counts]


@login_required(login_url='account_login')
def chatapp_home(request):
    return render(request, 'chat/chatapphome.html')


@login_required(login_url='account_login')
def search_chats(request):
    query = request.GET.get('q')
    chats, other_user_chats = [], []
    name = 'search'
    if query:
        chats = Chat.objects.filter(Q(username__icontains=query) | Q(name__icontains=query)).filter(Q(type='PB') | Q(type='OO'))
        other_user_chats = Account.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(username__icontains=query))
    
    context = {
        'chats': chats,
        'other_user_chats': other_user_chats,
        'name': name,
    }
    
    return render(request, 'chat/search.html', context)


@login_required(login_url='account_login')
def single_chat(request, user_id):
    search_query = request.GET.get('q')
    
    if request.user.id == int(user_id):
        return redirect('my_profile')
    
    user = Account.objects.get(pk=user_id)
    single_chat = Chat.objects.filter(Q(members__in=[request.user, user]) & Q(type='OO')).first()
    single_chat_messages = []
    shared_photos = []
    if single_chat:
        if not search_query:
            single_chat_messages = single_chat.message.all()
        else:
            single_chat_messages = single_chat.message.filter(Q(message__icontains=search_query) | Q(files__icontains=search_query))
        shared_photos = _image_filter(single_chat)

    context = {
        'single_chat_user': user,
        'single_chat_messages': single_chat_messages,
        'shared_photos': shared_photos,
    }
    return render(request, 'chat/single_chat.html', context)


@login_required(login_url='account_login')
def delete_single_chat(request, user_id):
    user = Account.objects.get(pk=user_id)
    single_chat = Chat.objects.filter(Q(members__in=[request.user, user]) & Q(type='OO')).first()
    if single_chat:
        single_chat.delete()
    
    return redirect('chatapp-home')


@login_required(login_url='account_login')
def create_group(request):
    pass


@login_required(login_url='account_login')
def create_public_group(request):
    initial_data = {'username': ''}
    form = PublicGroupForm(initial=initial_data)
    
    if request.method == 'POST':
        form = PublicGroupForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.type = 'PB'
            form.owner = request.user
            form.save()
            form.members.add(request.user)
            return redirect('public-chat', form.username)
        
    context = {
        'form': form,
    }
    
    return render(request, 'chat/create_group.html', context)


@login_required(login_url='account_login')
def create_private_group(request):
    form = PrivateGroupForm()
    
    if request.method == 'POST':
        form = PrivateGroupForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.type = 'PR'
            form.owner = request.user
            form.save()
            form.members.add(request.user)
            return redirect('private-chat', form.username)
        
    context = {
        'form': form,
    }
    
    return render(request, 'chat/create_group.html', context)


@login_required(login_url='account_login')
def delete_group(request, group_username):
    group = get_object_or_404(Chat, username=group_username)
    if group.owner == request.user:
        group.delete()
    
    return redirect('chatapp-home')


@login_required(login_url='account_login')
def edit_group(request, group_username):
    group = get_object_or_404(Chat, username=group_username)
    
    if group.owner != request.user:
        return redirect('home')
    
    if request.method == 'POST':
        if group.type == 'PB':
            form = PublicGroupForm(request.POST, request.FILES, instance=group)
            if form.is_valid():
                form.save()
                return redirect('public-chat', form.cleaned_data['username'])
        elif group.type == 'PR':
            form = PrivateGroupForm(request.POST, request.FILES, instance=group)
            if form.is_valid():
                form.save()
                return redirect('private-chat', group_username)
    
    if group.type == 'PB':
        form = PublicGroupForm(instance=group)
    elif group.type == 'PR':
        form = PrivateGroupForm(instance=group)
    
    context = {
        'form': form,
        'group': group,
    }
    
    return render(request, 'chat/edit-group.html', context)


@login_required(login_url='account_login')
def public_group_chat(request, group_username):
    search_query = request.GET.get('q')
    
    group_chat = get_object_or_404(Chat, username=group_username, type='PB')
    
    if not search_query:
        chat_messages = group_chat.message.all()
    else:
        chat_messages = group_chat.message.filter(Q(message__icontains=search_query) | Q(files__icontains=search_query))
    
    shared_photos = _image_filter(group_chat)
    is_member = group_chat.members.filter(pk=request.user.id).exists()
    
    all_members_count = group_chat.members.count()
    member3 = group_chat.members.all()[:3]
    online_members = group_chat.online_members.count()
    
    if request.method == 'POST':
        group_chat.members.add(request.user)
        is_member = True
    
    context = {
        'group_chat': group_chat,
        'chat_messages': chat_messages,
        'username': group_chat.username,
        'is_member': is_member,
        'all_members_count': all_members_count,
        'member3': member3,
        'online_members': online_members,
        'shared_photos': shared_photos,
    }
    return render(request, 'chat/publicgroupchat.html', context)


@login_required(login_url='account_login')
def private_group_chat(request, group_username):
    search_query = request.GET.get('q')
    
    group_chat = get_object_or_404(Chat, username=group_username, type='PR')
    
    if request.method == 'POST':
        group_chat.members.add(request.user)
        
    is_member = group_chat.members.filter(pk=request.user.id).exists()
    all_members_count = group_chat.members.count()
    member3 = group_chat.members.all()[:3]
    online_members = group_chat.online_members.count()
    shared_photos = _image_filter(group_chat)
    
        
    if not is_member:
        return render(request, 'chat/subscripe_to_group.html')
    
    if not search_query:
        chat_messages = group_chat.message.all()
    else:
        chat_messages = group_chat.message.filter(Q(message__icontains=search_query) | Q(files__icontains=search_query))
        
    context = {
        'group_chat': group_chat,
        'chat_messages': chat_messages,
        'username': group_chat.username,
        'is_member': is_member,
        'all_members_count': all_members_count,
        'member3': member3,
        'online_members': online_members,
        'shared_photos': shared_photos,
    }
    return render(request, 'chat/privategroupchat.html', context)


@login_required(login_url='account_login')
def group_detail_area(request, group_username):
    group_chat = get_object_or_404(Chat, username=group_username)
    
    return render(request, 'chat/chat_detail.html', {'group_chat': group_chat, 'detail_area_center': 'detail-area-center'})


@login_required(login_url='account_login')
def my_chats(request):
    any_chat = request.user.chat.exists()
    return render(request, 'chat/my_chats.html', {'any_chat': any_chat})


@login_required(login_url='account_login')
def leave_group(request, group_username):
    group_chat = get_object_or_404(Chat, username=group_username)
    group_chat.members.remove(request.user)
    group_chat.save()
    
    return redirect('chatapp-home')
    