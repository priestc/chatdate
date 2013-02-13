from django.template.response import TemplateResponse
from .models import Relationship

def relationships(request):
    relationships = Relationship.objects.my_relationships(request.user)
    return TemplateResponse(request, "relationships.html", {
        'relationships': relationships
    })