from django.core.management.base import BaseCommand

from django_comments.models import Comment


class Command(BaseCommand):
    help = ("Remove comments for which the related objects "
            "don't exist anymore!")

    def add_arguments(self, parser):
        parser.add_argument(
            '-y', '--yes', default='x', action='store_const', const='y',
            dest='answer', help='Automatically confirm deletion',
        )

    def handle(self, *args, **kwargs):
        verbose = kwargs['verbosity'] >= 1
        answer = kwargs['answer']

        # -v0 sets --yes
        if not verbose:
            answer = 'y'

        for comment in Comment.objects.all():
            if comment.content_object is None:
                if verbose:
                    self.stdout.write(
                        "Comment `%s' to non-existing `%s' with PK `%s'" %
                        (comment, comment.content_type.model, comment.object_pk))

                while answer not in 'yn':
                    answer = input("Do you wish to delete? [yN] ")
                    if not answer:
                        answer = 'x'
                        continue
                    answer = answer[0].lower()

                if answer == 'y' :
                    comment.delete()

                    if verbose:
                        self.stdout.write("Deleted comment `%s'" % comment)
