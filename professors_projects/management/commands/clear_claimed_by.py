from django.core.management.base import BaseCommand
from your_app.models import Project

class Command(BaseCommand):
    help = 'Clear the claimed_by field for a specific project'

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=int, help='The ID of the project to clear claimed_by for')

    def handle(self, *args, **kwargs):
        project_id = kwargs['project_id']
        try:
            project = Project.objects.get(pk=project_id)
            project.claimed_by.clear()
            self.stdout.write(self.style.SUCCESS(f'Successfully cleared claimed_by for project {project_id}'))
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project with ID {project_id} does not exist'))
