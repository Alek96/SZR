# Generated by Django 2.1.7 on 2019-05-06 05:55

import GitLabApi.objects
import core.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_celery_beat', '0006_periodictask_priority'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_level', models.IntegerField(choices=[(10, 'Guest'), (20, 'Reporter'), (30, 'Developer'), (40, 'Master'), (50, 'Owner')], default=10)),
                ('create_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('execute_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('finished_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.PositiveIntegerField(choices=[(4, 'Waiting'), (0, 'Ready'), (1, 'Running'), (2, 'Succeed'), (3, 'Failed')], default=0)),
                ('error_msg', models.CharField(blank=True, max_length=2000, null=True)),
                ('username', models.CharField(max_length=100)),
                ('celery_task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='django_celery_beat.PeriodicTask')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, core.models.StatusMethods, core.models.ModelUrlsMethods, GitLabApi.objects.AccessLevel),
        ),
        migrations.CreateModel(
            name='AddProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibility', models.CharField(choices=[('private', 'Private'), ('internal', 'Internal'), ('public', 'Public')], default='private', max_length=10)),
                ('create_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('execute_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('finished_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.PositiveIntegerField(choices=[(4, 'Waiting'), (0, 'Ready'), (1, 'Running'), (2, 'Succeed'), (3, 'Failed')], default=0)),
                ('error_msg', models.CharField(blank=True, max_length=2000, null=True)),
                ('create_type', models.CharField(choices=[('blank', 'Blank'), ('fork', 'Fork'), ('copy', 'Copy')], default='blank', max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('path', models.SlugField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=2000, null=True)),
                ('import_url', models.URLField(blank=True, null=True)),
                ('celery_task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='django_celery_beat.PeriodicTask')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, core.models.StatusMethods, core.models.ModelUrlsMethods, GitLabApi.objects.VisibilityLevel),
        ),
        migrations.CreateModel(
            name='AddSubgroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibility', models.CharField(choices=[('private', 'Private'), ('internal', 'Internal'), ('public', 'Public')], default='private', max_length=10)),
                ('create_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('execute_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('finished_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.PositiveIntegerField(choices=[(4, 'Waiting'), (0, 'Ready'), (1, 'Running'), (2, 'Succeed'), (3, 'Failed')], default=0)),
                ('error_msg', models.CharField(blank=True, max_length=2000, null=True)),
                ('name', models.CharField(max_length=100)),
                ('path', models.SlugField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=2000, null=True)),
                ('celery_task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='django_celery_beat.PeriodicTask')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, core.models.StatusMethods, core.models.ModelUrlsMethods, GitLabApi.objects.VisibilityLevel),
        ),
        migrations.CreateModel(
            name='GitlabGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gitlab_id', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('gitlab_web_url', models.URLField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GitlabProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gitlab_id', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('gitlab_web_url', models.URLField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaskGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('execute_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('finished_date', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=2000)),
                ('gitlab_group', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='groups.GitlabGroup')),
                ('parent_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_group_task_set_groups_taskgroup', to='groups.AddSubgroup')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, core.models.StatusMethods, core.models.ModelUrlsMethods),
        ),
        migrations.AddField(
            model_name='addsubgroup',
            name='gitlab_group',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='groups.GitlabGroup'),
        ),
        migrations.AddField(
            model_name='addsubgroup',
            name='new_gitlab_group',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_creator', to='groups.GitlabGroup'),
        ),
        migrations.AddField(
            model_name='addsubgroup',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_tasks_groups_addsubgroup', to='core.GitlabUser'),
        ),
        migrations.AddField(
            model_name='addsubgroup',
            name='parent_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_task_set_groups_addsubgroup', to='groups.AddSubgroup'),
        ),
        migrations.AddField(
            model_name='addsubgroup',
            name='task_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_set_groups_addsubgroup', to='groups.TaskGroup'),
        ),
        migrations.AddField(
            model_name='addproject',
            name='gitlab_group',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='groups.GitlabGroup'),
        ),
        migrations.AddField(
            model_name='addproject',
            name='new_gitlab_project',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='groups.GitlabProject'),
        ),
        migrations.AddField(
            model_name='addproject',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_tasks_groups_addproject', to='core.GitlabUser'),
        ),
        migrations.AddField(
            model_name='addproject',
            name='parent_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_task_set_groups_addproject', to='groups.AddSubgroup'),
        ),
        migrations.AddField(
            model_name='addproject',
            name='task_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_set_groups_addproject', to='groups.TaskGroup'),
        ),
        migrations.AddField(
            model_name='addmember',
            name='gitlab_group',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='groups.GitlabGroup'),
        ),
        migrations.AddField(
            model_name='addmember',
            name='new_gitlab_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.GitlabUser'),
        ),
        migrations.AddField(
            model_name='addmember',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_tasks_groups_addmember', to='core.GitlabUser'),
        ),
        migrations.AddField(
            model_name='addmember',
            name='parent_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_task_set_groups_addmember', to='groups.AddSubgroup'),
        ),
        migrations.AddField(
            model_name='addmember',
            name='task_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_set_groups_addmember', to='groups.TaskGroup'),
        ),
    ]
