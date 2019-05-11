from GitLabApi import GitLabApi
from GitLabApi import mock_all_gitlab_url
from core.exceptions import FormNotValidError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from groups import forms
from groups import models
from groups.sidebar import GroupSidebar, FutureGroupSidebar


@login_required
@mock_all_gitlab_url
def init_sidebar(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    context = {
        'group': group,
        'sidebar': GroupSidebar(group)
    }
    return render(request, 'sidebar.html', context)


@login_required
def roots(request):
    context = {
        'group_list': GitLabApi(request.user.id).groups.get_roots(),
    }
    return render(request, 'groups/index.html', context)


@login_required
def detail(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)
    context = {
        'group': group,
        'sidebar': GroupSidebar(group),
        'unfinished_add_subgroup_list': gitlab_group.get_unfinished_add_subgroup_list(),
        'unfinished_add_project_list': gitlab_group.get_unfinished_add_project_list(),
    }
    return render(request, 'groups/detail.html', context)


@login_required
def members(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)
    context = {
        'group': group,
        'sidebar': GroupSidebar(group),
        'unfinished_task_list': gitlab_group.get_unfinished_add_member_list(),
    }
    return render(request, 'groups/members.html', context)


@login_required
def tasks(request, group_id):
    group = GitLabApi(request.user.id).groups.get(group_id)
    gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)
    new_group_links = [
        ('New Task Group', reverse('groups:new_task_group', kwargs={'group_id': group_id})),
        ('New Subgroup', reverse('groups:new_subgroup_task', kwargs={'group_id': group_id})),
        ('New Project', reverse('groups:new_project_task', kwargs={'group_id': group_id})),
        ('New Member', reverse('groups:new_member_task', kwargs={'group_id': group_id}))
    ]
    context = {
        'group': group,
        'sidebar': GroupSidebar(group),
        'unfinished_task_list': gitlab_group.get_unfinished_task_list(include_groups=True),
        'finished_task_list': gitlab_group.get_finished_task_list(include_groups=True),
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
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:index'))


@login_required
def new_subgroup(request, group_id):
    form = forms.AddSubgroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Subgroup',
        "fields_title": 'New Subgroup',
    }
    try:
        form.save_in_gitlab(user_id=request.user.id, group_id=group_id)
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:detail', args=(group_id,)))


@login_required
def new_task_group(request, group_id=None, task_id=None):
    parent_task = get_object_or_404(models.AddSubgroup, id=task_id) if task_id else None
    form = forms.TaskGroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Task Group',
        "fields_title": 'Add Task Group',
    }
    try:
        model = form.save(group_id=group_id, parent_task=parent_task)
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def edit_task_group(request, task_group_id):
    task_group = get_object_or_404(models.TaskGroup, id=task_group_id)
    form = forms.TaskGroupForm(request.POST or None, instance=task_group)
    context = {
        "form": form,
        "page_title": 'Edit Task Group',
        "fields_title": 'Edit Task Group',
    }
    try:
        model = form.update()
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def new_subgroup_task(request, group_id=None, task_group_id=None, task_id=None):
    task_group = get_object_or_404(models.TaskGroup, id=task_group_id) if task_group_id else None
    parent_task = get_object_or_404(models.AddSubgroup, id=task_id) if task_id else None
    form = forms.AddSubgroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Subgroup Task',
        "fields_title": 'Add Subgroup Task',
    }
    try:
        model = form.save(user_id=request.user.id, group_id=group_id, task_group=task_group, parent_task=parent_task)
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def edit_subgroup_task(request, task_id):
    task = get_object_or_404(models.AddSubgroup, id=task_id)
    form = forms.AddSubgroupForm(request.POST or None, instance=task)
    context = {
        "form": form,
        "page_title": 'Edit Subgroup Task',
        "fields_title": 'Edit Subgroup Task',
    }
    try:
        model = form.update()
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def new_project(request, group_id):
    form = forms.AddProjectForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Project',
        "fields_title": 'New Project',
    }
    try:
        form.save_in_gitlab(user_id=request.user.id, group_id=group_id)
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:detail', args=(group_id,)))


@login_required
def new_project_task(request, group_id=None, task_group_id=None, task_id=None):
    task_group = get_object_or_404(models.TaskGroup, id=task_group_id) if task_group_id else None
    parent_task = get_object_or_404(models.AddSubgroup, id=task_id) if task_id else None
    form = forms.AddProjectForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Project Task',
        "fields_title": 'Add Project Task',
    }
    try:
        model = form.save(user_id=request.user.id, group_id=group_id, task_group=task_group, parent_task=parent_task)
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def edit_project_task(request, task_id):
    task = get_object_or_404(models.AddProject, id=task_id)
    form = forms.AddProjectForm(request.POST or None, instance=task)
    context = {
        "form": form,
        "page_title": 'Edit Project Task',
        "fields_title": 'Edit Project Task',
    }
    try:
        model = form.update()
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


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
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('groups:members', args=(group_id,)))


@login_required
def new_member_task(request, group_id=None, task_group_id=None, task_id=None):
    task_group = get_object_or_404(models.TaskGroup, id=task_group_id) if task_group_id else None
    parent_task = get_object_or_404(models.AddSubgroup, id=task_id) if task_id else None
    form = forms.AddMemberForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Member Task',
        "fields_title": 'Add Member Task',
    }
    try:
        model = form.save(user_id=request.user.id, group_id=group_id, task_group=task_group, parent_task=parent_task)
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def edit_member_task(request, task_id):
    task = get_object_or_404(models.AddMember, id=task_id)
    form = forms.AddMemberForm(request.POST or None, instance=task)
    context = {
        "form": form,
        "page_title": 'Edit Member Task',
        "fields_title": 'Edit Member Task',
    }
    try:
        model = form.update()
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def new_members_from_file(request, group_id=None, task_id=None):
    parent_task = get_object_or_404(models.AddSubgroup, id=task_id) if task_id else None
    form = forms.MembersFromFileForm(request.POST or None, request.FILES or None)
    context = {
        "form": form,
        "page_title": 'Add members from file',
        "fields_title": 'Add members from file',
    }
    try:
        model = form.save(group_id=group_id, parent_task=parent_task, user_id=request.user.id)
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def new_subgroup_and_members_from_file(request, group_id=None, task_id=None):
    parent_task = get_object_or_404(models.AddSubgroup, id=task_id) if task_id else None
    form = forms.SubgroupAndMembersFromFileForm(request.POST or None, request.FILES or None)
    context = {
        "form": form,
        "page_title": 'Add members from file',
        "fields_title": 'Add members from file',
    }
    try:
        model = form.save(group_id=group_id, parent_task=parent_task, user_id=request.user.id)
    except FormNotValidError:
        return render(request, 'groups/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def future_group_detail(request, task_id):
    task = get_object_or_404(models.AddSubgroup, id=task_id)
    gitlab_group = task.new_gitlab_group
    context = {
        'task': task,
        'sidebar': FutureGroupSidebar(task),
        'unfinished_add_subgroup_list': gitlab_group.get_unfinished_add_subgroup_list(),
        'unfinished_add_project_list': gitlab_group.get_unfinished_add_project_list(),
    }
    return render(request, 'groups/tasks/detail.html', context)


@login_required
def future_group_members(request, task_id):
    task = get_object_or_404(models.AddSubgroup, id=task_id)
    gitlab_group = task.new_gitlab_group
    context = {
        'task': task,
        'sidebar': FutureGroupSidebar(task),
        'unfinished_task_list': gitlab_group.get_unfinished_add_member_list(),
    }
    return render(request, 'groups/tasks/members.html', context)


@login_required
def future_group_tasks(request, task_id):
    task = get_object_or_404(models.AddSubgroup, id=task_id)
    gitlab_group = task.new_gitlab_group
    new_group_links = [
        ('New Task Group', reverse('groups:new_task_group', kwargs={'task_id': task_id})),
        ('New Subgroup', reverse('groups:new_subgroup_task', kwargs={'task_id': task_id})),
        ('New Project', reverse('groups:new_project_task', kwargs={'task_id': task_id})),
        ('New Member', reverse('groups:new_member_task', kwargs={'task_id': task_id}))
    ]
    context = {
        'task': task,
        'sidebar': FutureGroupSidebar(task),
        'unfinished_task_list': gitlab_group.get_unfinished_task_list(include_groups=True),
        'finished_task_list': gitlab_group.get_finished_task_list(include_groups=True),
        'new_group_links': new_group_links,
    }
    return render(request, 'groups/tasks/tasks.html', context)


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
