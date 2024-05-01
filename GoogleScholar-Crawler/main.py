import csv
import pycountry
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scholarly import scholarly, ProxyGenerator


CSV_FILE_PATH = './university_data.csv'
CSV_HEADER = ['GUID', 'Name', 'Research Interests', 'University', 'Num Citations']
COUNTRY_NAME = 'Canada'
NUM_RESULTS = 20  # top ranked universities to crawl
NUM_RESEARCHERS = 2000  # top cited researchers to crawl
PROXY_IP = '23.23.23.23:3128'  # proxy ip for selenium driver

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO)
scholarly.logger.setLevel(level='CRITICAL')  # prevent scholarly logger from info logs
logging.getLogger('httpx').setLevel(logging.CRITICAL)  # scholarly shifted from requests to httpx


def initialize_csv_writer(path):
    csv_file = open(path, mode='a+', newline='', encoding='utf-8-sig')  # encoding must handle special chars
    writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    writer.writerow(CSV_HEADER)
    return writer, csv_file


def initialize_driver(use_proxy=False, proxy_ip=PROXY_IP):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if use_proxy:
        chrome_options.add_argument('--proxy-server=%s' % proxy_ip)
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

    universities = []
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
    driver = initialize_driver(use_proxy=False)
    logging.info('finding top %d universities in %s', NUM_RESULTS, COUNTRY_NAME)
    universities = get_top_universities_of(country=COUNTRY_NAME, topn=NUM_RESULTS, driver=driver)

    logging.info(universities)
    initialize_scholarly_proxy()
    writer, csv_file = initialize_csv_writer(path=CSV_FILE_PATH)

    for university in universities:
        univ_id = scholarly.search_org(name=university)[0]['id']
        logging.info('%s has an ID of %s', university, univ_id)
        univ_researchers = scholarly.search_author_by_organization(organization_id=int(univ_id))
        logging.info('university researchers found ...')

        counter = 0
        for researcher in univ_researchers:
            if counter == NUM_RESEARCHERS: break
            if researcher['interests']:
                counter += 1
                guid = researcher['scholar_id']
                name = researcher['name']
                # affiliation = researcher['affiliation']
                research_interests = ', '.join(researcher['interests'])
                num_citations = researcher['citedby'] if 'citedby' in researcher else 0
                writer.writerow([guid, name, research_interests, university, num_citations])

        logging.info('top %d researchers from %s dumped into csv file', counter, university)
    csv_file.close()


if __name__ == '__main__':
    main()
