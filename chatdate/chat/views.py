import json

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import ReadyToChat

@login_required
def still_here_short_poll(request):
    ReadyToChat.objects.set_ready(request.user)
    users = ReadyToChat.objects.values('user__nickname', 'user__hash', 'user__reputation').exclude(user=request.user)
    return HttpResponse(json.dumps(list(users)), mimetype="application/json")