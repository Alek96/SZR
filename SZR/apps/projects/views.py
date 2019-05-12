from GitLabApi import GitLabApi
from GitLabApi import mock_all_gitlab_url
from core.exceptions import FormNotValidError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from . import forms
from . import models
from .sidebar import ProjectSidebar, FutureProjectSidebar


@login_required
@mock_all_gitlab_url
def init_sidebar(request, project_id):
    project = GitLabApi(request.user.id).projects.get(project_id)
    context = {
        'project': project,
        'sidebar': ProjectSidebar(project)
    }
    return render(request, 'sidebar.html', context)


@login_required
def roots(request):
    context = {
        'project_list': GitLabApi(request.user.id).projects.get_roots(),
    }
    return render(request, 'projects/index.html', context)


@login_required
def detail(request, project_id):
    project = GitLabApi(request.user.id).projects.get(project_id)
    context = {
        'project': project,
        'sidebar': ProjectSidebar(project),
    }
    return render(request, 'projects/detail.html', context)


@login_required
def members(request, project_id):
    project = GitLabApi(request.user.id).projects.get(project_id)
    gitlab_project, _ = models.GitlabProject.objects.get_or_create(gitlab_id=project_id)
    context = {
        'project': project,
        'sidebar': ProjectSidebar(project),
        'unfinished_task_list': gitlab_project.get_unfinished_task_list(model=models.AddMember),
    }
    return render(request, 'projects/members.html', context)


@login_required
def tasks(request, project_id):
    project = GitLabApi(request.user.id).projects.get(project_id)
    gitlab_project, _ = models.GitlabProject.objects.get_or_create(gitlab_id=project_id)
    new_project_links = [
        ('New Task Group', reverse('projects:new_task_group', kwargs={'project_id': project_id})),
        ('New Member', reverse('projects:new_member_task', kwargs={'project_id': project_id}))
    ]
    context = {
        'project': project,
        'sidebar': ProjectSidebar(project),
        'unfinished_task_list': gitlab_project.get_unfinished_task_list(include_groups=True),
        'finished_task_list': gitlab_project.get_finished_task_list(include_groups=True),
        'new_project_links': new_project_links,
    }
    return render(request, 'projects/tasks.html', context)


@login_required
def new_task_group(request, project_id=None, task_id=None):
    parent_task = get_object_or_404(models.AddProject, id=task_id) if task_id else None
    form = forms.TaskGroupForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Task Group',
        "fields_title": 'Add Task Group',
    }
    try:
        model = form.save(project_id=project_id, parent_task=parent_task)
    except FormNotValidError:
        return render(request, 'projects/form_base_site.html', context)
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
        return render(request, 'projects/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def edit_project_task(request, task_id):
    return HttpResponseRedirect(reverse('groups:edit_project_task', kwargs={'task_id': task_id}))


@login_required
def new_member(request, project_id):
    form = forms.AddMemberForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'New Group Member',
        "fields_title": 'New Group Member',
    }
    try:
        form.save_in_gitlab(user_id=request.user.id, project_id=project_id)
    except FormNotValidError:
        return render(request, 'projects/form_base_site.html', context)
    else:
        return HttpResponseRedirect(reverse('projects:members', args=(project_id,)))


@login_required
def new_member_task(request, project_id=None, task_group_id=None, task_id=None):
    task_group = get_object_or_404(models.TaskGroup, id=task_group_id) if task_group_id else None
    parent_task = get_object_or_404(models.AddProject, id=task_id) if task_id else None
    form = forms.AddMemberForm(request.POST or None)
    context = {
        "form": form,
        "page_title": 'Add Member Task',
        "fields_title": 'Add Member Task',
    }
    try:
        model = form.save(user_id=request.user.id, project_id=project_id, task_group=task_group,
                          parent_task=parent_task)
    except FormNotValidError:
        return render(request, 'projects/form_base_site.html', context)
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
        return render(request, 'projects/form_base_site.html', context)
    else:
        return HttpResponseRedirect(model.tasks_page_url)


@login_required
def future_project_detail(request, task_id):
    task = get_object_or_404(models.AddProject, id=task_id)
    context = {
        'task': task,
        'sidebar': FutureProjectSidebar(task),
    }
    return render(request, 'projects/tasks/detail.html', context)


@login_required
def future_project_members(request, task_id):
    task = get_object_or_404(models.AddProject, id=task_id)
    gitlab_project = task.new_gitlab_project
    context = {
        'task': task,
        'sidebar': FutureProjectSidebar(task),
        'unfinished_task_list': gitlab_project.get_unfinished_task_list(model=models.AddMember),
    }
    return render(request, 'projects/tasks/members.html', context)


@login_required
def future_project_tasks(request, task_id):
    task = get_object_or_404(models.AddProject, id=task_id)
    gitlab_project = task.new_gitlab_project
    new_project_links = [
        ('New Task Group', reverse('projects:new_task_group', kwargs={'task_id': task_id})),
        ('New Member', reverse('projects:new_member_task', kwargs={'task_id': task_id}))
    ]
    context = {
        'task': task,
        'sidebar': FutureProjectSidebar(task),
        'unfinished_task_list': gitlab_project.get_unfinished_task_list(include_groups=True),
        'finished_task_list': gitlab_project.get_finished_task_list(include_groups=True),
        'new_project_links': new_project_links,
    }
    return render(request, 'projects/tasks/tasks.html', context)
