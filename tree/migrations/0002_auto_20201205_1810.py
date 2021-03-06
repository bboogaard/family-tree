# Generated by Django 3.1.1 on 2020-12-05 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ancestor',
            name='father',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(gender='m'), null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_of_father', to='tree.ancestor', verbose_name='Vader'),
        ),
        migrations.AlterField(
            model_name='ancestor',
            name='mother',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(gender='f'), null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_of_mother', to='tree.ancestor', verbose_name='Moeder'),
        ),
    ]
