# Generated by Django 5.0.1 on 2024-05-02 22:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "professors_projects",
            "0002_remove_professor_department_remove_professor_name_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="is_available",
            field=models.BooleanField(default=True),
        ),
    ]
