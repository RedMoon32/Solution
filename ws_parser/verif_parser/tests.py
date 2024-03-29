from django.test import TestCase

# Create your tests here.
from verif_parser.main_parser import session, CompanyParser
from verif_parser.models import Director, Company


class TestParser(TestCase):
    def test_parse1(self):
        data = session.get("https://www.verif.com/societe/ACME-807755319/")
        comp = CompanyParser(data, 807755319).parse()
        self.assertEqual(comp.name, "acme")
        self.assertEqual(comp.address, "75010 paris 10")
        self.assertEqual(comp.directors.count(), 2)
        self.assertEqual(comp.siren, 807755319)
        self.assertEqual(comp.directors.filter(name="Camille TORRE".lower()).count(), 1)
        self.assertEqual(
            comp.directors.filter(name="Benjamin BELLECOUR".lower()).count(), 1
        )
        self.assertEqual(
            Director.objects.get(name="Camille TORRE".lower()).companies.count(), 2
        )
        self.assertEqual(
            Director.objects.get(name="Camille TORRE".lower()).date_of_birth,
            "4 avril 1981",
        )
        self.assertEqual(Company.objects.get(name="entre 2&4").siren, 814577516)

    def test_parse2(self):
        data = session.get("https://www.verif.com/societe/JANOYER-THIERRY-325175/")
        comp =CompanyParser(data, 0).parse()
        self.assertEqual(comp.name, 'janoyer thierry')
        self.assertEqual(comp.directors.count(), 1)
