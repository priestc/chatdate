import json

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import ReadyToChat

@login_required
def karma(request):
    return HttpResponse(json.dumps(request.user.reputation), mimetype="application/json")