import csv
import pandas as pd
import pycountry

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scholarly import scholarly, ProxyGenerator


COUNTRY_NAME = 'Canada'
NUM_RESULTS = 50
CSV_FILE_PATH = './university_data.csv'
CSV_HEADER = ['GUID', 'Name', 'Research Interests', 'University', 'University Field', 'Num Citations']


def initialize_csv_writer(path):
    csv_file = open(path, mode='w', newline='', encoding='utf-8')
    writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    writer.writerow(CSV_HEADER)
    return writer, csv_file


def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # proxy = "23.23.23.23:3128"
    # chrome_options.add_argument('--proxy-server=%s' % proxy)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_top_universities_of(country, topn, driver):
    country_abbr = pycountry.countries.get(name=country).alpha_3  # get abbreviation
    url = f'https://timeshighereducation.com/impactrankings#!/length/{topn}' \
          f'/locations/{country_abbr}/sort_by/rank/sort_order/asc'
    driver.get(url=url)

    # wait for the table to be present in the DOM
    table_present = EC.presence_of_element_located((By.CSS_SELECTOR, '#datatable-1'))
    table_element = WebDriverWait(driver, timeout=10).until(table_present)
    rows = table_element.find_elements(By.CSS_SELECTOR, value='tbody tr')

    universities = list()
    for row in rows:
        name_element = row.find_element(By.CSS_SELECTOR, value='td.name.namesearch a')
        univ_name = name_element.get_attribute(name='textContent')
        universities.append(univ_name)

    driver.quit()  # close web driver
    return universities


def initialize_scholarly_proxy():
    pg = ProxyGenerator()
    pg.FreeProxies(timeout=1, wait_time=120)
    scholarly.use_proxy(proxy_generator=pg, secondary_proxy_generator=pg)


def main():
    driver = initialize_driver()
    universities = get_top_universities_of(country=COUNTRY_NAME, topn=NUM_RESULTS, driver=driver)
    print(universities)
    initialize_scholarly_proxy()
    univ_id = scholarly.search_org(name=universities[0])[0]['id']
    univ_researchers = scholarly.search_author_by_organization(organization_id=int(univ_id))
    print(f'{universities[0]} has an ID of {univ_id}')

    writer, csv_file = initialize_csv_writer(path=CSV_FILE_PATH)

    idx = 0
    for researcher in univ_researchers:
        idx += 1
        if idx == 30: break
        if researcher['interests']:
            guid = researcher['scholar_id']
            name = researcher['name']
            # affiliation = researcher['affiliation']
            research_interests = researcher['interests']
            num_citations = researcher['citedby']

            writer.writerow([guid, name, research_interests, universities[0], None, num_citations])

    csv_file.close()


if __name__ == '__main__':
    main()
