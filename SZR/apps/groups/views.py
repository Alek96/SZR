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
from . import forms

#
# @login_required
# def init_sidebar(request):
#     return render(request, 'groups/sidebar.html', {'text': "Hello!"})


@login_required
def groups_index(request):
    context = {
        'group_list': GitLabApi(request.user.id).groups.get_roots(),
    }
    return render(request, 'groups/groups_index.html', context)


@login_required
def group_detail_index(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group': group,
    }
    return render(request, 'groups/group_detail_index.html', context)


@login_required
def group_members(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group': group,
    }
    return render(request, 'groups/group_detail_members.html', context)


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
    return new_subgroup(request, None)


@login_required
def new_subgroup(request, group_id):
    form = forms.GroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Group',
        "fields_title": 'New Group',
    }
    if form.is_valid():
        form.save_in_gitlab(request.user.id, group_id)
        return HttpResponseRedirect(reverse('groups:index'))

    return render(request, 'groups/new_group.html', context)
