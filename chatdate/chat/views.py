import json

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import ReadyToChat

@login_required
def start_chat(request):
    ReadyToChat.objects.set_ready(request.user)
    locals = ReadyToChat.objects.online_users(request.user)
    return TemplateResponse(request, 'chat.html', {
        'locals': locals
    })

@login_required
def still_here_short_poll(request):
    ReadyToChat.objects.set_ready(request.user)
    all = ReadyToChat.objects.all().exclude(user=request.user)
    users = [{'nickname': x.user.nickname, 'hash': x.user.hash} for x in all]
    return HttpResponse(json.dumps(users), mimetype="application/json")