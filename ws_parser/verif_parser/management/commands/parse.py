from django.core.management.base import BaseCommand
from verif_parser.main_parser import parse_all, load_data
from multiprocessing import Process

from verif_parser.models import Director, Company


class Command(BaseCommand):
    help = "Parse Verif.com for companies and directors"

    def handle(self, *args, **options):
        print("Flushing DB ...")
        Director.objects.all().delete()
        Company.objects.all().delete()
        print("Parsing ...")
        data = load_data()
        dcount = len(data)
        number_of_processes = 4
        last = 0
        prs = []
        for i in range(1, number_of_processes + 1):
            p = Process(
                target=parse_all,
                args=(data[last : dcount // number_of_processes * i], i),
            )
            last = dcount // number_of_processes * i
            p.start()
            prs.append(p)
        [p.join() for p in prs]
        self.stdout.write("Parsing completed!")
