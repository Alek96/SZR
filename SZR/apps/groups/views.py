from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.conf import settings

from GitLabApi import *
from GitLabApi.exceptions import *
from . import forms

from GitLabApi import mock_all_gitlab_url


@login_required
@mock_all_gitlab_url
def init_sidebar(request, group_id):
    context = {
        'group': GitLabApi(request.user.id).groups.get(group_id),
    }
    return render(request, 'groups/sidebar.html', context)


@login_required
def groups_roots(request):
    context = {
        'group_list': GitLabApi(request.user.id).groups.get_roots(),
    }
    return render(request, 'groups/index.html', context)


@login_required
def group_detail(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group': group,
    }
    return render(request, 'groups/group_detail.html', context)


@login_required
def group_members(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group': group,
    }
    return render(request, 'groups/group_members.html', context)


@login_required
def ajax_load_subgroups(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group_list': group.subgroups.list(),
        'project_list': [],
    }
    return render(request, 'groups/ajax_load_subgroups_and_projects.html', context)


@login_required
def ajax_load_subgroups_and_projects(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group_list': group.subgroups.list(),
        'project_list': group.projects.list(),
    }
    return render(request, 'groups/ajax_load_subgroups_and_projects.html', context)


@login_required
def new_group(request):
    form = forms.GroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Group',
        "fields_title": 'New Group',
    }
    try:
        form.save_in_gitlab(request.user.id)
    except forms.WrongFormError:
        return render(request, 'groups/new_group.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:index'))


@login_required
def new_subgroup(request, group_id):
    form = forms.GroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Group',
        "fields_title": 'New Group',
    }
    try:
        form.save_in_gitlab(request.user.id, group_id)
    except forms.WrongFormError:
        return render(request, 'groups/new_group.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:group_detail', args=(group_id,)))
