__author__ = 'mnowotka'

from django.core.management.base import BaseCommand

#-----------------------------------------------------------------------------------------------------------------------

class Command(BaseCommand):

#-----------------------------------------------------------------------------------------------------------------------

    def handle(self, *args, **options):
        raise NotImplementedError # TODO: implement

#-----------------------------------------------------------------------------------------------------------------------