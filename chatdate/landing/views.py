from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as dj_logout

from .forms import RegisterForm

def landingpage(request):
    if request.user.is_authenticated():
        return TemplateResponse(request, 'app.html', {})

    if request.POST:
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'Invalid Login')
    
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
            return HttpResponseRedirect('/')
        else:
            status = 400

    return TemplateResponse(request, 'register.html', {'form': form}, status=status)

def logout(request):
    dj_logout(request)
    return HttpResponseRedirect('/')