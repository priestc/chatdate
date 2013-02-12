from django.template.response import TemplateResponse
from chatdate.models import Relationship

def dashboard(request):
    relationships = Relationship.objects.my_relationships(request.user)
    return TemplateResponse(request, "dashboard.html", {
        'relationships': relationships
    })