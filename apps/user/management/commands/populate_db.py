import random

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.utils.factory import UserFactory, NoteFactory, AdminFactory, Note, User


class Command(BaseCommand):
    help = 'Populate database with demo data'

    def add_arguments(self, parser):
        parser.add_argument('--uc', type=int, help="user count", nargs="?", default=9)
        parser.add_argument('--nc', type=int, help="note count", nargs="?", default=100)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Project is in Production mode. Turn on DEBUG to use this command")

        try:
            User.objects.all().delete()
            Note.objects.all().delete()

            user = AdminFactory.create(first_name='Admin',
                                       last_name='User',
                                       email='admin@email.com',
                                       password='Password123')
            users = UserFactory.create_batch(size=options['uc'])
            users.append(user)

            for _ in range(options['nc']):
                rd_value = random.randint(1, 8)
                note: Note = NoteFactory.create(owner=random.choice(users))
                random.shuffle(users)
                note.collaborator.set(users[:random.randint(1, 3)])
                note.save()
        except Exception as e:
            raise CommandError(e)
