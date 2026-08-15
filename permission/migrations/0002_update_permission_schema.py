# Generated manually for Permission model update

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
        ('module', '0001_initial'),
        ('permission', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='permission',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='permission',
            name='resource',
        ),
        migrations.AddField(
            model_name='permission',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='company.company'),
        ),
        migrations.AddField(
            model_name='permission',
            name='module',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='module.module'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permission',
            name='display_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permission',
            name='code',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='permission',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='permission',
            name='action',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='permission',
            unique_together={('module', 'code')},
        ),
    ]
