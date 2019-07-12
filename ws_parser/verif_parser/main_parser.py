from typing import List
import csv
from requests_html import HTMLSession

from verif_parser.models import Company, Director

find_company_url = "https://www.verif.com/recherche/{}/1/ca/d/?ville=null"
session = HTMLSession()

COMPANY_URL = "https://www.verif.com/societe/"
COMPANY_NAME_SELECTOR = """table[class='table infoGen hidden-smallDevice'] tr:nth-child(1) > td:nth-child(2)"""
COMPANY_ADDRESS_SELECTOR1 = """span[itemprop='postalCode']"""
COMPANY_ADDRESS_SELECTOR2 = """span[itemprop='addressLocality']"""
COMPANY_OFFICERS_SELECTOR = """//*[@id="fiche_entreprise"]/div[4]/div[2]/table[2]"""

MAN_NAME_SELECTOR = """//*[@id="verif_main"]/div[2]/h1"""
MAN_DATE_OF_BIRTH_SELECTOR = """//*[@id="verif_main"]/div[2]/div[3]/p[1]/text()[1]"""
MAN_COMPANIES_SELECTOR1 = """//*[@id="verif_main"]/div[2]/div[5]"""


def load_data() -> List[int]:
    """Get sirens from csv file"""
    sirens = []
    with open("verif_parser/companies.csv") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                sirens.append(row["siren"])
            except:
                pass
    return sirens


def parse_all(sirens, nworker=1):
    """Parse all companies"""
    for siren in sirens:
        page = session.get(find_company_url.format(siren))
        res = CompanyParser(page, siren).parse()
        if res is not None:
            print(f"{nworker} : + Company {siren} parsed successfully - {str(res)}")
        else:
            print(
                f"{nworker} : - Company {siren} failed to parse (maybe company does not exists on site)"
            )


class DirectorParser:

    def __init__(self, page):
        self.page = page

    def get_name(self):
        return self.page.html.xpath(MAN_NAME_SELECTOR)[0].text.lower()

    def get_date_of_birth(self):
        date_of_birth = self.page.html.xpath(MAN_DATE_OF_BIRTH_SELECTOR)[0].lower()
        name = self.get_name()
        dot = [i for i in range(len(date_of_birth)) if date_of_birth[i] == "."][0]
        date_of_birth = date_of_birth[len(name) + len(" est né le  "): dot]
        return date_of_birth

    def get_companies(self):
        html_comps = self.page.html.xpath(MAN_COMPANIES_SELECTOR1)[0]
        companies = []
        for company_url in html_comps.absolute_links:
            if COMPANY_URL in company_url:
                dot = [i for i in range(len(company_url)) if company_url[i] == "-"][-1]
                siren = int(company_url[dot + 1: -1])
                comp = Company.objects.filter(siren=siren)
                if not comp.exists():
                    page = session.get(company_url)
                    comp = CompanyParser(page, siren).parse()
                else:
                    comp = comp[0]
                if comp is not None:
                    companies.append(comp)
        return companies

    def parse(self):
        cur = None
        try:
            name = self.get_name()
            date_of_birth = self.get_date_of_birth()
            cur, created = Director.objects.get_or_create(name=name, date_of_birth=date_of_birth)
            if not created:
                return cur
            companies = self.get_companies()
            [cur.companies.add(company) for company in companies]
            cur.save()
        except Exception as e:
            pass
        return cur


class CompanyParser:

    def __init__(self, page, siren):
        self.page = page
        self.siren = siren

    def get_name(self):
        return self.page.html.find(COMPANY_NAME_SELECTOR)[0].text.lower()

    def get_company_address(self):
        company_address1 = self.page.html.find(COMPANY_ADDRESS_SELECTOR1)[0].text.lower()
        company_address2 = self.page.html.find(COMPANY_ADDRESS_SELECTOR2)[0].text.lower()
        return company_address1 + " " + company_address2

    def get_directors(self):
        company_officers = self.page.html.xpath(COMPANY_OFFICERS_SELECTOR)
        directors = []
        if len(company_officers) > 0:
            # parse directors only where there is link to his information
            company_officers = company_officers[0].absolute_links
        for worker_url in company_officers:
            page = session.get(worker_url)
            director = DirectorParser(page).parse()
            if director is not None:
                directors.append(director)
        return directors

    def parse(self):
        cur = None
        try:
            company_name = self.get_name()
            company_address = self.get_company_address()
            cur, created = Company.objects.get_or_create(
                name=company_name,
                address=company_address,
                siren=self.siren,
            )
            if not created:  # company
                return cur
            directors = self.get_directors()
            [cur.directors.add(director) for director in directors]
            cur.save()
        except Exception as e:
            pass
        return cur
