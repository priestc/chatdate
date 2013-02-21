import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Relationship

@login_required
def relationships(request):
    r = Relationship.objects.my_relationships(request.user)
    r_json = [x.to_json(perspective=request.user) for x in r]
    return HttpResponse(json.dumps(r_json), mimetype="application/json")

def block_user(request, user_hash):
    r = Relationship.objects.get_or_make_relationship(request.user.hash, user_hash)
    r.blocked = True
    r.save()
    return HttpResponse("OK", mimetype="application/json")
