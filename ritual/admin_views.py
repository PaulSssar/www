from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdminChatMessageForm
from .models import UserAccounts, ChatMessage

from django.shortcuts import render, get_object_or_404
from .forms import AdminChatMessageForm
from .models import UserAccounts


def send_admin_message(request, user_id):
    recipient = get_object_or_404(UserAccounts, pk=user_id)
    if request.method == 'POST':
        form = AdminChatMessageForm(request.POST, author=request.user, recipient=recipient)
        if form.is_valid():
            form.save()
            return redirect('admin:ritual_useraccounts_change', user_id)

    else:
        form = AdminChatMessageForm(author=request.user, recipient=recipient)

    return render(request, 'admin/send_admin_message.html', {'form': form, 'recipient': recipient})




