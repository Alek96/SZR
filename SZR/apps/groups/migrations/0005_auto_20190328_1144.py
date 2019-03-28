# Generated by Django 2.1.7 on 2019-03-28 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_auto_20190319_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addgroupmembertask',
            name='status',
            field=models.PositiveIntegerField(choices=[(4, 'Waiting'), (0, 'Ready'), (1, 'Running'), (2, 'Succeed'), (3, 'Failed')], default=0),
        ),
        migrations.AlterField(
            model_name='addgroupmembertaskgroup',
            name='status',
            field=models.PositiveIntegerField(choices=[(4, 'Waiting'), (0, 'Ready'), (1, 'Running'), (2, 'Succeed'), (3, 'Failed')], default=0),
        ),
    ]
