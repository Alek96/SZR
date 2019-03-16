# Generated by Django 2.1.7 on 2019-03-16 09:23

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('django_celery_beat', '0006_periodictask_priority'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddGroupMemberTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('execute_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('finished_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.PositiveIntegerField(choices=[(0, 'Created'), (1, 'Running'), (2, 'Completed'), (3, 'Failed')], default=0)),
                ('username', models.CharField(max_length=100)),
                ('celery_task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_celery_beat.PeriodicTask')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AddGroupMemberTaskGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('execute_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('finished_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.PositiveIntegerField(choices=[(0, 'Created'), (1, 'Running'), (2, 'Completed'), (3, 'Failed')], default=0)),
                ('tasks_number', models.PositiveIntegerField(default=0)),
                ('finished_tasks_number', models.PositiveIntegerField(default=0)),
                ('failed_task_number', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
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
        migrations.AddField(
            model_name='addgroupmembertask',
            name='gitlab_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.GitlabGroup'),
        ),
        migrations.AddField(
            model_name='addgroupmembertask',
            name='new_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.GitlabUser'),
        ),
        migrations.AddField(
            model_name='addgroupmembertask',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_tasks_addgroupmembertask', to='core.GitlabUser'),
        ),
        migrations.AddField(
            model_name='addgroupmembertask',
            name='task_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks_set', to='groups.AddGroupMemberTaskGroup'),
        ),
    ]
