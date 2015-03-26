#-*-coding:utf8;-*-
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from member.forms import RegisterForm, LoginForm, ProfileForm
from member.func import login as login_user, logout as logout_user, profile as profile_user

def index(request, template_name="passport/index.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def register(request, form_class=RegisterForm, template_name="passport/register.html"):
    if request.method == "POST":
        goto = request.POST.get("goto")
        if goto is None:
            goto = settings.DEFAULT_GOTO
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login_user(request, user)
            return HttpResponseRedirect(goto)
    else:
        goto = request.GET.get("goto")
        form = form_class(initial={"goto": goto})
    return render_to_response(template_name, {
        'form':form,
    }, context_instance=RequestContext(request))
    
def login(request, form_class=LoginForm, template_name="passport/login.html"):
    if request.method == "POST":
        goto = request.POST.get("goto")
        if goto is None:
            goto = settings.DEFAULT_GOTO
        form = form_class(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login_user(request, user)
            return HttpResponseRedirect(goto)
    else:
        goto = request.GET.get("goto")
        form = form_class(request, initial={"goto": goto})
    return render_to_response(template_name, {
        'form':form,
    }, context_instance=RequestContext(request))
    
def logout(request, template_name="passport/logout.html"):
    goto = request.GET.get("goto")
    if goto is None:
        goto = settings.DEFAULT_GOTO
    logout_user(request)
    return HttpResponseRedirect(goto)
    
def forget(request, template_name="passport/forget.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
    
def profile(request, form_class=ProfileForm, template_name="passport/profile.html"):
    if request.method == "POST":
        goto = request.POST.get("goto")
        if goto is None:
            goto = settings.DEFAULT_GOTO
        form = form_class(request.POST)
        if form.is_valid():
            user = profile_user(request, form)
            return HttpResponseRedirect(goto)
    else:
        goto = request.GET.get("goto")
        form = form_class(initial={"goto": goto, "name":request.myuser.name, "password":request.myuser.password})    
    return render_to_response(template_name, {
        'form':form,
    }, context_instance=RequestContext(request))

def active(request, template_name="passport/active.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
    