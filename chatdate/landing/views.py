from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from .forms import RegisterForm

def landingpage(request):
    return TemplateResponse(request, 'landingpage.html', {})

def register_start(request):
    form = RegisterForm()
    status = 200
    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.set_password(new_user.password)
            new_user.save()
            user = authenticate(username=request.POST['email'], password=request.POST['password'])
            login(request, user)
            url = reverse('dashboard')
            return HttpResponseRedirect(url)
        else:
            status = 400

    return TemplateResponse(request, 'register.html', {'form': form}, status=status)