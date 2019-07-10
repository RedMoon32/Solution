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
        res = parse_company(page, siren)
        if res is not None:
            print(f"{nworker} : + Company {siren} parsed successfully - {str(res)}")
        else:
            print(
                f"{nworker} : - Company {siren} failed to parse (maybe company does not exists on site)"
            )


def parse_company(page, siren) -> Company:
    print('Parsing {siren} ...')
    """Parse company page"""
    try:
        company_name = page.html.find(COMPANY_NAME_SELECTOR)[0].text.lower()
        cur = Company.objects.filter(name=company_name)
        if cur.exists():
            return cur[0]
        company_address1 = page.html.find(COMPANY_ADDRESS_SELECTOR1)[0].text.lower()
        company_address2 = page.html.find(COMPANY_ADDRESS_SELECTOR2)[0].text.lower()

        cur = Company.objects.get_or_create(
            name=company_name, address=company_address1 + " " + company_address2, siren=siren
        )[0]
        company_officers = page.html.xpath(COMPANY_OFFICERS_SELECTOR)
        if len(company_officers) > 0:
            # parse directors only where there is link to his information
            company_officers = company_officers[0].absolute_links
        for worker_url in company_officers:
            page = session.get(worker_url)
            director = parse_director(page)
            if director is not None:
                cur.directors.add(director)
        cur.save()
        return cur
    except Exception as e:
        return None


def parse_director(page) -> Director:
    """Parse Director page"""
    try:
        name = page.html.xpath(MAN_NAME_SELECTOR)[0].text.lower()
        date_of_birth = page.html.xpath(MAN_DATE_OF_BIRTH_SELECTOR)[0].lower()
        cur = Director.objects.filter(name=name, date_of_birth=date_of_birth)
        dot = [i for i in range(len(date_of_birth)) if date_of_birth[i] == "."][0]
        date_of_birth = date_of_birth[len(name) + len(" est né le  "): dot]
        if cur.exists():
            return cur
        cur = Director.objects.get_or_create(name=name, date_of_birth=date_of_birth)[0]
        html_comps = page.html.xpath(MAN_COMPANIES_SELECTOR1)[0]
        for company_url in html_comps.absolute_links:
            if COMPANY_URL in company_url:
                dot = [i for i in range(len(company_url)) if company_url[i] == '-'][-1]
                siren = int(company_url[dot + 1:-1])
                comp = Company.objects.filter(siren=siren)
                if not comp.exists():
                    page = session.get(company_url)
                    comp = parse_company(page, siren)
                else:
                    comp = comp[0]
                cur.companies.add(comp)
        cur.save()
        return cur
    except Exception as e:
        return None
