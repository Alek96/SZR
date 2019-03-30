from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.conf import settings

from GitLabApi import *
from GitLabApi.exceptions import *
from core.exceptions import WrongFormError
from groups import forms
from groups import models

from GitLabApi import mock_all_gitlab_url


@login_required
@mock_all_gitlab_url
def init_sidebar(request, group_id):
    context = {
        'group': GitLabApi(request.user.id).groups.get(group_id),
    }
    return render(request, 'groups/sidebar.html', context)


@login_required
def roots(request):
    context = {
        'group_list': GitLabApi(request.user.id).groups.get_roots(),
    }
    return render(request, 'groups/index.html', context)


@login_required
def detail(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group': group,
    }
    return render(request, 'groups/detail.html', context)


@login_required
def members(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group': group,
    }
    return render(request, 'groups/members.html', context)


@login_required
def tasks(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)
    new_group_links = [
        ('New Subgroup Group', reverse('groups:new_subgroup_group', kwargs={'group_id': group_id})),
        ('New Member Group', reverse('groups:new_member_group', kwargs={'group_id': group_id}))
    ]
    context = {
        'group': group,
        'unfinished_task_list': gitlab_group.get_unfinished_task_list(),
        'finished_task_list': gitlab_group.get_finished_task_list(),
        'new_group_links': new_group_links,
    }
    return render(request, 'groups/tasks.html', context)


@login_required
def new_group(request):
    form = forms.AddSubgroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Group',
        "fields_title": 'New Group',
    }
    try:
        form.save_in_gitlab(user_id=request.user.id)
    except WrongFormError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:index'))


@login_required
def new_subgroup(request, group_id):
    form = forms.AddSubgroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Group',
        "fields_title": 'New Group',
    }
    try:
        form.save_in_gitlab(user_id=request.user.id, group_id=group_id)
    except WrongFormError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:detail', args=(group_id,)))


@login_required
def new_subgroup_group(request, group_id):
    form = forms.AddSubgroupGroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Subgroup Group',
        "fields_title": 'Add Subgroup Group',
    }
    try:
        form.save_in_db(group_id=group_id)
    except WrongFormError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:tasks', args=(group_id,)))


@login_required
def new_subgroup_task(request, group_id, task_group_id):
    get_object_or_404(models.AddSubgroupGroup, id=task_group_id)
    form = forms.AddSubgroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Subgroup Task',
        "fields_title": 'Add Subgroup Task',
    }
    try:
        form.save_in_db(user_id=request.user.id, task_group_id=task_group_id)
    except WrongFormError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:tasks', args=(group_id,)))


@login_required
def new_member(request, group_id):
    form = forms.AddMemberForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Group Member',
        "fields_title": 'New Group Member',
    }
    try:
        form.save_in_gitlab(user_id=request.user.id, group_id=group_id)
    except WrongFormError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:members', args=(group_id,)))


@login_required
def new_member_group(request, group_id):
    form = forms.AddMemberGroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Member Group',
        "fields_title": 'Add Member Group',
    }
    try:
        form.save_in_db(group_id=group_id)
    except WrongFormError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:tasks', args=(group_id,)))


@login_required
def new_member_task(request, group_id, task_group_id):
    get_object_or_404(models.AddMemberGroup, id=task_group_id)
    form = forms.AddMemberForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Member Task',
        "fields_title": 'Add Member Task',
    }
    try:
        form.save_in_db(user_id=request.user.id, task_group_id=task_group_id)
    except WrongFormError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:tasks', args=(group_id,)))


@login_required
def ajax_load_subgroups(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group_list': group.subgroups.list(),
        'project_list': [],
    }
    return render(request, 'groups/ajax/load_subgroups_and_projects.html', context)


@login_required
def ajax_load_subgroups_and_projects(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group_list': group.subgroups.list(),
        'project_list': group.projects.list(),
    }
    return render(request, 'groups/ajax/load_subgroups_and_projects.html', context)
