from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Account
from .forms import AccountEditForm


@login_required(login_url='account_login')
def profile_redirect(request):
    return redirect('profile', request.user.username)


@login_required(login_url='account_login')
def profile(request, username):
    user = get_object_or_404(Account, username=username)
    
    context = {
        'user': user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='account_login')
def profile_edit(request):
    form = AccountEditForm(instance=request.user)
    
    if request.method == 'POST':
        form = AccountEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/profile-edit.html', context)
